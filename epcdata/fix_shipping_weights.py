#!/usr/bin/env python
"""
Fix shipping by adding weight attributes to products
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from decimal import Decimal
from oscar.core.loading import get_model
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_weight_attributes():
    """Add weight attributes to products that don't have them"""
    
    print("🏋️ Adding Weight Attributes to Products")
    print("=" * 50)
    
    # Get Oscar models
    Product = get_model('catalogue', 'Product')
    ProductAttribute = get_model('catalogue', 'ProductAttribute')
    ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
    
    try:
        # Create or get weight attribute
        weight_attr, created = ProductAttribute.objects.get_or_create(
            code='weight',
            defaults={
                'name': 'Weight (kg)',
                'type': ProductAttribute.FLOAT,
                'required': False,
            }
        )
        
        if created:
            print(f"✅ Created weight attribute: {weight_attr}")
        else:
            print(f"✅ Using existing weight attribute: {weight_attr}")
        
        # Get products without weight attributes
        products_without_weight = Product.objects.exclude(
            attribute_values__attribute=weight_attr
        )
        
        print(f"📦 Found {products_without_weight.count()} products without weight")
        
        # Add default weights based on product categories or parts
        updated_count = 0
        for product in products_without_weight[:50]:  # Start with first 50
            try:
                # Assign weight based on product type/title
                default_weight = Decimal('2.5')  # Default 2.5kg for motor parts
                
                # Adjust weight based on product title keywords
                title_lower = product.title.lower()
                if any(word in title_lower for word in ['engine', 'block', 'transmission']):
                    default_weight = Decimal('45.0')  # Heavy parts
                elif any(word in title_lower for word in ['battery', 'radiator', 'alternator']):
                    default_weight = Decimal('15.0')  # Medium parts  
                elif any(word in title_lower for word in ['filter', 'belt', 'gasket', 'seal']):
                    default_weight = Decimal('1.0')   # Light parts
                elif any(word in title_lower for word in ['brake', 'disc', 'pad']):
                    default_weight = Decimal('8.0')   # Brake parts
                elif any(word in title_lower for word in ['wheel', 'tyre', 'tire']):
                    default_weight = Decimal('25.0')  # Wheels/tyres
                
                # Create weight attribute value
                ProductAttributeValue.objects.create(
                    product=product,
                    attribute=weight_attr,
                    value_float=float(default_weight)
                )
                
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"   📦 Updated {updated_count} products...")
                    
            except Exception as e:
                logger.warning(f"Could not add weight to product {product.id}: {e}")
                continue
        
        print(f"✅ Successfully added weights to {updated_count} products")
        
        # Show sample products with weights
        products_with_weight = Product.objects.filter(
            attribute_values__attribute=weight_attr
        )[:5]
        
        print(f"\n📋 Sample products with weights:")
        for product in products_with_weight:
            try:
                weight_value = product.attribute_values.get(attribute=weight_attr)
                print(f"   • {product.title[:50]}... = {weight_value.value_float}kg")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error adding weight attributes: {e}")
        import traceback
        traceback.print_exc()

def test_weight_based_shipping():
    """Test that weight-based shipping now works"""
    
    print(f"\n🧪 Testing Weight-Based Shipping")
    print("=" * 50)
    
    # Get Oscar models
    Product = get_model('catalogue', 'Product')
    Basket = get_model('basket', 'Basket')
    ProductAttribute = get_model('catalogue', 'ProductAttribute')
    
    try:
        # Find products with different weights
        weight_attr = ProductAttribute.objects.get(code='weight')
        
        # Light product (should be £11.95 shipping)
        light_products = Product.objects.filter(
            attribute_values__attribute=weight_attr,
            attribute_values__value_float__lte=5.0
        )[:1]
        
        # Heavy product (should be higher shipping)
        heavy_products = Product.objects.filter(
            attribute_values__attribute=weight_attr,
            attribute_values__value_float__gte=30.0
        )[:1]
        
        from shipping.repository import Repository
        repository = Repository()
        
        # Test light product shipping
        if light_products:
            light_product = light_products[0]
            basket = Basket.objects.create()
            basket.add_product(light_product, quantity=1)
            
            methods = repository.get_available_shipping_methods(basket)
            weight_method = next((m for m in methods if m.code == 'weight_based'), None)
            
            if weight_method:
                charge = weight_method.calculate(basket)
                weight_value = light_product.attribute_values.get(attribute=weight_attr)
                print(f"💡 Light product: {light_product.title[:40]}...")
                print(f"   Weight: {weight_value.value_float}kg")
                print(f"   Shipping: £{charge.incl_tax}")
            
            basket.delete()
        
        # Test heavy product shipping  
        if heavy_products:
            heavy_product = heavy_products[0]
            basket = Basket.objects.create()
            basket.add_product(heavy_product, quantity=2)  # 2 heavy items
            
            methods = repository.get_available_shipping_methods(basket)
            weight_method = next((m for m in methods if m.code == 'weight_based'), None)
            
            if weight_method:
                charge = weight_method.calculate(basket)
                weight_value = heavy_product.attribute_values.get(attribute=weight_attr)
                total_weight = weight_value.value_float * 2
                print(f"🏋️ Heavy products: 2x {heavy_product.title[:40]}...")
                print(f"   Total weight: {total_weight}kg") 
                print(f"   Shipping: £{charge.incl_tax}")
                
                # Show which weight band this falls into
                from shipping.repository import WeightBasedShippingMethod
                method = WeightBasedShippingMethod()
                for min_w, max_w, cost in method.WEIGHT_BANDS:
                    if min_w <= Decimal(str(total_weight)) <= max_w:
                        print(f"   Weight band: {min_w}-{max_w}kg = £{cost}")
                        break
            
            basket.delete()
        
        print(f"✅ Weight-based shipping test completed")
        
    except Exception as e:
        print(f"❌ Weight-based shipping test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_weight_attributes()
    test_weight_based_shipping()