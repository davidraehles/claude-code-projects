# Vercel Environment Variables Setup Script
# Configures required environment variables for Vercel deployment

Write-Host "=== Vercel Environment Variables Setup ===" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "meal-planner-ui"

if (-not (Test-Path $frontendDir)) {
    Write-Host "✗ Frontend directory not found: $frontendDir" -ForegroundColor Red
    exit 1
}

Push-Location $frontendDir

Write-Host "Current directory: $frontendDir" -ForegroundColor Gray
Write-Host ""

# Check if vercel is installed and authenticated
Write-Host "Checking Vercel CLI..." -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version 2>&1
    Write-Host "✓ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Vercel CLI not found. Please run: npm install -g vercel" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "--- Setting Environment Variables ---" -ForegroundColor Yellow
Write-Host ""

# 1. NEXT_PUBLIC_API_URL
Write-Host "1. Setting NEXT_PUBLIC_API_URL..." -ForegroundColor White
$apiUrl = "https://claude-code-projects-production.up.railway.app"
Write-Host "   Value: $apiUrl" -ForegroundColor Gray

try {
    # Remove existing variable if it exists
    vercel env rm NEXT_PUBLIC_API_URL production --yes 2>$null
    vercel env rm NEXT_PUBLIC_API_URL preview --yes 2>$null
    vercel env rm NEXT_PUBLIC_API_URL development --yes 2>$null

    # Add new variable for all environments
    Write-Host "   Adding to production..." -ForegroundColor Gray
    echo $apiUrl | vercel env add NEXT_PUBLIC_API_URL production

    Write-Host "   Adding to preview..." -ForegroundColor Gray
    echo $apiUrl | vercel env add NEXT_PUBLIC_API_URL preview

    Write-Host "   Adding to development..." -ForegroundColor Gray
    echo $apiUrl | vercel env add NEXT_PUBLIC_API_URL development

    Write-Host "   ✓ NEXT_PUBLIC_API_URL configured" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Error setting NEXT_PUBLIC_API_URL: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# 2. NEXTAUTH_SECRET
Write-Host "2. Setting NEXTAUTH_SECRET..." -ForegroundColor White
Write-Host "   Generating secure secret..." -ForegroundColor Gray

# Generate a random secret
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$secret = [Convert]::ToBase64String($bytes)
$rng.Dispose()

Write-Host "   Generated: $($secret.Substring(0, 10))..." -ForegroundColor Gray

try {
    # Remove existing variable if it exists
    vercel env rm NEXTAUTH_SECRET production --yes 2>$null
    vercel env rm NEXTAUTH_SECRET preview --yes 2>$null
    vercel env rm NEXTAUTH_SECRET development --yes 2>$null

    # Add new variable for all environments
    Write-Host "   Adding to production..." -ForegroundColor Gray
    echo $secret | vercel env add NEXTAUTH_SECRET production

    Write-Host "   Adding to preview..." -ForegroundColor Gray
    echo $secret | vercel env add NEXTAUTH_SECRET preview

    Write-Host "   Adding to development..." -ForegroundColor Gray
    echo $secret | vercel env add NEXTAUTH_SECRET development

    Write-Host "   ✓ NEXTAUTH_SECRET configured" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Error setting NEXTAUTH_SECRET: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# 3. NEXTAUTH_URL
Write-Host "3. NEXTAUTH_URL (skip for now - update after first deployment)" -ForegroundColor White
Write-Host "   This will be your Vercel deployment URL" -ForegroundColor Gray
Write-Host "   You can add it later with:" -ForegroundColor Gray
Write-Host "   vercel env add NEXTAUTH_URL production" -ForegroundColor White

Write-Host ""
Write-Host "--- Summary ---" -ForegroundColor Cyan
Write-Host ""

# List all environment variables
Write-Host "Current environment variables:" -ForegroundColor Yellow
try {
    vercel env ls
} catch {
    Write-Host "Could not list environment variables" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Deploy to Vercel:" -ForegroundColor Yellow
Write-Host "   vercel --prod" -ForegroundColor White
Write-Host ""
Write-Host "2. After deployment, update NEXTAUTH_URL:" -ForegroundColor Yellow
Write-Host "   vercel env add NEXTAUTH_URL production" -ForegroundColor White
Write-Host "   (Enter your Vercel URL, e.g., https://your-project.vercel.app)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Redeploy to apply the NEXTAUTH_URL:" -ForegroundColor Yellow
Write-Host "   vercel --prod --force" -ForegroundColor White
Write-Host ""

Pop-Location

Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
