# Installation script for Railway and Vercel CLI tools
# Run this script in PowerShell (7+ recommended)

Write-Host "=== Railway & Vercel CLI Installation ===" -ForegroundColor Cyan

# Check PowerShell version
Write-Host "`nPowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "Note: You're using PowerShell $($PSVersionTable.PSVersion.Major). PowerShell 7+ is recommended." -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/PowerShell/PowerShell/releases" -ForegroundColor Yellow
}

# Common Node.js installation paths
$commonNodePaths = @(
    "$env:ProgramFiles\nodejs",
    "${env:ProgramFiles(x86)}\nodejs",
    "$env:LOCALAPPDATA\Programs\nodejs",
    "$env:APPDATA\npm"
)

# Check if Node.js is installed and add to PATH if needed
Write-Host "`nChecking for Node.js..." -ForegroundColor Yellow

$nodeFound = $false
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue

if ($nodeCmd -and $npmCmd) {
    $nodeFound = $true
} else {
    # Try to find Node.js in common locations
    Write-Host "Node.js not in PATH. Searching common locations..." -ForegroundColor Yellow

    foreach ($path in $commonNodePaths) {
        if (Test-Path "$path\node.exe") {
            Write-Host "Found Node.js at: $path" -ForegroundColor Green
            $env:Path += ";$path"
            $nodeFound = $true
            break
        }
    }
}

if ($nodeFound) {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
    Write-Host "✓ npm $npmVersion found" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    Write-Host "`nPlease install Node.js first:" -ForegroundColor Yellow
    Write-Host "1. Visit https://nodejs.org/" -ForegroundColor White
    Write-Host "2. Download the LTS version (v20.x or v22.x)" -ForegroundColor White
    Write-Host "3. Run the installer (use default settings)" -ForegroundColor White
    Write-Host "4. IMPORTANT: Check 'Add to PATH' during installation" -ForegroundColor White
    Write-Host "5. Restart PowerShell and run this script again" -ForegroundColor White
    Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Install Railway CLI
Write-Host "`nInstalling Railway CLI..." -ForegroundColor Yellow
try {
    npm install -g @railway/cli
    Write-Host "✓ Railway CLI installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install Railway CLI" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Install Vercel CLI
Write-Host "`nInstalling Vercel CLI..." -ForegroundColor Yellow
try {
    npm install -g vercel
    Write-Host "✓ Vercel CLI installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install Vercel CLI" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Verify installations
Write-Host "`n=== Verifying Installations ===" -ForegroundColor Cyan

Write-Host "`nRailway CLI:" -ForegroundColor Yellow
try {
    $railwayVersion = railway --version
    Write-Host "✓ $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Railway CLI not found" -ForegroundColor Red
}

Write-Host "`nVercel CLI:" -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version
    Write-Host "✓ Vercel $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Vercel CLI not found" -ForegroundColor Red
}

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host @"

To authenticate and use the CLI tools:

1. Railway:
   railway login
   railway link

2. Vercel:
   vercel login
   vercel link

For debugging, see CLI_INSTALLATION.md for available commands.

"@ -ForegroundColor White

Write-Host "Installation complete! Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
