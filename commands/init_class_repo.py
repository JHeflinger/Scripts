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

:: ensure build folder exists
if NOT exist \"build\" (
    echo \"Need to initialize in QT Creator\"
    exit /b 1
)

:: build
cd \"build\"
for /d %%D in (*) do (
    cd \"%%D\"
    goto :done
)
:done
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
cd \"build\"
set QTDIR=
for /d %%D in (*) do (
    set QTDIR=%%D
    goto :done
)
:done
cd ..
\"build/%QTDIR%/""")
        f.write(f"{default_exe_name}.exe\"")
    with open("clean.bat", "w") as f:
        f.write("""@echo off
if exist \"build\" (
    rmdir /s /q \"build\"
)""")
    with open("build.sh", "w") as f:
        f.write("""# ensure build folder exists
if [ ! -d \"build\" ]; then
	echo \"Need to initialize in QT Creator\"
	exit 1
fi

# build
cd build/Desktop-Debug
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
./build/Desktop-Debug/""")
        f.write(f"{default_exe_name}")
    with open("clean.sh", "w") as f:
        f.write("""if [ -d \"build\" ]; then
	rm -rf build
fi
""")
    if (os.name != "nt"):
        os.system("chmod +x build.sh")
        os.system("chmod +x run.sh")
        os.system("chmod +x clean.sh")
    print("Successfully set up build scripts!")
except:
    print("An error occured - unable to finish setup...")