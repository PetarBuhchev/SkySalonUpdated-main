"""
Quick test to verify email is working with the new credentials.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salon_site.settings")
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print()

if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    print("ERROR: Still using console backend!")
    print("Make sure .env file exists and restart the server.")
    exit(1)

test_email = input("Enter email address to send test to (or press Enter to skip): ").strip()

if test_email:
    try:
        print(f"\nSending test email to {test_email}...")
        
        # Send a simple test email
        send_mail(
            subject="Test Email from Sky Salon Booking System",
            message="This is a test email to verify your email configuration is working correctly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✓ Email sent successfully!")
        print(f"Check the inbox (and spam folder) of {test_email}")
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        print("\nCommon issues:")
        print("1. Check that the App Password is correct")
        print("2. Verify 2-Step Verification is enabled")
        print("3. Make sure EMAIL_USE_TLS is True")
else:
    print("Skipping email test. Configuration looks good!")
    print("Restart your Django server and try creating a booking with an email address.")



