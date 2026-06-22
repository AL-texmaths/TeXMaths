@echo off

echo Detection environnement...

:: Test proxy
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable 2^>nul') do (
    set ENABLED=%%B
)

if "%ENABLED%"=="0x1" (
    set MODE=work
)

:: Fallback : test IP
ipconfig | find "172.23." >nul
if %errorlevel%==0 (
    set MODE=work
)

:: Sinon
if not defined MODE (
    set MODE=home
)

echo Mode detecte : %MODE%