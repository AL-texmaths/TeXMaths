@echo off

where code >nul 2>nul
if %errorlevel% equ 0 (
    code %*
) else (
    "..\..\Programmes\VSCode\Code.exe" %*
)
