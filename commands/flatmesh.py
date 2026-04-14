"""
author: Jason Heflinger
description: Reduces a navmesh to a given y level
"""

import sys

def filter_obj_by_y(input_path, output_path, target_y, epsilon=1e-5):
    vertices = []
    faces = []
    with open(input_path, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
            elif line.startswith("f "):
                faces.append(line.strip())
    keep = [abs(v[1] - target_y) < epsilon for v in vertices]
    index_map = {}
    new_vertices = []
    new_index = 1
    for i, (v, k) in enumerate(zip(vertices, keep)):
        if k:
            index_map[i + 1] = new_index
            new_vertices.append(v)
            new_index += 1
    new_faces = []
    for face in faces:
        parts = face.split()[1:]
        indices = [int(p.split("/")[0]) for p in parts]
        if all(i in index_map for i in indices):
            new_indices = [str(index_map[i]) for i in indices]
            new_faces.append("f " + " ".join(new_indices))
    with open(output_path, "w") as f:
        for v in new_vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in new_faces:
            f.write(face + "\n")

if len(sys.argv) < 4:
    print("Usage: python flatmesh.py input.obj output.obj target_y")
    sys.exit(1)
input_path = sys.argv[1]
output_path = sys.argv[2]
target_y = float(sys.argv[3])
filter_obj_by_y(input_path, output_path, target_y)
