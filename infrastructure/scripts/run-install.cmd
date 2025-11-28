@echo off
REM Launcher script for install-cli-tools.ps1
REM Automatically uses PowerShell 7 if available, otherwise falls back to Windows PowerShell

echo Checking for PowerShell...

REM Check for PowerShell 7+ (pwsh.exe)
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found PowerShell 7+, using it for better performance...
    pwsh.exe -ExecutionPolicy Bypass -File "%~dp0install-cli-tools.ps1"
    goto :end
)

REM Fall back to Windows PowerShell 5.1
echo PowerShell 7 not found, using Windows PowerShell 5.1...
echo ^(Recommended: Install PowerShell 7 from https://github.com/PowerShell/PowerShell/releases^)
echo.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0install-cli-tools.ps1"

:end
pause
