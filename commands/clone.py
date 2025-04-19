"""
author: Jason Heflinger
description: clones shell.py into the current working directory
"""

import urllib.request

if __name__ == "__main__":
    try:
        urllib.request.urlretrieve("https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/shell.py", "shell.py")
        print("Successfully cloned shell to current working directory!")
    except:
        print("Failed to clone shell into current working directory. Are you sure you are connected to the internet?")
