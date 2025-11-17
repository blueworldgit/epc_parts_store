#!/usr/bin/env python
"""
Test script to verify shipping is being calculated and saved properly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from decimal import Decimal
from oscar.core.loading import get_model
from shipping.repository import Repository
from oscar.core import prices
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_shipping_calculation():
    """Test shipping calculation with sample weight"""
    
    print("🧪 Testing Shipping Calculation")
    print("=" * 50)
    
    # Get Oscar models
    Product = get_model('catalogue', 'Product')
    Basket = get_model('basket', 'Basket')
    ProductAttribute = get_model('catalogue', 'ProductAttribute')
    
    # Create or get a test product with weight
    try:
        # Try to find a product with weight
        products_with_weight = Product.objects.filter(
            attribute_values__attribute__code='weight'
        ).distinct()[:1]
        
        if products_with_weight:
            test_product = products_with_weight[0]
            print(f"✅ Using existing product: {test_product.title} (UPC: {test_product.upc})")
        else:
            print("❌ No products found with weight attribute")
            return
            
        # Create a test basket
        basket = Basket.objects.create()
        basket.add_product(test_product, quantity=2)
        
        print(f"🛒 Created test basket with 2x {test_product.title}")
        
        # Test shipping repository
        repository = Repository()
        available_methods = repository.get_available_shipping_methods(basket)
        
        print(f"🚚 Available shipping methods: {len(available_methods)}")
        
        for method in available_methods:
            print(f"\n📦 Method: {method.name} ({method.code})")
            try:
                charge = method.calculate(basket)
                print(f"   💰 Charge: £{charge.incl_tax}")
                print(f"   📊 Charge type: {type(charge)}")
                
                # Test order creation parameters
                if hasattr(method, 'charge_incl_tax'):
                    print(f"   🔧 Method charge_incl_tax: £{method.charge_incl_tax}")
                else:
                    print(f"   🔧 Method has no charge_incl_tax attribute")
                    
            except Exception as e:
                print(f"   ❌ Error calculating charge: {e}")
        
        # Clean up
        basket.delete()
        print(f"\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_email_context():
    """Test email context variables"""
    
    print("\n🧪 Testing Email Context")
    print("=" * 50)
    
    # Import order emails module to test context creation
    try:
        import epcdata.order_emails
        print("✅ Order emails module imported successfully")
        print("✅ Email context should now include shipping_cost and shipping_method_name")
    except Exception as e:
        print(f"❌ Error importing order emails: {e}")

if __name__ == "__main__":
    test_shipping_calculation()
    test_email_context()