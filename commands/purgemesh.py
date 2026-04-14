"""
author: Jason Heflinger
description: Purges all smaller unconnected parts of a mesh
"""

import sys
from collections import defaultdict, deque

def load_obj(path):
    vertices = []
    faces = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                vertices.append(tuple(map(float, parts[1:4])))
            elif line.startswith("f "):
                parts = line.split()[1:]
                face = [int(p.split("/")[0]) - 1 for p in parts]
                faces.append(face)
    return vertices, faces


def build_face_adjacency(faces):
    vertex_to_faces = defaultdict(list)
    for fi, face in enumerate(faces):
        for v in face:
            vertex_to_faces[v].append(fi)
    adjacency = [[] for _ in range(len(faces))]
    for face_list in vertex_to_faces.values():
        for i in face_list:
            for j in face_list:
                if i != j:
                    adjacency[i].append(j)
    return adjacency


def find_largest_component(adjacency):
    visited = set()
    largest = []
    for start in range(len(adjacency)):
        if start in visited:
            continue
        queue = deque([start])
        component = []
        while queue:
            f = queue.popleft()
            if f in visited:
                continue
            visited.add(f)
            component.append(f)
            for n in adjacency[f]:
                if n not in visited:
                    queue.append(n)
        if len(component) > len(largest):
            largest = component
    return set(largest)


def write_filtered_obj(output_path, vertices, faces, keep_faces):
    used_vertices = set()
    for fi in keep_faces:
        used_vertices.update(faces[fi])
    index_map = {}
    new_vertices = []
    for v in sorted(used_vertices):
        index_map[v] = len(new_vertices)
        new_vertices.append(vertices[v])
    with open(output_path, "w") as f:
        for v in new_vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for fi in keep_faces:
            face = faces[fi]
            new_face = [index_map[v] + 1 for v in face]
            f.write("f " + " ".join(map(str, new_face)) + "\n")

def keep_largest_island(input_obj, output_obj):
    vertices, faces = load_obj(input_obj)
    adjacency = build_face_adjacency(faces)
    largest_component = find_largest_component(adjacency)
    write_filtered_obj(output_obj, vertices, faces, largest_component)

if len(sys.argv) != 3:
    print("Usage: python purgemesh.py input.obj output.obj")
    sys.exit(1)
keep_largest_island(sys.argv[1], sys.argv[2])
