# PowerShell script to set Gmail email credentials
# Run this script and it will create a .env file with your credentials

Write-Host "=" -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Gmail Email Setup for Django Salon Booking" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# Get Gmail address
Write-Host "Step 1: Enter your Gmail address" -ForegroundColor Yellow
$email = Read-Host "Gmail address (e.g., yourname@gmail.com)"

if (-not $email -or $email -notmatch "@gmail\.com$") {
    Write-Host "ERROR: Please enter a valid Gmail address." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Get your Gmail App Password" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow
Write-Host "IMPORTANT: You need a Gmail App Password, NOT your regular password!" -ForegroundColor Red
Write-Host ""
Write-Host "To get an App Password:" -ForegroundColor Cyan
Write-Host "1. Go to: https://myaccount.google.com/security" -ForegroundColor White
Write-Host "2. Enable '2-Step Verification' (if not already enabled)" -ForegroundColor White
Write-Host "3. Go to 'App passwords'" -ForegroundColor White
Write-Host "4. Select 'Mail' and generate a password" -ForegroundColor White
Write-Host "5. Copy the 16-character password" -ForegroundColor White
Write-Host ""
Write-Host "See GET_GMAIL_APP_PASSWORD.md for detailed instructions" -ForegroundColor Gray
Write-Host ""

$appPassword = Read-Host "Enter your Gmail App Password (16 characters)" -AsSecureString
$appPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($appPassword)
)

# Remove spaces
$appPasswordPlain = $appPasswordPlain -replace '\s', ''

if ($appPasswordPlain.Length -ne 16) {
    Write-Host ""
    Write-Host "WARNING: App password should be 16 characters, you entered $($appPasswordPlain.Length)" -ForegroundColor Yellow
    $confirm = Read-Host "Continue anyway? (y/n)"
    if ($confirm -ne 'y') {
        exit 1
    }
}

# Create .env file content
$envContent = @"
# Gmail Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=$email
EMAIL_HOST_PASSWORD=$appPasswordPlain
DEFAULT_FROM_EMAIL=$email
"@

# Write to .env file
try {
    $envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline
    Write-Host ""
    Write-Host "✓ Configuration saved to .env file" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERROR: Could not write to .env file: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Install python-dotenv" -ForegroundColor Yellow
Write-Host "Installing python-dotenv..." -ForegroundColor Gray
python -m pip install python-dotenv -q

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Your email configuration has been saved to .env file." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your Django server (stop and start again)" -ForegroundColor White
Write-Host "2. The settings will automatically load from .env" -ForegroundColor White
Write-Host "3. Test by creating a booking with an email address" -ForegroundColor White
Write-Host ""
Write-Host "To verify it's working, run:" -ForegroundColor Cyan
Write-Host "  python test_email.py" -ForegroundColor White
Write-Host ""




