"""
author: Jason Heflinger
description: Given a command, it will print out it's description
"""

import sys
import re
import os

if len(sys.argv) != 2:
    print("Please provide a command to describe")
    exit(0)

if not os.path.isfile(f".scache/{sys.argv[1]}.py"):
    print("This command does not exist on disk. Please download it to see the description.")
    exit(0)

with open(f".scache/{sys.argv[1]}.py", "r") as file:
    content = file.read()
    breakit = content.split("\"\"\"")
    print(breakit[0])
    if len(breakit) < 2:
        print("A description does not exist for this command")
        exit(0)
    print(breakit[1])
