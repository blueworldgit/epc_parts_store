import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product

print('🔍 Debugging URL routing for LSFAL11A4PA157987 serial...')

# Check the exact child categories that exist
parent_slug = 'serial-LSFAL11A4PA157987-parent-12'
parent_category = Category.objects.filter(slug=parent_slug).first()

if parent_category:
    print(f'📁 Parent: {parent_category.name}')
    print(f'   URL: {parent_category.get_absolute_url()}')
    
    children = parent_category.get_children()
    print(f'\n👶 Child categories ({children.count()}):')
    
    for child in children:
        products = Product.objects.filter(categories=child)
        print(f'  📂 {child.slug}')
        print(f'     Name: {child.name}')
        print(f'     Products: {products.count()}')
        print(f'     URL: {child.get_absolute_url()}')
        
        if products.exists():
            print(f'     Sample product: {products.first().title}')
        print()

# Let's also check what products exist and their callout data
print('\n🔍 Checking products with callout data:')
all_products = Product.objects.filter(categories__in=parent_category.get_descendants())

for product in all_products:
    try:
        callout_attr = product.attribute_values.filter(attribute__name='call_out_number').first()
        callout = callout_attr.value if callout_attr else 'No callout'
        category_names = [cat.name for cat in product.categories.all()]
        print(f'  Product: {product.title}')
        print(f'    Callout: {callout}')
        print(f'    Categories: {category_names}')
        print()
    except Exception as e:
        print(f'  Error reading product {product.title}: {e}')