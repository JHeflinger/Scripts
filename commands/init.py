
print("Initializing C build scripts...")

import urllib.request
import os

try:
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/build.sh", "build.sh")
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/run.sh", "run.sh")
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/clean.sh", "clean.sh")
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/build.bat", "build.bat")
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/run.bat", "run.bat")
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/JHeflinger/Scripts/refs/heads/main/extra/clean.bat", "clean.bat")
    if (os.name != "nt"):
        os.system("chmod +x build.sh")
        os.system("chmod +x run.sh")
        os.system("chmod +x clean.sh")
    print("Successfully set up build scripts!")
except:
    print("An error occured - unable to finish setup...")