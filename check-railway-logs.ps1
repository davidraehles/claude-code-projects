# Railway Logs Viewer
# Displays recent Railway deployment logs for debugging

Write-Host "=== Railway Deployment Logs ===" -ForegroundColor Cyan
Write-Host ""

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
Write-Host "Fetching logs..." -ForegroundColor Yellow
Write-Host ""

# Get logs
try {
    Write-Host "Recent logs:" -ForegroundColor White
    railway logs

    Write-Host ""
    Write-Host "--- Deployment Status ---" -ForegroundColor Cyan
    railway status
} catch {
    Write-Host "Error fetching logs: $($_.Exception.Message)" -ForegroundColor Red
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
Write-Host "View specific logs:  railway logs <deployment-id>" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
