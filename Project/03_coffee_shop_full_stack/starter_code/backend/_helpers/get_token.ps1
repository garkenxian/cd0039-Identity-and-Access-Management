param([string]$Role = 'barista')

# Load .env file
$envFile = Join-Path $PSScriptRoot '.env'
if (Test-Path $envFile) {
    Get-Content $envFile | Where-Object { $_ -match '^\w+=' -and -not $_.StartsWith('#') } | ForEach-Object {
        $parts = $_ -split '=', 2
        if ($parts.Count -eq 2) {
            [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
        }
    }
}

# Configuration
$auth0Domain = if ([Environment]::GetEnvironmentVariable('AUTH0_DOMAIN')) { [Environment]::GetEnvironmentVariable('AUTH0_DOMAIN') } else { 'dev-53bey634viqgnyzc.us.auth0.com' }
$clientId = [Environment]::GetEnvironmentVariable('AUTH0_CLIENT_ID')
$clientSecret = [Environment]::GetEnvironmentVariable('AUTH0_CLIENT_SECRET')
$audience = if ([Environment]::GetEnvironmentVariable('API_AUDIENCE')) { [Environment]::GetEnvironmentVariable('API_AUDIENCE') } else { 'coffee-shop-api' }

if ([string]::IsNullOrEmpty($clientId)) {
    Write-Host "Error: AUTH0_CLIENT_ID not set in .env" -ForegroundColor Red
    exit 1
}

# User credentials
$emails = @{'barista' = 'barista@test.local'; 'manager' = 'manager@test.local'}

if ([string]::IsNullOrEmpty($emails[$Role])) {
    Write-Host "Error: Invalid role '$Role'. Use 'barista' or 'manager'" -ForegroundColor Red
    exit 1
}

$email = $emails[$Role]
# Prompt at runtime to avoid storing secrets in source.
$securePassword = Read-Host -Prompt "Enter password for $email" -AsSecureString
if (-not $securePassword -or $securePassword.Length -eq 0) {
    Write-Host "Error: Password is required" -ForegroundColor Red
    exit 1
}

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

$securePassword = $null

$tokenUrl = "https://$auth0Domain/oauth/token"

$jsonBody = @"
{
  "grant_type": "password",
  "username": "$email",
  "password": "$password",
  "audience": "$audience",
  "client_id": "$clientId",
  "client_secret": "$clientSecret"
}
"@

try {
    $response = Invoke-WebRequest -Uri $tokenUrl -Method POST -ContentType 'application/json' -Body $jsonBody -UseBasicParsing
    $tokenData = ConvertFrom-Json $response.Content
    
    Write-Host "`n======================================================================"  -ForegroundColor Green
    Write-Host "JWT Token for $($Role.ToUpper())"  -ForegroundColor Green
    Write-Host "======================================================================`n"  -ForegroundColor Green
    Write-Host $tokenData.access_token
    Write-Host "`n"
    Write-Host "Type: $($tokenData.token_type)   Expires: $($tokenData.expires_in)s" -ForegroundColor Cyan
    Write-Host "======================================================================`n"  -ForegroundColor Green
    
} catch {
    Write-Host "Error: Failed to get token" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

