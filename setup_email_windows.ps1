# PowerShell script to set up Gmail email configuration
# Run this script before starting the Django server

Write-Host "Gmail Email Setup for Django Salon Booking" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Get Gmail address
$email = Read-Host "Enter your Gmail address (e.g., yourname@gmail.com)"

# Get App Password
Write-Host ""
Write-Host "IMPORTANT: You need a Gmail App Password, not your regular password!" -ForegroundColor Yellow
Write-Host "To get an App Password:" -ForegroundColor Yellow
Write-Host "1. Go to https://myaccount.google.com/security" -ForegroundColor Yellow
Write-Host "2. Enable 2-Step Verification (if not already enabled)" -ForegroundColor Yellow
Write-Host "3. Go to App passwords and generate one for 'Mail'" -ForegroundColor Yellow
Write-Host "4. Copy the 16-character password" -ForegroundColor Yellow
Write-Host ""
$appPassword = Read-Host "Enter your Gmail App Password (16 characters, spaces optional)"

# Set environment variables
$env:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "1"
$env:EMAIL_HOST_USER = $email
$env:EMAIL_HOST_PASSWORD = $appPassword -replace '\s', ''  # Remove spaces
$env:DEFAULT_FROM_EMAIL = $email

Write-Host ""
Write-Host "Email configuration set!" -ForegroundColor Green
Write-Host ""
Write-Host "Email settings:" -ForegroundColor Cyan
Write-Host "  EMAIL_HOST_USER: $email"
Write-Host "  EMAIL_HOST: smtp.gmail.com"
Write-Host "  EMAIL_PORT: 587"
Write-Host ""
Write-Host "To make these settings permanent, you can:" -ForegroundColor Yellow
Write-Host "1. Add them to your system environment variables, OR" -ForegroundColor Yellow
Write-Host "2. Install python-dotenv and create a .env file" -ForegroundColor Yellow
Write-Host ""
Write-Host "Now you can run: python manage.py runserver" -ForegroundColor Green




