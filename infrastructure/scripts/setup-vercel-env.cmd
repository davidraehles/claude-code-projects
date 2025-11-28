@echo off
REM Launcher for Vercel environment variables setup

echo Setting up Vercel environment variables...
echo.

REM Check for PowerShell 7+ (pwsh.exe)
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pwsh.exe -ExecutionPolicy Bypass -File "%~dp0setup-vercel-env.ps1"
) else (
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0setup-vercel-env.ps1"
)
