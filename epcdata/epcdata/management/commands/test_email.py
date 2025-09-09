from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage, get_connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Gmail SMTP email configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to (default: uses EMAIL_HOST_USER)',
        )
        parser.add_argument(
            '--html',
            action='store_true',
            help='Send HTML test email',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🚀 EPC PARTS STORE - EMAIL CONFIGURATION TEST"))
        self.stdout.write("=" * 60)
        
        # Test configuration
        self.test_email_configuration()
        
        # Test SMTP connection
        if not self.test_smtp_connection():
            self.stdout.write(self.style.ERROR("\n❌ SMTP connection failed. Please check your configuration."))
            return
        
        self.stdout.write("\n" + "=" * 60)
        
        # Determine recipient
        recipient = options.get('email') or settings.EMAIL_HOST_USER
        
        # Send test email
        if self.send_test_email(recipient):
            self.stdout.write(self.style.SUCCESS("\n✅ Basic email test passed!"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Basic email test failed!"))
            return
        
        # Send HTML email if requested
        if options.get('html'):
            self.stdout.write("\n" + "=" * 60)
            if self.send_html_test_email(recipient):
                self.stdout.write(self.style.SUCCESS("\n✅ HTML email test passed!"))
            else:
                self.stdout.write(self.style.ERROR("\n❌ HTML email test failed!"))
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 EMAIL TESTING COMPLETE!"))
        self.stdout.write(f"📬 Check your inbox at: {recipient}")
        self.stdout.write("=" * 60)

    def test_email_configuration(self):
        """Test basic email configuration"""
        self.stdout.write("🔧 Testing Email Configuration...")
        self.stdout.write(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"📧 EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        self.stdout.write("-" * 50)

    def test_smtp_connection(self):
        """Test SMTP connection without sending email"""
        self.stdout.write("🔗 Testing SMTP Connection...")
        try:
            connection = get_connection()
            connection.open()
            self.stdout.write(self.style.SUCCESS("✅ SMTP Connection successful!"))
            connection.close()
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ SMTP Connection failed: {e}"))
            return False

    def send_test_email(self, recipient):
        """Send a test email"""
        self.stdout.write("📬 Sending test email...")
        
        try:
            send_mail(
                subject='🧪 Django Email Test - EPC Parts Store',
                message='This is a test email from your EPC Parts Store Django application.\n\nIf you receive this, Gmail SMTP is working correctly!\n\nBest regards,\nEPC Parts Store System',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✅ Test email sent successfully!"))
            self.stdout.write(f"📬 Email sent from: {settings.EMAIL_HOST_USER}")
            self.stdout.write(f"📬 Email sent to: {recipient}")
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {e}"))
            return False

    def send_html_test_email(self, recipient):
        """Send a fancy HTML test email"""
        self.stdout.write("🎨 Sending HTML test email...")
        
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
                <p>This email was sent automatically by your Django management command.</p>
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
                to=[recipient],
            )
            email.content_subtype = "html"
            email.send()
            
            self.stdout.write(self.style.SUCCESS("✅ HTML test email sent successfully!"))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send HTML email: {e}"))
            return False
