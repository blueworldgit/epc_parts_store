#!/usr/bin/env python
"""
PRODUCTION-SAFE Serial Data Cleanup Script

This script removes all categories and products for serial LSFAL11A4PA157987
while preserving the serial brand itself for fresh reimport.
"""

import psycopg2
import json
from datetime import datetime

class SerialCleanupManager:
    def __init__(self):
        self.serial = 'LSFAL11A4PA157987'
        self.backup_file = f"serial_cleanup_backup_{self.serial}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Production database connection
        self.db_config = {
            'host': '80.95.207.42',
            'database': 'parts_store',
            'user': 'postgres',
            'password': 'N0rwich!',
            'port': 5432
        }
        self.conn = None
    
    def connect(self):
        """Connect to production database"""
        print("🔌 CONNECTING TO PRODUCTION DATABASE...")
        print("="*60)
        print(f"🎯 Host: {self.db_config['host']}")
        print(f"🗄️ Database: {self.db_config['database']}")
        
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_current_data(self):
        """Analyze what data exists for this serial"""
        print(f"\\n🔍 ANALYZING CURRENT DATA FOR {self.serial}")
        print("="*60)
        
        cursor = self.conn.cursor()
        
        # Count categories
        cursor.execute("""
            SELECT COUNT(*) FROM catalogue_category 
            WHERE slug LIKE %s
        """, (f'%{self.serial}%',))
        
        category_count = cursor.fetchone()[0]
        print(f"📁 Categories found: {category_count}")
        
        # Count products in these categories
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id)
            FROM catalogue_product p
            JOIN catalogue_productcategory pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
        """, (f'%{self.serial}%',))
        
        product_count = cursor.fetchone()[0]
        print(f"📦 Products found: {product_count}")
        
        # Find the brand/serial record itself
        cursor.execute("""
            SELECT id, name, slug, path, depth
            FROM catalogue_category 
            WHERE slug = %s
        """, (f'serial-{self.serial}',))
        
        brand_record = cursor.fetchone()
        if brand_record:
            print(f"\\n🏷️  BRAND RECORD FOUND:")
            print(f"   ID: {brand_record[0]}")
            print(f"   Name: {brand_record[1]}")
            print(f"   Slug: {brand_record[2]}")
            print(f"   Path: {brand_record[3]}")
            print(f"   Depth: {brand_record[4]}")
        else:
            print(f"\\n❌ Brand record not found for serial-{self.serial}")
        
        cursor.close()
        
        return {
            'categories': category_count,
            'products': product_count,
            'brand_record': brand_record
        }
    
    def create_backup(self):
        """Create comprehensive backup of all data"""
        print(f"\\n💾 CREATING BACKUP...")
        print("="*60)
        
        cursor = self.conn.cursor()
        backup_data = {
            'serial': self.serial,
            'timestamp': datetime.now().isoformat(),
            'categories': [],
            'products': [],
            'product_categories': []
        }
        
        # Backup categories
        cursor.execute("""
            SELECT id, name, slug, path, depth, description, image, numchild
            FROM catalogue_category 
            WHERE slug LIKE %s
            ORDER BY depth, slug
        """, (f'%{self.serial}%',))
        
        categories = cursor.fetchall()
        for cat in categories:
            backup_data['categories'].append({
                'id': cat[0],
                'name': cat[1],
                'slug': cat[2],
                'path': cat[3],
                'depth': cat[4],
                'description': cat[5],
                'image': cat[6],
                'numchild': cat[7]
            })
        
        print(f"✅ Backed up {len(categories)} categories")
        
        # Backup products in these categories
        cursor.execute("""
            SELECT DISTINCT p.id, p.structure, p.title, p.slug, p.description, 
                   p.meta_title, p.meta_description, p.is_public,
                   p.is_discountable, p.date_created, p.date_updated
            FROM catalogue_product p
            JOIN catalogue_productcategory pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
        """, (f'%{self.serial}%',))
        
        products = cursor.fetchall()
        for prod in products:
            backup_data['products'].append({
                'id': prod[0],
                'structure': prod[1],
                'title': prod[2],
                'slug': prod[3],
                'description': prod[4],
                'meta_title': prod[5],
                'meta_description': prod[6],
                'is_public': prod[7],
                'is_discountable': prod[8],
                'date_created': prod[9].isoformat() if prod[9] else None,
                'date_updated': prod[10].isoformat() if prod[10] else None
            })
        
        print(f"✅ Backed up {len(products)} products")
        
        # Backup product-category relationships
        cursor.execute("""
            SELECT pc.product_id, pc.category_id
            FROM catalogue_productcategory pc
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
        """, (f'%{self.serial}%',))
        
        relationships = cursor.fetchall()
        for rel in relationships:
            backup_data['product_categories'].append({
                'product_id': rel[0],
                'category_id': rel[1]
            })
        
        print(f"✅ Backed up {len(relationships)} product-category relationships")
        
        # Save backup to file
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"📁 Backup saved to: {self.backup_file}")
        
        cursor.close()
        return backup_data
    
    def cleanup_data(self, preserve_brand=True):
        """Remove all data for this serial except the brand record"""
        print(f"\\n🧹 CLEANING UP DATA FOR {self.serial}")
        print("="*60)
        
        cursor = self.conn.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN;")
            
            # Step 1: Get all product IDs to be deleted first
            cursor.execute("""
                SELECT DISTINCT p.id 
                FROM catalogue_product p
                JOIN catalogue_productcategory pc ON p.id = pc.product_id
                JOIN catalogue_category c ON pc.category_id = c.id
                WHERE c.slug LIKE %s
            """, (f'%{self.serial}%',))
            
            product_ids = [row[0] for row in cursor.fetchall()]
            print(f"📋 Found {len(product_ids)} products to delete")
            
            if not product_ids:
                print("✅ No products to delete")
                return True
            
            # Convert to tuple for SQL IN clause
            product_ids_tuple = tuple(product_ids)
            
            # Step 2: Remove basket lines that reference these stock records
            cursor.execute("""
                DELETE FROM basket_line 
                WHERE stockrecord_id IN (
                    SELECT id FROM partner_stockrecord 
                    WHERE product_id = ANY(%s)
                )
            """, (product_ids,))
            
            basket_count = cursor.rowcount
            print(f"✅ Removed {basket_count} basket lines")
            
            # Step 3: Remove partner stock records
            cursor.execute("""
                DELETE FROM partner_stockrecord 
                WHERE product_id = ANY(%s)
            """, (product_ids,))
            
            stock_count = cursor.rowcount
            print(f"✅ Removed {stock_count} stock records")
            
            # Step 4: Remove analytics product records
            cursor.execute("""
                DELETE FROM analytics_productrecord 
                WHERE product_id = ANY(%s)
            """, (product_ids,))
            
            analytics_count = cursor.rowcount
            print(f"✅ Removed {analytics_count} analytics records")
            
            # Step 5: Remove product attribute values
            cursor.execute("""
                DELETE FROM catalogue_productattributevalue 
                WHERE product_id = ANY(%s)
            """, (product_ids,))
            
            attribute_count = cursor.rowcount
            print(f"✅ Removed {attribute_count} product attribute values")
            
            # Step 6: Remove ALL product-category relationships for these products
            cursor.execute("""
                DELETE FROM catalogue_productcategory 
                WHERE product_id = ANY(%s)
            """, (product_ids,))
            
            relationship_count = cursor.rowcount
            print(f"✅ Removed {relationship_count} product-category relationships")
            
            # Step 7: Remove products
            cursor.execute("""
                DELETE FROM catalogue_product 
                WHERE id = ANY(%s)
            """, (product_ids,))
            
            product_count = cursor.rowcount
            print(f"✅ Removed {product_count} products")
            
            # Step 8: Remove categories (except brand record if preserve_brand=True)
            if preserve_brand:
                cursor.execute("""
                    DELETE FROM catalogue_category 
                    WHERE slug LIKE %s AND slug != %s
                """, (f'%{self.serial}%', f'serial-{self.serial}'))
            else:
                cursor.execute("""
                    DELETE FROM catalogue_category 
                    WHERE slug LIKE %s
                """, (f'%{self.serial}%',))
            
            category_count = cursor.rowcount
            print(f"✅ Removed {category_count} categories")
            
            if preserve_brand:
                print(f"✅ Preserved brand record: serial-{self.serial}")
            
            # Commit transaction
            cursor.execute("COMMIT;")
            
            print(f"\\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
            print(f"   📁 Categories removed: {category_count}")
            print(f"   📦 Products removed: {product_count}")
            print(f"   🔗 Relationships removed: {relationship_count}")
            print(f"   🏷️  Attributes removed: {attribute_count}")
            print(f"   📊 Analytics removed: {analytics_count}")
            print(f"   📦 Stock records removed: {stock_count}")
            print(f"   🛒 Basket lines removed: {basket_count}")
            
            return True
            
        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK;")
            print(f"❌ Cleanup failed: {e}")
            print("🔄 All changes have been rolled back")
            return False
        
        finally:
            cursor.close()
    
    def verify_cleanup(self):
        """Verify the cleanup was successful"""
        print(f"\\n✅ VERIFYING CLEANUP...")
        print("="*60)
        
        cursor = self.conn.cursor()
        
        # Check remaining categories
        cursor.execute("""
            SELECT COUNT(*) FROM catalogue_category 
            WHERE slug LIKE %s
        """, (f'%{self.serial}%',))
        
        remaining_categories = cursor.fetchone()[0]
        print(f"📁 Remaining categories: {remaining_categories}")
        
        # Check remaining products
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id)
            FROM catalogue_product p
            JOIN catalogue_productcategory pc ON p.id = pc.product_id
            JOIN catalogue_category c ON pc.category_id = c.id
            WHERE c.slug LIKE %s
        """, (f'%{self.serial}%',))
        
        remaining_products = cursor.fetchone()[0]
        print(f"📦 Remaining products: {remaining_products}")
        
        # Check if brand record exists
        cursor.execute("""
            SELECT name FROM catalogue_category 
            WHERE slug = %s
        """, (f'serial-{self.serial}',))
        
        brand_record = cursor.fetchone()
        if brand_record:
            print(f"✅ Brand record preserved: {brand_record[0]}")
        else:
            print(f"❌ Brand record missing!")
        
        cursor.close()
        
        return {
            'categories': remaining_categories,
            'products': remaining_products,
            'brand_preserved': brand_record is not None
        }
    
    def get_user_confirmation(self, analysis):
        """Get user confirmation for the cleanup"""
        print("\\n" + "="*60)
        print("⚠️  PRODUCTION DATA CLEANUP CONFIRMATION")
        print("="*60)
        print("🚨 PRODUCTION DATABASE - PROCEED WITH EXTREME CAUTION!")
        print()
        print(f"📊 Data to be removed for serial {self.serial}:")
        print(f"   • {analysis['categories']} categories")
        print(f"   • {analysis['products']} products")
        print(f"   • All product-category relationships")
        print()
        print(f"✅ Will preserve: Brand record 'Maxus Deliver 9 RWD LUX'")
        print(f"📁 Backup will be saved to: {self.backup_file}")
        print()
        print("This will prepare for fresh import of clean data.")
        
        while True:
            response = input("Type 'y' to proceed, or 'n' to abort: ").strip().lower()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            print("Invalid response. Please type 'y' or 'n'.")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\\n🔌 Database connection closed.")
    
    def run(self):
        """Main execution method"""
        print("🧹 PRODUCTION SERIAL DATA CLEANUP MANAGER")
        print("="*60)
        print(f"🎯 Target Serial: {self.serial}")
        print(f"🏷️  Will preserve: Maxus Deliver 9 RWD LUX brand record")
        print()
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        try:
            # Step 2: Analyze current data
            analysis = self.analyze_current_data()
            
            if analysis['categories'] == 0:
                print("✅ No data found to clean up!")
                return True
            
            # Step 3: Get user confirmation
            if not self.get_user_confirmation(analysis):
                print("❌ Operation cancelled by user.")
                return False
            
            # Step 4: Create backup
            backup_data = self.create_backup()
            
            # Step 5: Cleanup data
            success = self.cleanup_data(preserve_brand=True)
            
            if success:
                # Step 6: Verify cleanup
                verification = self.verify_cleanup()
                
                print(f"\\n🎉 SERIAL CLEANUP COMPLETED!")
                print(f"✅ Ready for fresh import of {self.serial} data")
                print(f"📁 Backup available: {self.backup_file}")
                
                return True
            else:
                return False
            
        finally:
            self.close()


if __name__ == "__main__":
    cleanup = SerialCleanupManager()
    success = cleanup.run()
    
    if success:
        print("\\n🚀 Next steps:")
        print("1. Run your import command for LSFAL11A4PA157987")
        print("2. Test the problematic URLs")
        print("3. Verify all products are in correct categories")
    else:
        print("\\n⚠️ Cleanup failed or was cancelled.")