@echo off
REM Railway Logs Viewer

echo Fetching Railway logs...
echo.

REM Check for PowerShell 7+ (pwsh.exe)
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pwsh.exe -ExecutionPolicy Bypass -File "%~dp0check-railway-logs.ps1"
) else (
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0check-railway-logs.ps1"
)
