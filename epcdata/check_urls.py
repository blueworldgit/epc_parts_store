import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

print('🔍 Checking actual child category slugs and URLs...')

# Check parent 12 specifically
parent_slug = 'serial-LSFAL11A4PA157987-parent-12'
parent_category = Category.objects.filter(slug=parent_slug).first()

if parent_category:
    print(f'📁 Parent category: {parent_category.name}')
    print(f'   Full path: {parent_category.get_absolute_url()}')
    
    children = parent_category.get_children()
    print(f'\nChild categories ({children.count()}):')
    
    for child in children:
        print(f'  📂 {child.slug}')
        print(f'     Name: {child.name}')
        print(f'     URL: {child.get_absolute_url()}')
        print()
        
else:
    print('❌ Parent category not found')

# Also check what the user is trying to access vs what exists
requested_slug = 'serial-LSFAL11A4PA157987-parent-12-child-1_40'
actual_child_1 = Category.objects.filter(slug='serial-LSFAL11A4PA157987-parent-12-child-1').first()

print(f'User requesting URL with slug: {requested_slug}')
if actual_child_1:
    print(f'Actual child-1 URL: {actual_child_1.get_absolute_url()}')
    print(f'Difference: user has "_40" suffix, actual category does not')
else:
    print('Child-1 category not found')