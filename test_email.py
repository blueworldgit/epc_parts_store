#!/usr/bin/env python3
"""
Test actual email sending functionality
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent / "epcdata"
sys.path.insert(0, str(project_dir))

# Load environment
import dotenv
dotenv.load_dotenv()

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Initialize Django
import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_settings():
    print("🔧 Testing email configuration...")
    
    # Check email settings
    print(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"📧 EMAIL_HOST_PASSWORD: {'***SET***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"📧 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("")
    
    try:
        print("🧪 Testing direct email send...")
        result = send_mail(
            subject='Test Email from Van Parts Direct',
            message='This is a test email to verify SMTP configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shanepillay011@gmail.com'],
            fail_silently=False,
        )
        
        if result:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    test_email_settings()
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shanepillay011@gmail.com'],
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print("💡 This suggests SMTP credentials are not properly configured")
        
        # Check environment variables
        print("\n🔍 Environment variables:")
        print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER', 'NOT SET')}")
        print(f"EMAIL_HOST_PASSWORD: {'***SET***' if os.getenv('EMAIL_HOST_PASSWORD') else 'NOT SET'}")
        print(f"DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL', 'NOT SET')}")

if __name__ == "__main__":
    test_email_settings()
