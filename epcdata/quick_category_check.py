import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product

print('🔍 Checking category fix results...')

# Check the specific child category from the URL
child_slug = 'serial-LSFAL11A4PA157987-parent-12-child-1_40'
child_category = Category.objects.filter(slug=child_slug).first()

if child_category:
    products = Product.objects.filter(categories=child_category)
    print(f'✅ Child category found: {child_category.name}')
    print(f'Products in child category: {products.count()}')
    if products.exists():
        print('Sample products in child:')
        for p in products[:3]:
            print(f'  - {p.title}')
else:
    print(f'❌ Child category not found: {child_slug}')

# Check the parent category
parent_slug = 'serial-LSFAL11A4PA157987-parent-12'
parent_category = Category.objects.filter(slug=parent_slug).first()

if parent_category:
    parent_products = Product.objects.filter(categories=parent_category)
    print(f'📁 Parent category: {parent_category.name}')
    print(f'Products in parent: {parent_products.count()}')
    
    children = parent_category.get_children()
    print(f'Child categories: {children.count()}')
    
    total_in_children = 0
    for child in children:
        child_products = Product.objects.filter(categories=child)
        total_in_children += child_products.count()
        print(f'  {child.slug}: {child_products.count()} products')
    
    print(f'Total products in children: {total_in_children}')
    
    if parent_products.count() > 0:
        print('⚠️ Products still in parent (should be in children):')
        for p in parent_products[:3]:
            print(f'  - {p.title}')
else:
    print(f'❌ Parent category not found: {parent_slug}')