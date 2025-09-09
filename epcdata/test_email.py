#!/usr/bin/env python
"""
Email Configuration Test Script
Tests Gmail SMTP configuration for Django app
"""

import os
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Add the project directory to Python path
import sys
sys.path.append(str(BASE_DIR))

django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core.mail import get_connection

def test_email_configuration():
    """Test basic email configuration"""
    print("🔧 Testing Email Configuration...")
    print(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"📧 EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print("-" * 50)

def test_smtp_connection():
    """Test SMTP connection without sending email"""
    print("🔗 Testing SMTP Connection...")
    try:
        connection = get_connection()
        connection.open()
        print("✅ SMTP Connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ SMTP Connection failed: {e}")
        return False

def send_test_email():
    """Send a test email"""
    print("📬 Sending test email...")
    
    try:
        # Simple test email
        send_mail(
            subject='🧪 Django Email Test - EPC Parts Store',
            message='This is a test email from your EPC Parts Store Django application.\n\nIf you receive this, Gmail SMTP is working correctly!\n\nBest regards,\nEPC Parts Store System',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        print(f"📬 Email sent from: {settings.EMAIL_HOST_USER}")
        print(f"📬 Email sent to: {settings.EMAIL_HOST_USER}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def send_html_test_email():
    """Send a fancy HTML test email"""
    print("🎨 Sending HTML test email...")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #ff6b35; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .footer { background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧪 EPC Parts Store Email Test</h1>
        </div>
        <div class="content">
            <h2>Gmail SMTP Configuration Test</h2>
            <p>Congratulations! Your Django application can now send emails using Gmail SMTP.</p>
            <p><strong>Configuration Details:</strong></p>
            <ul>
                <li>SMTP Server: smtp.gmail.com</li>
                <li>Port: 587 (TLS)</li>
                <li>From Email: info@rapidfit.co.uk</li>
            </ul>
            <p>This email was sent automatically by your Django test script.</p>
        </div>
        <div class="footer">
            EPC Parts Store - Django Email System
        </div>
    </body>
    </html>
    """
    
    try:
        email = EmailMessage(
            subject='🎨 HTML Email Test - EPC Parts Store',
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
        )
        email.content_subtype = "html"  # Main content is now text/html
        email.send()
        
        print("✅ HTML test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send HTML email: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 EPC PARTS STORE - EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Test 1: Configuration
    test_email_configuration()
    
    # Test 2: SMTP Connection
    if not test_smtp_connection():
        print("\n❌ SMTP connection failed. Please check your configuration.")
        return
    
    print("\n" + "=" * 60)
    
    # Test 3: Simple Text Email
    if send_test_email():
        print("\n✅ Basic email test passed!")
    else:
        print("\n❌ Basic email test failed!")
        return
    
    print("\n" + "=" * 60)
    
    # Test 4: HTML Email
    if send_html_test_email():
        print("\n✅ HTML email test passed!")
    else:
        print("\n❌ HTML email test failed!")
    
    print("\n" + "=" * 60)
    print("🎉 EMAIL TESTING COMPLETE!")
    print("📬 Check your inbox at: info@rapidfit.co.uk")
    print("=" * 60)

if __name__ == "__main__":
    main()
