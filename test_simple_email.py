#!/usr/bin/env python3
"""
Test email sending with updated Gmail credentials
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

def test_email():
    print("📧 Testing email configuration...")
    print(f"FROM EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"EMAIL HOST: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL PASSWORD: {'***SET***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    try:
        # Send a simple test email
        result = send_mail(
            subject='Test Email from Van Parts Direct',
            message='This is a test email to verify SMTP configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['bluefieldmediasa@gmail.com'],
            fail_silently=False,
        )
        
        if result:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    test_email()
