@echo off
REM Launcher for Railway and Vercel authentication
REM Automatically uses PowerShell 7 if available

echo Launching authentication script...
echo.

REM Check for PowerShell 7+ (pwsh.exe)
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Using PowerShell 7+...
    pwsh.exe -ExecutionPolicy Bypass -File "%~dp0login-and-link.ps1"
) else (
    echo Using Windows PowerShell 5.1...
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0login-and-link.ps1"
)
