"""
author: Jason Heflinger
description: Initializes build, run, and clean scripts for class repos built with CMake
"""

print("Writing build scripts...")

import os

try:
    with open("build.bat", "w") as f:
        f.write("""@echo off
setlocal enabledelayedexpansion

set BUILD_DIR=jason_custom_build

:: ensure build folder exists
if NOT exist \"build\" (
    mkdir build
)

:: ensure subbuild folder exists
if NOT exist \"build/%BUILD_DIR%\" (
    cd build
    mkdir %BUILD_DIR%
    cd %BUILD_DIR%
    cmake ../..
    cd ..
    cd ..
)

:: build
cd \"build/%BUILD_DIR%\"
cmake --build .
cd ..
cd ..
if %ERRORLEVEL% NEQ 0 (
    exit /b %ERRORLEVEL%
)""")
    default_exe_name="bin"
    with open("CMakeLists.txt", "r") as f:
        for line in f:
            if line.strip().startswith("project("):
                default_exe_name=line.split("(")[1].split(" ")[0]
                break
    with open("run.bat", "w") as f:
        f.write("""@echo off
call build.bat
if %ERRORLEVEL% NEQ 0 (
    exit /b %ERRORLEVEL%
)
\"build/jason_custom_build/Debug/""")
        f.write(f"{default_exe_name}.exe\"")
    with open("clean.bat", "w") as f:
        f.write("""@echo off
if exist \"build/jason_custom_build\" (
    rmdir /s /q \"build\jason_custom_build\"
)""")
    with open("build.sh", "w") as f:
        f.write("""# ensure build folder exists
if [ ! -d \"build\" ]; then
	mkdir \"build\"
fi

# ensure subbuild folder exists
if [ ! -d \"build/jason_custom_build\" ]; then
    cd build
	mkdir \"jason_custom_build\"
    cd jason_custom_build
	cmake ../..
	cd ..
    cd ..
fi

# build
cd build/jason_custom_build
cmake --build .
cd ..
cd ..
if [ $? -ne 0 ]; then
	exit 1
fi""")
    with open("run.sh", "w") as f:
        f.write("""./build.sh
if [ $? -ne 0 ]; then
	exit 1
fi
./build/jason_custom_build/""")
        f.write(f"{default_exe_name}.exe")
    with open("clean.sh", "w") as f:
        f.write("""if [ -d \"build/jason_custom_build\" ]; then
    cd build
	rm -rf jason_custom_build
    cd ..
fi
""")
    if (os.name != "nt"):
        os.system("chmod +x build.sh")
        os.system("chmod +x run.sh")
        os.system("chmod +x clean.sh")
    print("Successfully set up build scripts!")
except:
    print("An error occured - unable to finish setup...")