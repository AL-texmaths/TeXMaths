@echo off

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" %*
) else (
    "..\..\Programmes\Python\python.exe" %*
)
