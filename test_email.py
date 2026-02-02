"""
Test script to verify email configuration.
Run this after setting up your Gmail credentials.
"""
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salon_site.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test sending an email with current configuration."""
    print("Testing email configuration...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    if not settings.EMAIL_HOST_USER:
        print("ERROR: EMAIL_HOST_USER is not set!")
        print("Please set your Gmail address as an environment variable:")
        print("  Windows PowerShell: $env:EMAIL_HOST_USER='your-email@gmail.com'")
        print("  Windows CMD: set EMAIL_HOST_USER=your-email@gmail.com")
        print("  Linux/Mac: export EMAIL_HOST_USER='your-email@gmail.com'")
        return False
    
    if not settings.EMAIL_HOST_PASSWORD:
        print("ERROR: EMAIL_HOST_PASSWORD is not set!")
        print("Please set your Gmail App Password as an environment variable:")
        print("  Windows PowerShell: $env:EMAIL_HOST_PASSWORD='your-app-password'")
        print("  Windows CMD: set EMAIL_HOST_PASSWORD=your-app-password")
        print("  Linux/Mac: export EMAIL_HOST_PASSWORD='your-app-password'")
        return False
    
    # Get test email address
    test_email = input("Enter an email address to send a test email to: ").strip()
    
    if not test_email:
        print("No email address provided. Exiting.")
        return False
    
    try:
        print(f"\nSending test email to {test_email}...")
        send_mail(
            subject="Test Email from Salon Booking System",
            message="This is a test email to verify your email configuration is working correctly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✓ Email sent successfully!")
        print(f"Check the inbox (and spam folder) of {test_email}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        print("\nCommon issues:")
        print("1. Make sure you're using a Gmail App Password, not your regular password")
        print("2. Verify 2-Step Verification is enabled on your Google account")
        print("3. Check that EMAIL_USE_TLS is set to True")
        print("4. Verify your Gmail address and App Password are correct")
        return False

if __name__ == "__main__":
    test_email()




