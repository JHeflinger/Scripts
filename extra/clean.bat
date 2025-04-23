@echo off
if exist "build\cache" (
    rmdir /s /q "build\cache"
)
if exist "build\vendor" (
    rmdir /s /q "build\vendor"
)
if exist "build\bin.exe" (
    del /f /q "build\bin.exe"
)