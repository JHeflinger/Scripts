"""
author: Jason Heflinger
description: cleans the scripting cache
"""

import os
import shutil

if __name__ == "__main__":
    print("Cleaning script cache...")
    for filename in os.listdir(".scache"):
        path = os.path.join(".scache", filename)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    print("Finished cleaning script cache!")
    
