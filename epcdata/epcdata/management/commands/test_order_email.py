from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model
from epcdata.order_emails import send_custom_order_email
import uuid

# Get models
Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
Product = get_model('catalogue', 'Product')
User = get_user_model()

class Command(BaseCommand):
    help = 'Test order confirmation email with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='info@rapidfit.co.uk',
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("📧 TESTING ORDER CONFIRMATION EMAIL"))
        self.stdout.write("=" * 60)
        
        try:
            # Create or get a test user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': 'Test',
                    'last_name': 'Customer',
                    'is_active': True
                }
            )
            
            # Get the first product for testing
            product = Product.objects.first()
            if not product:
                self.stdout.write(self.style.ERROR("❌ No products found. Please add some products first."))
                return
            
            # Create a mock order object for testing
            class MockOrder:
                def __init__(self):
                    self.number = f"TEST-{uuid.uuid4().hex[:8].upper()}"
                    self.email = email
                    self.user = user
                    self.total_incl_tax = 99.99
                    self.date_placed = "January 15, 2025"
                    self.billing_address = None
                    self.shipping_address = None
                    
                def lines(self):
                    return MockOrderLine.objects.all()
                    
            class MockOrderLine:
                def __init__(self, product, quantity=1, price=99.99):
                    self.product = product
                    self.quantity = quantity
                    self.line_price_incl_tax = price
                    
                @classmethod
                def all(cls):
                    return [cls(product, 1, 99.99)]
                    
            class MockOrderLineManager:
                def all(self):
                    return [MockOrderLine(product, 1, 99.99)]
            
            # Create mock order
            mock_order = MockOrder()
            mock_order.lines = MockOrderLineManager()
            
            self.stdout.write(f"📋 Test Order Number: {mock_order.number}")
            self.stdout.write(f"📧 Sending to: {email}")
            self.stdout.write(f"🛒 Product: {product.title}")
            
            # Try to send email using our custom function
            from epcdata.order_emails import send_custom_order_email
            
            success = send_custom_order_email(
                mock_order, 
                'order_confirmation',
                extra_context={'test_mode': True}
            )
            
            if success:
                self.stdout.write(self.style.SUCCESS("\n✅ Test order confirmation email sent successfully!"))
                self.stdout.write(f"📬 Check your inbox at: {email}")
            else:
                self.stdout.write(self.style.ERROR("\n❌ Failed to send test email"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {e}"))
            
        self.stdout.write("=" * 60)
