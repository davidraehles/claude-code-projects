# Login and Link Script for Railway and Vercel
# Run this script after installing the CLI tools

Write-Host "=== Railway & Vercel Authentication ===" -ForegroundColor Cyan

# Railway Login and Link
Write-Host "`n--- Railway Setup ---" -ForegroundColor Yellow
Write-Host "Step 1: Login to Railway (this will open your browser)..." -ForegroundColor White

try {
    railway login

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Railway login successful!" -ForegroundColor Green

        Write-Host "`nStep 2: Linking to Railway project..." -ForegroundColor White
        Write-Host "This will show you a list of your Railway projects." -ForegroundColor Gray

        railway link

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Railway project linked!" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to link Railway project" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Railway login failed" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" -NoNewline

# Vercel Login and Link
Write-Host "--- Vercel Setup ---" -ForegroundColor Yellow
Write-Host "Step 1: Login to Vercel (this will open your browser)..." -ForegroundColor White

try {
    vercel login

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Vercel login successful!" -ForegroundColor Green

        Write-Host "`nStep 2: Linking to Vercel project..." -ForegroundColor White
        Write-Host "Navigate to frontend directory first..." -ForegroundColor Gray

        # Change to frontend directory
        $frontendDir = Join-Path $PSScriptRoot "meal-planner-ui"

        if (Test-Path $frontendDir) {
            Push-Location $frontendDir

            Write-Host "Current directory: $frontendDir" -ForegroundColor Gray
            vercel link

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Vercel project linked!" -ForegroundColor Green
            } else {
                Write-Host "✗ Failed to link Vercel project" -ForegroundColor Red
            }

            Pop-Location
        } else {
            Write-Host "✗ Frontend directory not found: $frontendDir" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Vercel login failed" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan

# Check Railway status
Write-Host "`nRailway Status:" -ForegroundColor Yellow
try {
    railway status
} catch {
    Write-Host "Not linked or error occurred" -ForegroundColor Gray
}

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host @"

✅ Railway Commands:
   railway logs              - View deployment logs
   railway status            - Check service status
   railway variables         - List environment variables
   railway open              - Open project in browser

✅ Vercel Commands (from meal-planner-ui directory):
   vercel                    - Deploy to preview
   vercel --prod             - Deploy to production
   vercel logs               - View logs
   vercel env ls             - List environment variables
   vercel open               - Open project in browser

📋 Your Project URLs:
   Railway: https://claude-code-projects-production.up.railway.app
   Vercel: (will be shown after first deployment)

"@ -ForegroundColor White

Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
