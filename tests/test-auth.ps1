# Test Authentication Endpoints
# Quick script to verify auth endpoints are working

$API_URL = "https://claude-code-projects-production.up.railway.app"

Write-Host "=== Testing Authentication Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Register a new user
Write-Host "1. Testing user registration..." -ForegroundColor Yellow
$registerData = @{
    email = "test@example.com"
    password = "testpassword123"
    country = "US"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerData `
        -ErrorAction Stop

    Write-Host "✓ Registration successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0,20))..." -ForegroundColor Gray
    $accessToken = $response.access_token
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "ℹ User already exists, trying login instead..." -ForegroundColor Yellow
    } else {
        Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 2: Login with existing user
Write-Host "2. Testing user login..." -ForegroundColor Yellow
$loginData = @{
    email = "test@example.com"
    password = "testpassword123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginData `
        -ErrorAction Stop

    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host "Refresh Token: $($response.refresh_token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host "Expires in: $($response.expires_in) seconds" -ForegroundColor Gray
    $accessToken = $response.access_token
    $refreshToken = $response.refresh_token
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Get current user profile
Write-Host "3. Testing get current user..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $accessToken"
    }

    $user = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/me" `
        -Method GET `
        -Headers $headers `
        -ErrorAction Stop

    Write-Host "✓ Got user profile!" -ForegroundColor Green
    Write-Host "User ID: $($user.id)" -ForegroundColor Gray
    Write-Host "Email: $($user.email)" -ForegroundColor Gray
    Write-Host "Country: $($user.country)" -ForegroundColor Gray
    Write-Host "Subscription: $($user.subscription_tier)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Get user failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Refresh token
Write-Host "4. Testing token refresh..." -ForegroundColor Yellow
$refreshData = @{
    refresh_token = $refreshToken
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/refresh" `
        -Method POST `
        -ContentType "application/json" `
        -Body $refreshData `
        -ErrorAction Stop

    Write-Host "✓ Token refresh successful!" -ForegroundColor Green
    Write-Host "New Access Token: $($response.access_token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Token refresh failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== All Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation: $API_URL/api/docs" -ForegroundColor White
Write-Host ""
