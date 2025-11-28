@echo off
REM Launcher for deployment verification script

echo Verifying deployments...
echo.

REM Check for PowerShell 7+ (pwsh.exe)
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pwsh.exe -ExecutionPolicy Bypass -File "%~dp0verify-deployment.ps1"
) else (
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0verify-deployment.ps1"
)
