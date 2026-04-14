"""
author: Jason Heflinger
description: Extracts a navmesh from a given obj
"""

import sys
import math

def parse_obj(path):
    vertices = []
    faces = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith("v "):
                _, x, y, z = line.strip().split()
                vertices.append((float(x), float(y), float(z)))
            elif line.startswith("f "):
                parts = line.strip().split()[1:]
                face = []
                for p in parts:
                    idx = int(p.split("/")[0]) - 1
                    face.append(idx)
                if len(face) == 3:
                    faces.append(tuple(face))
                elif len(face) > 3:
                    for i in range(1, len(face) - 1):
                        faces.append((face[0], face[i], face[i+1]))
    return vertices, faces


def vec_sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def length(v):
    return math.sqrt(dot(v, v))

def normalize(v):
    l = length(v)
    if l == 0:
        return (0,0,0)
    return (v[0]/l, v[1]/l, v[2]/l)

def triangle_normal(v0, v1, v2):
    e1 = vec_sub(v1, v0)
    e2 = vec_sub(v2, v0)
    return normalize(cross(e1, e2))

def generate_navmesh(vertices, faces, max_slope_degrees=45):
    up = (0,1,0)
    cos_limit = math.cos(math.radians(max_slope_degrees))
    nav_faces = []
    for f in faces:
        v0, v1, v2 = vertices[f[0]], vertices[f[1]], vertices[f[2]]
        n = triangle_normal(v0, v1, v2)
        slope = dot(n, up)
        if slope >= cos_limit:
            nav_faces.append(f)
    return nav_faces

def write_obj(path, vertices, faces):
    with open(path, "w") as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

if len(sys.argv) < 3:
    print("Usage: python navmesh.py input.obj output.obj [max_slope_deg]")
    sys.exit(1)
inp = sys.argv[1]
out = sys.argv[2]
slope = float(sys.argv[3]) if len(sys.argv) > 3 else 45
vertices, faces = parse_obj(inp)
nav_faces = generate_navmesh(vertices, faces, slope)
write_obj(out, vertices, nav_faces)
print(f"Original triangles: {len(faces)}")
print(f"Navmesh triangles: {len(nav_faces)}")
