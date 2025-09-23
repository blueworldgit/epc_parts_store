#!/usr/bin/env python
"""
Verify Complete Serial Data Removal

Check both Django models (motorpartsdata) AND Oscar catalogue 
to confirm LSFAL11A4PA157987 is completely clean for fresh import.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import SerialNumber, ParentTitle, ChildTitle, Part
from oscar.apps.catalogue.models import Category, Product
import psycopg2

def check_django_models():
    """Check Django motorpartsdata models"""
    print("🔍 CHECKING DJANGO MODELS (motorpartsdata)")
    print("="*50)
    
    serial = 'LSFAL11A4PA157987'
    
    # Check SerialNumber
    serial_obj = SerialNumber.objects.filter(serial=serial).first()
    if serial_obj:
        print(f"📋 SerialNumber found: {serial_obj.serial} - {serial_obj.vehicle_brand}")
        
        # Check ParentTitles
        parents = ParentTitle.objects.filter(serial_number=serial_obj)
        print(f"📁 ParentTitles: {parents.count()}")
        
        if parents.count() > 0:
            print("   Sample parents:")
            for parent in parents[:5]:
                print(f"     • {parent.title}")
            if parents.count() > 5:
                print(f"     ... and {parents.count() - 5} more")
        
        # Check ChildTitles
        child_count = 0
        part_count = 0
        for parent in parents:
            children = ChildTitle.objects.filter(parent=parent)
            child_count += children.count()
            
            for child in children:
                parts = Part.objects.filter(child_title=child)
                part_count += parts.count()
        
        print(f"📂 ChildTitles: {child_count}")
        print(f"🔧 Parts: {part_count}")
        
        return {
            'serial_exists': True,
            'parents': parents.count(),
            'children': child_count,
            'parts': part_count
        }
    else:
        print(f"✅ No SerialNumber found for {serial}")
        return {
            'serial_exists': False,
            'parents': 0,
            'children': 0,
            'parts': 0
        }

def check_oscar_catalogue():
    """Check Oscar catalogue models"""
    print("\\n🔍 CHECKING OSCAR CATALOGUE")
    print("="*50)
    
    serial = 'LSFAL11A4PA157987'
    
    # Check categories
    categories = Category.objects.filter(slug__contains=serial)
    print(f"📁 Oscar Categories: {categories.count()}")
    
    if categories.count() > 0:
        print("   Categories found:")
        for cat in categories[:5]:
            product_count = cat.product_set.count()
            print(f"     • {cat.name} ({cat.slug}) - {product_count} products")
        if categories.count() > 5:
            print(f"     ... and {categories.count() - 5} more")
    
    # Check products in these categories
    product_count = 0
    for cat in categories:
        product_count += cat.product_set.count()
    
    print(f"📦 Oscar Products: {product_count}")
    
    return {
        'categories': categories.count(),
        'products': product_count
    }

def check_production_database():
    """Double-check production database directly"""
    print("\\n🔍 CHECKING PRODUCTION DATABASE DIRECTLY")
    print("="*50)
    
    try:
        conn = psycopg2.connect(
            host='80.95.207.42',
            database='parts_store',
            user='postgres',
            password='N0rwich!',
            port=5432
        )
        
        cursor = conn.cursor()
        serial = 'LSFAL11A4PA157987'
        
        # Check Django models tables
        cursor.execute("SELECT COUNT(*) FROM motorpartsdata_serialnumber WHERE serial = %s", (serial,))
        django_serial_count = cursor.fetchone()[0]
        print(f"📋 Django SerialNumber records: {django_serial_count}")
        
        if django_serial_count > 0:
            cursor.execute("""
                SELECT COUNT(*) FROM motorpartsdata_parenttitle pt
                JOIN motorpartsdata_serialnumber sn ON pt.serial_number_id = sn.id
                WHERE sn.serial = %s
            """, (serial,))
            django_parent_count = cursor.fetchone()[0]
            print(f"📁 Django ParentTitle records: {django_parent_count}")
            
            cursor.execute("""
                SELECT COUNT(*) FROM motorpartsdata_childtitle ct
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                JOIN motorpartsdata_serialnumber sn ON pt.serial_number_id = sn.id
                WHERE sn.serial = %s
            """, (serial,))
            django_child_count = cursor.fetchone()[0]
            print(f"📂 Django ChildTitle records: {django_child_count}")
            
            cursor.execute("""
                SELECT COUNT(*) FROM motorpartsdata_part p
                JOIN motorpartsdata_childtitle ct ON p.child_title_id = ct.id
                JOIN motorpartsdata_parenttitle pt ON ct.parent_id = pt.id
                JOIN motorpartsdata_serialnumber sn ON pt.serial_number_id = sn.id
                WHERE sn.serial = %s
            """, (serial,))
            django_part_count = cursor.fetchone()[0]
            print(f"🔧 Django Part records: {django_part_count}")
        
        # Check Oscar tables
        cursor.execute("SELECT COUNT(*) FROM catalogue_category WHERE slug LIKE %s", (f'%{serial}%',))
        oscar_cat_count = cursor.fetchone()[0]
        print(f"📁 Oscar Category records: {oscar_cat_count}")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id)
            FROM catalogue_product p
            JOIN catalogue_productcategory pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
        """, (f'%{serial}%',))
        oscar_prod_count = cursor.fetchone()[0]
        print(f"📦 Oscar Product records: {oscar_prod_count}")
        
        cursor.close()
        conn.close()
        
        return {
            'django_serial': django_serial_count,
            'django_parents': django_parent_count if django_serial_count > 0 else 0,
            'django_children': django_child_count if django_serial_count > 0 else 0,
            'django_parts': django_part_count if django_serial_count > 0 else 0,
            'oscar_categories': oscar_cat_count,
            'oscar_products': oscar_prod_count
        }
        
    except Exception as e:
        print(f"❌ Error checking production database: {e}")
        return None

def main():
    print("🧹 COMPLETE SERIAL DATA VERIFICATION")
    print("="*60)
    print("Checking both Django models AND Oscar catalogue for LSFAL11A4PA157987")
    print()
    
    # Check Django models (via ORM)
    django_results = check_django_models()
    
    # Check Oscar catalogue (via ORM)
    oscar_results = check_oscar_catalogue()
    
    # Double-check via direct database queries
    db_results = check_production_database()
    
    # Summary
    print("\\n📊 COMPLETE VERIFICATION SUMMARY")
    print("="*60)
    
    django_total = (django_results['parents'] + django_results['children'] + 
                   django_results['parts'] if django_results['serial_exists'] else 0)
    oscar_total = oscar_results['categories'] + oscar_results['products']
    
    print(f"🔧 Django Models Total Records: {django_total}")
    print(f"🛒 Oscar Catalogue Total Records: {oscar_total}")
    
    if django_total == 0 and oscar_total == 0:
        print("\\n✅ COMPLETE CLEANUP CONFIRMED!")
        print("   🎉 Both Django models AND Oscar catalogue are clean")
        print("   🚀 Ready for fresh import process:")
        print("      1. scrapeandpush.py → Django models")
        print("      2. manage.py import_to_oscar → Oscar catalogue")
    else:
        print("\\n⚠️  DATA STILL EXISTS!")
        if django_total > 0:
            print(f"   🔧 Django models need cleanup: {django_total} records")
        if oscar_total > 0:
            print(f"   🛒 Oscar catalogue need cleanup: {oscar_total} records")
    
    if db_results:
        print(f"\\n🔍 Production DB Direct Check:")
        print(f"   Django: {db_results.get('django_serial', 0)} serials")
        print(f"   Oscar: {db_results.get('oscar_categories', 0)} categories")

if __name__ == "__main__":
    main()