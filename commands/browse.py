"""
author: Jason Heflinger
description: Displays local and remote possible commands
"""

import os
import requests

print("\nLocal commands:")
local = set()
for entry in os.listdir(".scache"):
    full_path = os.path.join(".scache", entry)
    if os.path.isfile(full_path):
        print(f"  - {entry[:-3]}")
        local.add(entry[:-3])

print("\nWould you like to see remote commands? (y/n)")
response = ""
while True:
    response = input("> ")
    if (response.lower() == "y" or response.lower() == "n"):
        response = response.lower()
        break
    else:
        print(f"Invalid response \"{response}\" detected. Please enter either \"y\" or \"n\".")
if (response == "y"):
    print("\nGetting remote commands...")
    api_url = f"https://api.github.com/repos/JHeflinger/Scripts/contents/commands?ref=main"
    response = requests.get(api_url)
    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file['type'] == 'file':
                name = file['name'][:-3]
                if name not in local:
                    print(f"  - {name}")
        print("")
    else:
        print("Failed to read remote commands")
else:
    print("Ok.")
