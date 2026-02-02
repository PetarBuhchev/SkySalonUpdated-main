"""
Script to verify email setup and test connection.
Run this to check if your email configuration is correct.
"""
import os
import sys

# Set environment variables first
os.environ["EMAIL_BACKEND"] = "django.core.mail.backends.smtp.EmailBackend"
os.environ["EMAIL_HOST_USER"] = "skysalonskysalonandbeauty@gmail.com"
os.environ["EMAIL_HOST_PASSWORD"] = "hzhh onfi pyju kuf"  # Try with spaces
os.environ["DEFAULT_FROM_EMAIL"] = "skysalonskysalonandbeauty@gmail.com"

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salon_site.settings")
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("Email Configuration Verification")
print("=" * 60)
print()
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    print("ERROR: Still using console backend!")
    print("Make sure environment variables are set before running this script.")
    sys.exit(1)

if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("ERROR: Email credentials not set!")
    sys.exit(1)

print("Testing email connection...")
print()

test_email = input("Enter email address to send test to (or press Enter to skip): ").strip()

if not test_email:
    print("Skipping email test.")
    print("Configuration looks correct. Try creating a booking with an email address.")
    sys.exit(0)

try:
    print(f"Sending test email to {test_email}...")
    send_mail(
        subject="Test Email from Sky Salon Booking System",
        message="This is a test email to verify your email configuration is working correctly!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[test_email],
        fail_silently=False,
    )
    print()
    print("✓ Email sent successfully!")
    print(f"Check the inbox (and spam folder) of {test_email}")
except Exception as e:
    print()
    print(f"✗ Error sending email: {e}")
    print()
    print("Possible issues:")
    print("1. App Password might be incorrect - try regenerating it")
    print("2. 2-Step Verification might not be enabled")
    print("3. Password format - try with/without spaces")
    print("4. Check TROUBLESHOOTING_EMAIL.md for more help")
    sys.exit(1)



