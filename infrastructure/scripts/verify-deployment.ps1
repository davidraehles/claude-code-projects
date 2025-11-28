# Deployment Verification Script
# Checks Railway and Vercel deployments and shows status

Write-Host "=== Deployment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Test Railway Backend
Write-Host "--- Railway Backend Status ---" -ForegroundColor Yellow
Write-Host ""

$railwayUrl = "https://claude-code-projects-production.up.railway.app"
$healthUrl = "$railwayUrl/health"

Write-Host "Testing Railway backend at: $railwayUrl" -ForegroundColor White

try {
    Write-Host "Checking health endpoint..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri $healthUrl -Method Get -TimeoutSec 10

    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Railway backend is UP and healthy!" -ForegroundColor Green
        Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
    } else {
        Write-Host "⚠ Railway backend returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Railway backend health check failed!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check Railway CLI status
Write-Host "Checking Railway CLI status..." -ForegroundColor Gray
try {
    $railwayStatus = railway status 2>&1
    Write-Host "Railway CLI Status:" -ForegroundColor White
    Write-Host $railwayStatus -ForegroundColor Gray
} catch {
    Write-Host "Railway CLI not authenticated or project not linked" -ForegroundColor Yellow
    Write-Host "Run: railway login && railway link" -ForegroundColor White
}

Write-Host ""
Write-Host "--- Vercel Frontend Status ---" -ForegroundColor Yellow
Write-Host ""

# Check Vercel deployments
Write-Host "Checking Vercel deployments..." -ForegroundColor Gray

$frontendDir = Join-Path $PSScriptRoot "meal-planner-ui"

if (Test-Path $frontendDir) {
    Push-Location $frontendDir

    try {
        Write-Host "Vercel Deployments:" -ForegroundColor White
        $vercelDeployments = vercel ls 2>&1
        Write-Host $vercelDeployments -ForegroundColor Gray

        Write-Host ""
        Write-Host "Environment Variables:" -ForegroundColor White
        $vercelEnv = vercel env ls 2>&1
        Write-Host $vercelEnv -ForegroundColor Gray
    } catch {
        Write-Host "Vercel CLI not authenticated or project not linked" -ForegroundColor Yellow
        Write-Host "Run: vercel login && vercel link" -ForegroundColor White
    }

    Pop-Location
} else {
    Write-Host "✗ Frontend directory not found: $frontendDir" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== API Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# Test common API endpoints
$endpoints = @(
    @{Path="/health"; Description="Health Check"},
    @{Path="/docs"; Description="API Documentation"},
    @{Path="/api/recipes"; Description="Recipes API"}
)

foreach ($endpoint in $endpoints) {
    $url = "$railwayUrl$($endpoint.Path)"
    Write-Host "Testing: $($endpoint.Description)" -ForegroundColor White
    Write-Host "  URL: $url" -ForegroundColor Gray

    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 10
        Write-Host "  ✓ Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host "  ⚠ Status: $statusCode" -ForegroundColor Yellow
        } else {
            Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Railway Backend: $railwayUrl" -ForegroundColor White
Write-Host "Health Check: $healthUrl" -ForegroundColor White
Write-Host "API Docs: $railwayUrl/docs" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  Railway: railway logs --follow" -ForegroundColor White
Write-Host "  Vercel: vercel logs" -ForegroundColor White
Write-Host ""
Write-Host "To redeploy:" -ForegroundColor Yellow
Write-Host "  Railway: git push origin claude/main (auto-deploys)" -ForegroundColor White
Write-Host "  Vercel: cd meal-planner-ui && vercel --prod" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
