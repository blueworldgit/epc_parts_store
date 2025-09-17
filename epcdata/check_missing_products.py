import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from oscar.apps.catalogue.models import ProductAttribute

print('🔍 Checking if callout data is being imported properly...')

# Check if the callout attribute exists
callout_attr = ProductAttribute.objects.filter(name='call_out_number').first()
if callout_attr:
    print(f'✅ Callout attribute exists: {callout_attr.name}')
else:
    print('❌ No callout attribute found!')

# Check all products in the LSFAL11A4PA157987 serial
serial_category = Category.objects.filter(slug='serial-lsfal11a4pa157987').first()
if serial_category:
    all_categories = serial_category.get_descendants()
    all_products = Product.objects.filter(categories__in=all_categories).distinct()
    
    print(f'\n📊 Total products in LSFAL11A4PA157987: {all_products.count()}')
    
    # Check for products with callout data
    products_with_callouts = 0
    products_without_callouts = 0
    
    print('\n🔍 Sample products and their callout data:')
    for product in all_products[:10]:  # Check first 10 products
        try:
            callout_value = product.attribute_values.filter(attribute__name='call_out_number').first()
            if callout_value and callout_value.value:
                print(f'  ✅ {product.title[:50]}: callout={callout_value.value}')
                products_with_callouts += 1
            else:
                print(f'  ❌ {product.title[:50]}: NO CALLOUT')
                products_without_callouts += 1
        except Exception as e:
            print(f'  ❌ {product.title[:50]}: ERROR - {e}')
            products_without_callouts += 1
    
    print(f'\n📈 Summary (first 10 products):')
    print(f'   Products with callouts: {products_with_callouts}')
    print(f'   Products without callouts: {products_without_callouts}')

# Let's also check what part numbers we expect vs what we have
print('\n🔍 Checking specific part numbers from HTML data...')
expected_parts = [
    'C00352453',  # From charging & energystorage Battery file
    'C00044731',  # From charging & energystorage Battery file  
    'C00087512',  # From charging & energystorage Battery file
    'C00178798',  # From power transmission (callout 40)
    'B90000621',  # From power transmission (callout 40)
]

for part_num in expected_parts:
    product = Product.objects.filter(upc=part_num).first()
    if product:
        print(f'  ✅ Found: {part_num} -> {product.title}')
        # Check its callout
        callout_value = product.attribute_values.filter(attribute__name='call_out_number').first()
        if callout_value:
            print(f'     Callout: {callout_value.value}')
        else:
            print(f'     Callout: MISSING')
    else:
        print(f'  ❌ Missing: {part_num}')