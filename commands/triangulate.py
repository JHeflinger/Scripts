"""
author: Jason Heflinger
description: Trianglulates OBJ files so they only contain faces of 3-4 vertices
"""

import sys

def triangulate_face(face_tokens):
    triangles = []
    v0 = face_tokens[1]
    for i in range(2, len(face_tokens) - 1):
        tri = ['f', v0, face_tokens[i], face_tokens[i + 1]]
        triangles.append(tri)
    return triangles


def process_obj(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            stripped = line.strip()
            if stripped.startswith('f '):
                tokens = stripped.split()
                if len(tokens) > 4:
                    triangles = triangulate_face(tokens)
                    for tri in triangles:
                        outfile.write(' '.join(tri) + '\n')
                else:
                    outfile.write(line)
            else:
                outfile.write(line)

if len(sys.argv) != 3:
    print("Usage: python triangulate_obj.py input.obj output.obj")
    sys.exit(1)
input_file = sys.argv[1]
output_file = sys.argv[2]
process_obj(input_file, output_file)
