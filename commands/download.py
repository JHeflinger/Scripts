"""
author: Jason Heflinger
description: Downloads a command
"""

import sys
import urllib.request

if len(sys.argv) != 2:
    print("Please provide a command to download")
    exit(0)

try:
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/commands/{sys.argv[1]}.py", f".scache/{sys.argv[1]}.py")
except:
    print("Unable to download command. Are you sure it exists?")
