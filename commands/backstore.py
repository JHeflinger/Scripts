"""
author: Jason Heflinger
description: Given a match string, will back up all the files and pack them into a singular 
             python script that can be used to recreate the files in the same exact locations
             if needed.
"""

import sys
import pathspec
import fnmatch
from pathlib import Path
import os
import sys

if len(sys.argv) != 2:
    print("Invlid script usage. Please provide one argument.")
    exit()

with open(".gitignore", "r") as file:
    gitignore_rules = file.read().splitlines()
    spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_rules)

to_backup = []
for root, dirs, files in os.walk("."):
    for file in files:
        filepath = os.path.join(root, file)
        if not spec.match_file(filepath) and fnmatch.fnmatch(filepath, sys.argv[1]):
            parents = Path(filepath).resolve().parents
            in_sub = False
            for parent in parents:
                if parent.name == "vendor":
                    in_sub = True
            if not (not root.endswith("vendor") and in_sub):
                to_backup.append(filepath)

print("The following files will be backstored:")
for file in to_backup:
    print(f"\t{file}")
print("")
ans = input("Would you like these files to be backstored? (y/n) ")
while ans != "y" and ans != "n":
    print("Invalid input detected. Please answer either \"y\" or \"n\".")
    ans = input("Would you like these files to be backstored? (y/n) ")

if ans == "n":
    print("Canceling backstore...")
    exit()
output_script_filepath = input("What would you like the backstore file to be called? ")
output_script_filepath = "scripts/backstore/" + output_script_filepath + ".py"

def generate_recreation_script():
    global output_script_filepath
    with open(output_script_filepath, 'w') as output_script:
        output_script.write('if __name__ != "__main__":\n')
        output_script.write('    print(\"Invalid usage for this recreation script\")\n')
        output_script.write('    exit()\n')
        output_script.write('\n')

def append_recreation_script(input_filepath):
    global output_script_filepath
    with open(input_filepath, 'rb') as original_file:
        file_bytes = original_file.read()
    with open(output_script_filepath, 'a') as output_script:
        output_script.write('file_bytes = [\n')
        for i in range(0, len(file_bytes), 12):  # Splits into rows of 12 bytes for readability
            line_bytes = ', '.join(f'{byte}' for byte in file_bytes[i:i+12])
            output_script.write(f'    {line_bytes},\n')
        
        output_script.write(']\n')
        output_script.write('\n')
        output_script.write(f'with open(\"{input_filepath}\", "wb") as new_file:\n')
        output_script.write('    new_file.write(bytes(file_bytes))\n')
        output_script.write('\n')

print("Backing up files to backstore...")

generate_recreation_script()
for file in to_backup:
    append_recreation_script(file.replace("\\", "\\\\"))

print(f"Wrote backstore file to {output_script_filepath}")
print("Removing backstored files...")

for file in to_backup:
    os.remove(file)

print("Finished moving files to backstore")
