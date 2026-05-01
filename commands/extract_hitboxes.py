"""
OBJ to Box Colliders Converter
================================
Converts a grid-aligned maze .obj into tight box colliders, then opens
an interactive 3D visualizer.

Strategy (much better than voxelization for grid mazes):
  1. Compute each triangle's face normal and snap it to the nearest axis
     (+X -X +Y -Y +Z -Z).
  2. Group triangles by (axis, position-along-axis).  All co-planar faces
     sharing the same normal and the same plane coordinate land in one group.
  3. Within each group project the triangles to 2D, flood-fill connected
     rectangles, then merge touching rectangles with a greedy 2-D sweep.
  4. Lift each merged 2-D rectangle back to 3-D: the thin dimension becomes
     the wall thickness (minimum non-zero extent of the source triangles
     along that axis).
  Result: one box per wall segment — typically 10-100× fewer than voxels.

Usage:
    python obj_to_box_colliders.py maze.obj --output colliders.json

Arguments:
    input           Path to the .obj file
    --output        Output JSON file path (default: colliders.json)
    --thickness     Fallback wall thickness when it cannot be auto-detected
                    (default: 0.1)
    --snap          Normal-snap tolerance in degrees (default: 15)
    --no-viz        Skip the 3D visualizer window

Visualizer controls:
    Left-drag  Orbit  |  Right-drag  Pan  |  Scroll  Zoom
    W  wireframe      |  S  solid          |  G  grid
    R  reset camera   |  Q / Esc  quit

Output JSON:
    [ { "center": [x,y,z], "scale": [sx,sy,sz] }, ... ]

Dependencies:
    pip install pygame PyOpenGL PyOpenGL_accelerate
"""

import argparse
import collections
import json
import math
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# OBJ Parser
# ---------------------------------------------------------------------------

def parse_obj(path: str):
    """Return (vertices, triangles). Triangles are index triples into vertices."""
    vertices = []
    triangles = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "v":
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif parts[0] == "f":
                indices = [int(p.split("/")[0]) - 1 for p in parts[1:]]
                for i in range(1, len(indices) - 1):
                    triangles.append((indices[0], indices[i], indices[i + 1]))
    return vertices, triangles


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def tri_normal(v0, v1, v2):
    ax, ay, az = v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]
    bx, by, bz = v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]
    nx, ny, nz = ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx
    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    if length < 1e-12:
        return None
    return nx/length, ny/length, nz/length


def snap_normal(nx, ny, nz, tol_deg=15):
    """Snap a face normal to the nearest axis direction. Returns (axis, sign) or None."""
    tol = math.cos(math.radians(90 - tol_deg))   # dot-product threshold
    axes = [(1,0,0), (0,1,0), (0,0,1)]
    best_dot, best_axis, best_sign = 0, None, 1
    for i, (ax, ay, az) in enumerate(axes):
        d = nx*ax + ny*ay + nz*az
        if abs(d) > best_dot:
            best_dot, best_axis, best_sign = abs(d), i, (1 if d > 0 else -1)
    if best_dot < tol or best_axis is None:
        return None
    return best_axis, best_sign   # axis: 0=X 1=Y 2=Z


# ---------------------------------------------------------------------------
# Wall-segment collider extraction
# ---------------------------------------------------------------------------

def extract_colliders(vertices, triangles, fallback_thickness=0.1, snap_tol_deg=15):
    """
    Fast, vertex-exact approach — no rasterization grid at all.

    For each group of co-planar, axis-aligned triangles:
      1. Snap each triangle's normal to the nearest axis.
      2. Collect the actual vertex coordinates projected to 2D (u, v).
      3. Snap u/v to a coarse coordinate grid derived from the unique vertex
         positions themselves (coordinate compression) — grid cells are defined
         by the real geometry, not an arbitrary resolution.
      4. Mark only cells whose centre is inside at least one triangle.
      5. Greedy-merge the filled cells into rectangles, then lift to 3D.

    This is O(triangles × unique_u_coords × unique_v_coords) which is tiny
    for a grid maze — typically microseconds per plane.
    """

    PLANE_ROUND  = 3    # decimal places for plane-coord bucketing
    MERGE_DIST   = 0.02 # max distance to merge nearly-coplanar faces
    SNAP_DIGITS  = 4    # round vertex coords to avoid float noise

    # ── 1. Bucket triangles by (axis, plane_coord) ───────────────────────
    plane_tris = collections.defaultdict(list)  # (axis, coord) → [(v0,v1,v2)]

    for tri in triangles:
        v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
        n = tri_normal(v0, v1, v2)
        if n is None:
            continue
        snapped = snap_normal(*n, tol_deg=snap_tol_deg)
        if snapped is None:
            continue
        axis, _sign = snapped
        plane_val = round((v0[axis] + v1[axis] + v2[axis]) / 3, PLANE_ROUND)
        plane_tris[(axis, plane_val)].append((v0, v1, v2))

    # ── 2. Merge nearly-coplanar planes ──────────────────────────────────
    merged: dict = {}
    for (axis, coord), tris in plane_tris.items():
        placed = False
        for (ka, kc) in list(merged.keys()):
            if ka == axis and abs(kc - coord) < MERGE_DIST:
                merged[(ka, kc)].extend(tris)
                placed = True
                break
        if not placed:
            merged[(axis, coord)] = list(tris)

    colliders = []

    for (axis, plane_coord), tris in merged.items():
        u_ax = (axis + 1) % 3
        v_ax = (axis + 2) % 3

        # ── 3. Collect projected verts + depth extent ─────────────────────
        depth_min, depth_max = math.inf, -math.inf
        tri_pts = []   # list of ((u0,v0),(u1,v1),(u2,v2)) per triangle

        for t0, t1, t2 in tris:
            pts = []
            for v in (t0, t1, t2):
                u = round(v[u_ax], SNAP_DIGITS)
                vv = round(v[v_ax], SNAP_DIGITS)
                depth_min = min(depth_min, v[axis])
                depth_max = max(depth_max, v[axis])
                pts.append((u, vv))
            tri_pts.append(pts)

        thickness = depth_max - depth_min
        if thickness < 1e-6:
            thickness = fallback_thickness

        # ── 4. Coordinate compression ─────────────────────────────────────
        # Build sorted lists of unique u and v values from actual vertices.
        # Each pair of adjacent values defines one cell column/row.
        all_u = sorted(set(p[0] for pts in tri_pts for p in pts))
        all_v = sorted(set(p[1] for pts in tri_pts for p in pts))

        if len(all_u) < 2 or len(all_v) < 2:
            # Degenerate plane — just emit one box from the bounding box
            if all_u and all_v:
                u_mid = (all_u[0] + all_u[-1]) / 2
                v_mid = (all_v[0] + all_v[-1]) / 2
                su = all_u[-1] - all_u[0] or fallback_thickness
                sv = all_v[-1] - all_v[0] or fallback_thickness
                center = [0.0, 0.0, 0.0]
                scale  = [0.0, 0.0, 0.0]
                center[axis] = (depth_min + depth_max) / 2
                center[u_ax] = u_mid
                center[v_ax] = v_mid
                scale[axis]  = thickness
                scale[u_ax]  = su
                scale[v_ax]  = sv
                colliders.append({
                    "center": [round(x, 6) for x in center],
                    "scale":  [round(x, 6) for x in scale],
                })
            continue

        # Map coordinate value → column/row index
        u_idx = {u: i for i, u in enumerate(all_u)}
        v_idx = {v: i for i, v in enumerate(all_v)}
        nu = len(all_u) - 1   # number of cell columns
        nv = len(all_v) - 1   # number of cell rows

        # ── 5. Mark filled cells ──────────────────────────────────────────
        # A cell (cu, cv) spans [all_u[cu], all_u[cu+1]] × [all_v[cv], all_v[cv+1]].
        # Test its centre against each triangle.
        filled = set()

        for pts in tri_pts:
            (au, av), (bu, bv), (cu, cv) = pts
            # Bounding box in cell space
            col0 = max(0, min(u_idx[au], u_idx[bu], u_idx[cu]))
            col1 = min(nu - 1, max(u_idx[au], u_idx[bu], u_idx[cu]))
            row0 = max(0, min(v_idx[av], v_idx[bv], v_idx[cv]))
            row1 = min(nv - 1, max(v_idx[av], v_idx[bv], v_idx[cv]))

            for col in range(col0, col1 + 1):
                for row in range(row0, row1 + 1):
                    if (col, row) in filled:
                        continue
                    # Centre of this compressed cell in world coords
                    uc = (all_u[col] + all_u[col + 1]) / 2
                    vc = (all_v[row] + all_v[row + 1]) / 2
                    if _pt_in_tri_2d(uc, vc, au, av, bu, bv, cu, cv):
                        filled.add((col, row))

        if not filled:
            continue

        # ── 6. Greedy 2-D rectangle merge ────────────────────────────────
        remaining = set(filled)
        rects = []  # (col0, row0, col1, row1) inclusive

        while remaining:
            sc, sr = next(iter(remaining))
            ec = sc
            while (ec + 1, sr) in remaining:
                ec += 1
            er = sr
            while all((c, er + 1) in remaining for c in range(sc, ec + 1)):
                er += 1
            for c in range(sc, ec + 1):
                for r in range(sr, er + 1):
                    remaining.discard((c, r))
            rects.append((sc, sr, ec, er))

        # ── 7. Lift each rect to a 3-D box ───────────────────────────────
        depth_mid = (depth_min + depth_max) / 2

        for (sc, sr, ec, er) in rects:
            wu0 = all_u[sc]
            wu1 = all_u[ec + 1]
            wv0 = all_v[sr]
            wv1 = all_v[er + 1]

            center = [0.0, 0.0, 0.0]
            scale  = [0.0, 0.0, 0.0]
            center[axis] = depth_mid
            center[u_ax] = (wu0 + wu1) / 2
            center[v_ax] = (wv0 + wv1) / 2
            scale[axis]  = thickness
            scale[u_ax]  = wu1 - wu0
            scale[v_ax]  = wv1 - wv0

            if all(s > 1e-9 for s in scale):
                colliders.append({
                    "center": [round(x, 6) for x in center],
                    "scale":  [round(x, 6) for x in scale],
                })

    return colliders


def _pt_in_tri_2d(px, py, ax, ay, bx, by, cx, cy):
    """Return True if point (px,py) is inside or on triangle (a,b,c)."""
    d1 = (px - bx) * (ay - by) - (ax - bx) * (py - by)
    d2 = (px - cx) * (by - cy) - (bx - cx) * (py - cy)
    d3 = (px - ax) * (cy - ay) - (cx - ax) * (py - ay)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


# ---------------------------------------------------------------------------
# 3-D Visualizer  (requires: pip install pygame PyOpenGL PyOpenGL_accelerate)
# ---------------------------------------------------------------------------

def build_box_geometry(colliders):
    """
    Pre-bake solid quads and wireframe edges for all colliders into flat
    float lists for fast OpenGL drawing.
    Returns (solid_quads, wire_lines)  — each is a list of (x,y,z) tuples.
    """
    # Unit cube: 6 faces × 4 verts, normals per face
    face_normals = [
        ( 0,  0,  1), ( 0,  0, -1),
        ( 0,  1,  0), ( 0, -1,  0),
        ( 1,  0,  0), (-1,  0,  0),
    ]
    face_verts = [
        [(-1,-1, 1),( 1,-1, 1),( 1, 1, 1),(-1, 1, 1)],  # +Z
        [( 1,-1,-1),(-1,-1,-1),(-1, 1,-1),( 1, 1,-1)],  # -Z
        [(-1, 1,-1),( 1, 1,-1),( 1, 1, 1),(-1, 1, 1)],  # +Y
        [(-1,-1, 1),( 1,-1, 1),( 1,-1,-1),(-1,-1,-1)],  # -Y
        [( 1,-1, 1),( 1,-1,-1),( 1, 1,-1),( 1, 1, 1)],  # +X
        [(-1,-1,-1),(-1,-1, 1),(-1, 1, 1),(-1, 1,-1)],  # -X
    ]
    # 12 edges of a unit cube (pairs of corner indices)
    corners = [(-1,-1,-1),( 1,-1,-1),( 1, 1,-1),(-1, 1,-1),
               (-1,-1, 1),( 1,-1, 1),( 1, 1, 1),(-1, 1, 1)]
    edge_pairs = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                  (0,4),(1,5),(2,6),(3,7)]

    solid_verts = []   # (nx,ny,nz, x,y,z) per vertex
    wire_verts  = []   # (x,y,z) per vertex

    for col in colliders:
        cx, cy, cz = col["center"]
        sx, sy, sz = col["scale"]
        hx, hy, hz = sx / 2, sy / 2, sz / 2

        for face_idx, (quad, normal) in enumerate(zip(face_verts, face_normals)):
            for lx, ly, lz in quad:
                solid_verts.append((
                    normal[0], normal[1], normal[2],
                    cx + lx * hx, cy + ly * hy, cz + lz * hz
                ))

        for a, b in edge_pairs:
            ax, ay, az = corners[a]
            bx, by, bz = corners[b]
            wire_verts.append((cx + ax * hx, cy + ay * hy, cz + az * hz))
            wire_verts.append((cx + bx * hx, cy + by * hy, cz + bz * hz))

    return solid_verts, wire_verts


def show_visualizer(colliders, title="Box Collider Visualizer"):
    try:
        import pygame
        from pygame.locals import (DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE,
                                   K_q, K_w, K_s, K_g, K_r,
                                   MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
                                   K_h)
        from OpenGL.GL import (
            glEnable, glDisable, glBlendFunc, glClear, glClearColor,
            glMatrixMode, glLoadIdentity, glViewport, glLineWidth,
            glBegin, glEnd, glVertex3f, glNormal3f, glColor4f,
            glLightfv, glMaterialfv, glShadeModel,
            GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
            GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
            GL_PROJECTION, GL_MODELVIEW,
            GL_QUADS, GL_LINES,
            GL_LIGHT0, GL_LIGHTING, GL_POSITION, GL_DIFFUSE, GL_AMBIENT,
            GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, GL_SMOOTH,
        )
        from OpenGL.GLU import gluPerspective, gluLookAt
    except ImportError:
        print("\n[visualizer] Install dependencies with:")
        print("    pip install pygame PyOpenGL PyOpenGL_accelerate")
        print("[visualizer] Skipping visualizer.\n")
        return

    # ── bounding info ────────────────────────────────────────────────────
    all_x = [c["center"][0] for c in colliders]
    all_y = [c["center"][1] for c in colliders]
    all_z = [c["center"][2] for c in colliders]
    cx0 = (min(all_x) + max(all_x)) / 2
    cy0 = (min(all_y) + max(all_y)) / 2
    cz0 = (min(all_z) + max(all_z)) / 2
    span = max(
        max(all_x) - min(all_x),
        max(all_y) - min(all_y),
        max(all_z) - min(all_z),
    ) or 1.0
    floor_y = min(c["center"][1] - c["scale"][1] / 2 for c in colliders)

    # ── pre-bake geometry ─────────────────────────────────────────────────
    solid_verts, wire_verts = build_box_geometry(colliders)

    # ── pygame / GL init ─────────────────────────────────────────────────
    pygame.init()
    W, H = 1280, 720
    pygame.display.set_mode((W, H), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"{title}  |  {len(colliders)} boxes  |  W=wireframe  S=solid  G=grid  R=reset  Q=quit")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.08, 0.08, 0.10, 1.0)

    glLightfv(GL_LIGHT0, GL_POSITION, (span, span * 2, span, 0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.25, 0.25, 0.3, 1.0))

    # ── camera state ──────────────────────────────────────────────────────
    theta   = 30.0        # azimuth  (degrees)
    phi     = 25.0        # elevation (degrees)
    dist    = span * 1.8
    pan_x   = cx0
    pan_y   = cy0
    pan_z   = cz0

    # ── toggle state ──────────────────────────────────────────────────────
    show_wire  = True
    show_solid = True
    show_grid  = False
    solid_alpha = 0.40

    dragging      = False
    right_drag    = False
    last_mouse    = (0, 0)

    def set_projection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50, W / H, 0.01, span * 40)
        glMatrixMode(GL_MODELVIEW)

    def camera_pos():
        tr = math.radians(theta)
        pr = math.radians(phi)
        ex = pan_x + dist * math.cos(pr) * math.sin(tr)
        ey = pan_y + dist * math.sin(pr)
        ez = pan_z + dist * math.cos(pr) * math.cos(tr)
        return ex, ey, ez

    def draw_grid():
        glDisable(GL_LIGHTING)
        glColor4f(0.3, 0.3, 0.4, 0.6)
        glLineWidth(1.0)
        step = span / 10
        count = 20
        y = floor_y - 0.01
        glBegin(GL_LINES)
        for i in range(-count, count + 1):
            glVertex3f(i * step, y, -count * step)
            glVertex3f(i * step, y,  count * step)
            glVertex3f(-count * step, y, i * step)
            glVertex3f( count * step, y, i * step)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_solid():
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE,
                     (0.28, 0.55, 1.0, solid_alpha))
        glBegin(GL_QUADS)
        for nx, ny, nz, x, y, z in solid_verts:
            glNormal3f(nx, ny, nz)
            glVertex3f(x, y, z)
        glEnd()

    def draw_wire():
        glDisable(GL_LIGHTING)
        glColor4f(0.55, 0.80, 1.0, 0.9)
        glLineWidth(1.2)
        glBegin(GL_LINES)
        for x, y, z in wire_verts:
            glVertex3f(x, y, z)
        glEnd()
        glEnable(GL_LIGHTING)

    set_projection()
    clock = pygame.time.Clock()

    print("\n[visualizer] Window open — controls:")
    print("   Left-drag: orbit  |  Right-drag: pan  |  Scroll: zoom")
    print("   W: wireframe  S: solid  G: grid  R: reset  Q/Esc: quit\n")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_q):
                    running = False
                elif event.key == K_w:
                    show_wire = not show_wire
                elif event.key == K_s:
                    show_solid = not show_solid
                elif event.key == K_g:
                    show_grid = not show_grid
                elif event.key == K_r:
                    theta, phi, dist = 30.0, 25.0, span * 1.8
                    pan_x, pan_y, pan_z = cx0, cy0, cz0

            elif event.type == MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    dragging   = True
                    right_drag = (event.button == 3)
                    last_mouse = event.pos
                elif event.button == 4:   # scroll up → zoom in
                    dist = max(span * 0.05, dist * 0.92)
                elif event.button == 5:   # scroll down → zoom out
                    dist *= 1.09

            elif event.type == MOUSEBUTTONUP:
                if event.button in (1, 3):
                    dragging = False

            elif event.type == MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]
                last_mouse = event.pos
                if right_drag:
                    # Pan in the camera's XZ plane
                    tr = math.radians(theta)
                    speed = dist * 0.0015
                    pan_x -= dx * speed * math.cos(tr)
                    pan_z -= dx * speed * (-math.sin(tr))
                    pan_y += dy * speed
                else:
                    theta -= dx * 0.4
                    phi    = max(-89, min(89, phi - dy * 0.4))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        ex, ey, ez = camera_pos()
        gluLookAt(ex, ey, ez, pan_x, pan_y, pan_z, 0, 1, 0)

        if show_grid:
            draw_grid()
        if show_solid:
            draw_solid()
        if show_wire:
            draw_wire()

        # HUD overlay — drawn in window-corner via pygame surface blit
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert a grid-aligned maze .obj into tight box colliders."
    )
    parser.add_argument("input", help="Path to the .obj file")
    parser.add_argument(
        "--output", default="colliders.json",
        help="Output JSON file (default: colliders.json)"
    )
    parser.add_argument(
        "--thickness", type=float, default=0.1,
        help="Fallback wall thickness when it cannot be auto-detected (default: 0.1)"
    )
    parser.add_argument(
        "--snap", type=float, default=15.0,
        help="Normal snap tolerance in degrees (default: 15)"
    )
    parser.add_argument(
        "--no-viz", action="store_true",
        help="Skip the 3D visualizer window"
    )
    args = parser.parse_args()

    print(f"[1/3] Parsing OBJ: {args.input}")
    vertices, triangles = parse_obj(args.input)
    print(f"      {len(vertices)} vertices, {len(triangles)} triangles")

    print(f"[2/3] Extracting wall-segment colliders (snap={args.snap}°) ...")
    colliders = extract_colliders(
        vertices, triangles,
        fallback_thickness=args.thickness,
        snap_tol_deg=args.snap,
    )
    print(f"      {len(colliders)} box colliders")

    print(f"[3/3] Writing output ...")
    with open(args.output, "w") as f:
        json.dump(colliders, f, indent=2)

    print(f"\n✓ Written {len(colliders)} box colliders → {args.output}")
    if colliders:
        print(f"\nExample entry:\n  {json.dumps(colliders[0], indent=4)}")

    if not args.no_viz:
        show_visualizer(colliders, title=Path(args.input).stem)


if __name__ == "__main__":
    main()
