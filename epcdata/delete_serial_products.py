import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from oscar.apps.partner.models import StockRecord

def delete_serial_products(serial_slug):
    """
    Safely delete all products associated with a specific serial
    """
    print(f'🗑️ Starting deletion process for serial: {serial_slug}')
    
    # Find the serial category
    serial_category = Category.objects.filter(slug=serial_slug).first()
    if not serial_category:
        print(f'❌ Serial category not found: {serial_slug}')
        return
    
    print(f'✅ Found serial category: {serial_category.name}')
    
    # Get all descendant categories (parents and children)
    all_categories = serial_category.get_descendants(include_self=True)
    print(f'📁 Found {all_categories.count()} categories in this serial')
    
    # Count products before deletion
    total_products = 0
    total_stock_records = 0
    
    for category in all_categories:
        products = Product.objects.filter(categories=category)
        product_count = products.count()
        total_products += product_count
        
        if product_count > 0:
            print(f'  📂 {category.slug}: {product_count} products')
            
            # Count stock records for these products
            for product in products:
                stock_count = StockRecord.objects.filter(product=product).count()
                total_stock_records += stock_count
    
    print(f'\n📊 DELETION SUMMARY:')
    print(f'   Total products to delete: {total_products}')
    print(f'   Total stock records to delete: {total_stock_records}')
    
    if total_products == 0:
        print('✅ No products to delete!')
        return
    
    # Confirm deletion
    confirmation = input(f'\n⚠️  Are you sure you want to delete {total_products} products? (yes/no): ')
    if confirmation.lower() != 'yes':
        print('❌ Deletion cancelled')
        return
    
    # Delete products and stock records
    deleted_products = 0
    deleted_stock_records = 0
    
    for category in all_categories:
        products = Product.objects.filter(categories=category)
        
        for product in products:
            # Delete stock records first
            stock_records = StockRecord.objects.filter(product=product)
            stock_count = stock_records.count()
            stock_records.delete()
            deleted_stock_records += stock_count
            
            # Delete the product
            product.delete()
            deleted_products += 1
            
            if deleted_products % 100 == 0:
                print(f'   Deleted {deleted_products} products...')
    
    print(f'\n✅ DELETION COMPLETE:')
    print(f'   Products deleted: {deleted_products}')
    print(f'   Stock records deleted: {deleted_stock_records}')
    print(f'\n🔄 Ready for fresh scraping and import!')

if __name__ == '__main__':
    # Delete all products for LSFAL11A4PA157987 serial
    delete_serial_products('serial-lsfal11a4pa157987')