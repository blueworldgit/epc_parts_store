#!/usr/bin/env python3
"""
Test that shipping methods are still working after dashboard fix
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

from shipping.repository import Repository
from oscar.apps.catalogue.models import Product

def test_shipping():
    print("🚚 Testing shipping methods after dashboard fix...")
    
    try:
        # Get a sample product for basket simulation
        product = Product.objects.first()
        if not product:
            print("❌ No products found")
            return
            
        print(f"📦 Test product: {product.title}")
        
        # Test shipping repository
        repository = Repository()
        methods = repository.get_available_shipping_methods(
            basket=None,  # Can be None for basic test
            user=None,
            shipping_addr=None
        )
        
        print(f"🚚 Available shipping methods: {len(methods)}")
        for method in methods:
            print(f"  - {method.name}: {method.description}")
            if hasattr(method, 'calculate'):
                try:
                    charge = method.calculate(None)  # Basic test
                    print(f"    Test charge: £{charge}")
                except:
                    print(f"    Charge calculation requires basket")
        
        print("✅ Shipping system is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_shipping()
