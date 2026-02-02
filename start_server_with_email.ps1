# PowerShell script to start Django server with email configuration
# This script sets email environment variables and starts the server

Write-Host "Starting Django Server with Email Configuration" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if email credentials are already set
if (-not $env:EMAIL_HOST_USER -or -not $env:EMAIL_HOST_PASSWORD) {
    Write-Host "Email credentials not found in environment." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable email sending, please provide:" -ForegroundColor Yellow
    Write-Host ""
    
    $email = Read-Host "Enter your Gmail address (or press Enter to skip)"
    if ($email) {
        Write-Host ""
        Write-Host "IMPORTANT: You need a Gmail App Password!" -ForegroundColor Yellow
        Write-Host "Get one at: https://myaccount.google.com/security" -ForegroundColor Yellow
        Write-Host ""
        $appPassword = Read-Host "Enter your Gmail App Password (16 characters)"
        
        if ($appPassword) {
            $env:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
            $env:EMAIL_HOST_USER = $email
            $env:EMAIL_HOST_PASSWORD = $appPassword -replace '\s', ''
            $env:DEFAULT_FROM_EMAIL = $email
            
            Write-Host ""
            Write-Host "Email configuration set!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "No password provided. Using console email backend (emails will print to console)." -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "No email provided. Using console email backend (emails will print to console)." -ForegroundColor Yellow
    }
} else {
    Write-Host "Email credentials found in environment." -ForegroundColor Green
    Write-Host "EMAIL_HOST_USER: $env:EMAIL_HOST_USER"
    Write-Host "EMAIL_BACKEND: $env:EMAIL_BACKEND"
    Write-Host ""
}

Write-Host "Starting Django development server..." -ForegroundColor Cyan
Write-Host ""

# Start the server
python manage.py runserver




