# Simple Authentication Test Script
$API_URL = "https://claude-code-projects-production.up.railway.app"

Write-Host "=== Testing Authentication Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# Test Login
Write-Host "Testing login endpoint..." -ForegroundColor Yellow
$loginJson = '{"email":"test@example.com","password":"testpassword123"}'

$result = curl.exe -s -X POST "$API_URL/api/v1/auth/login" `
    -H "Content-Type: application/json" `
    -d $loginJson

Write-Host "Response:" -ForegroundColor White
Write-Host $result
Write-Host ""

# Check if we got a token
if ($result -match '"access_token"') {
    Write-Host "✓ Login endpoint is working!" -ForegroundColor Green
} else {
    Write-Host "✗ Login endpoint returned an error" -ForegroundColor Red
}

Write-Host ""
Write-Host "Visit the API docs to test interactively:" -ForegroundColor Cyan
Write-Host "$API_URL/api/docs" -ForegroundColor White
