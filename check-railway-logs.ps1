# Railway Logs Viewer
# Fetches and saves Railway deployment logs for debugging

Write-Host "=== Railway Deployment Logs ===" -ForegroundColor Cyan
Write-Host ""

# Create logs directory
$logsDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "Created logs directory" -ForegroundColor Gray
}

# Generate timestamp for log file
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $logsDir "railway_logs_$timestamp.txt"

# Check if railway CLI is available
try {
    $railwayVersion = railway --version 2>&1
    Write-Host "Railway CLI: $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Railway CLI not found" -ForegroundColor Red
    Write-Host "Please run: npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Fetching logs and saving to: $logFile" -ForegroundColor Yellow
Write-Host ""

# Create header for log file
$header = @"
=== Railway Deployment Logs ===
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Railway CLI: $railwayVersion

"@

$header | Out-File -FilePath $logFile -Encoding UTF8

# Get logs and save to file
try {
    Write-Host "Fetching logs..." -ForegroundColor White

    # Capture logs
    "--- RAILWAY LOGS ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
    railway logs 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8

    Write-Host "✓ Logs saved" -ForegroundColor Green

    Write-Host ""
    Write-Host "Fetching deployment status..." -ForegroundColor White

    # Capture status
    "`n--- DEPLOYMENT STATUS ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
    railway status 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8

    Write-Host "✓ Status saved" -ForegroundColor Green

    Write-Host ""
    Write-Host "Fetching environment variables..." -ForegroundColor White

    # Capture variables
    "`n--- ENVIRONMENT VARIABLES ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
    railway variables 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8

    Write-Host "✓ Variables saved" -ForegroundColor Green

    Write-Host ""
    Write-Host "=== Log File Saved ===" -ForegroundColor Cyan
    Write-Host "Location: $logFile" -ForegroundColor White
    Write-Host ""

    # Display preview of logs
    Write-Host "--- Log Preview (last 20 lines) ---" -ForegroundColor Yellow
    Get-Content $logFile -Tail 20 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }

} catch {
    Write-Host "Error fetching logs: $($_.Exception.Message)" -ForegroundColor Red
    "ERROR: $($_.Exception.Message)" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Host ""
    Write-Host "Make sure you are logged in and linked to a project:" -ForegroundColor Yellow
    Write-Host "  railway login" -ForegroundColor White
    Write-Host "  railway link" -ForegroundColor White
}

Write-Host ""
Write-Host "--- Additional Commands ---" -ForegroundColor Cyan
Write-Host "View all logs:       railway logs" -ForegroundColor White
Write-Host "Check status:        railway status" -ForegroundColor White
Write-Host "View variables:      railway variables" -ForegroundColor White
Write-Host "View log file:       Get-Content '$logFile'" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
