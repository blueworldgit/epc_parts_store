#!/usr/bin/env python
"""
REMOTE Production Database Connection Script

This script connects directly to the remote production database
and fixes misplaced products.
"""

import os
import sys
import django
from collections import defaultdict
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment with REMOTE production database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Override database settings for remote connection
os.environ['DB_HOST'] = '80.95.207.42'  # Your production server IP
os.environ['DB_NAME'] = 'parts_store'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'N0rwich!'
os.environ['DB_PORT'] = '5432'

django.setup()

from oscar.apps.catalogue.models import Category, Product
from django.db import transaction, connection
from django.conf import settings


class RemoteProductionFixer:
    def __init__(self):
        self.backup_file = f"remote_production_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def test_connection(self):
        """Test connection to remote production database"""
        print("🔌 TESTING REMOTE PRODUCTION DATABASE CONNECTION...")
        print("="*60)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"✅ Connected to PostgreSQL: {version}")
                
                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()[0]
                print(f"✅ Database: {db_name}")
                
                cursor.execute("SELECT count(*) FROM oscar_catalogue_category;")
                cat_count = cursor.fetchone()[0]
                print(f"✅ Categories found: {cat_count}")
                
                cursor.execute("SELECT count(*) FROM oscar_catalogue_product;")
                prod_count = cursor.fetchone()[0]
                print(f"✅ Products found: {prod_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_energy_storage_problem(self):
        """Analyze the specific energy storage URL problem"""
        print("\n🎯 ANALYZING ENERGY STORAGE URL PROBLEM...")
        print("="*60)
        
        serial = 'LSFAL11A4PA157987'
        
        # Check the specific URL pattern the user mentioned
        # http://127.0.0.1:8000/catalogue/category/maxus/serial-lsfal11a4pa157987/serial-LSFAL11A4PA157987-parent-12/serial-LSFAL11A4PA157987-parent-12-child-1_40/
        
        target_slug_pattern = f'serial-{serial}-parent-12-child-1'
        
        print(f"🔍 Looking for categories matching: {target_slug_pattern}")
        
        # Find categories that match this pattern
        matching_categories = Category.objects.filter(slug__contains=target_slug_pattern)
        
        print(f"Found {len(matching_categories)} matching categories:")
        
        for cat in matching_categories:
            products = cat.product_set.all()
            print(f"\n📁 Category: {cat.name}")
            print(f"   Slug: {cat.slug}")
            print(f"   Products: {products.count()}")
            
            if products.count() > 0:
                print("   Product list:")
                for product in products:
                    print(f"     • {product.title}")
            else:
                print("   ❌ NO PRODUCTS FOUND")
        
        # Also check what's in parent-2 categories for this serial
        print(f"\n🔍 Checking what's in Parent-2 categories for {serial}...")
        parent2_categories = Category.objects.filter(
            slug__contains=f'serial-{serial}',
            slug__contains='-parent-2-'
        )
        
        print(f"Found {len(parent2_categories)} Parent-2 categories:")
        
        total_parent2_products = 0
        for cat in parent2_categories:
            products = cat.product_set.all()
            total_parent2_products += products.count()
            print(f"\n📁 {cat.name} ({cat.slug})")
            print(f"   Products: {products.count()}")
            
            # Look for energy storage products specifically
            energy_products = []
            for product in products:
                title_upper = product.title.upper()
                if any(keyword in title_upper for keyword in ['BATTERY', 'ENERGY', 'POWER', 'ELECTRICAL']):
                    energy_products.append(product)
            
            if energy_products:
                print(f"   Energy Storage Products ({len(energy_products)}):")
                for product in energy_products:
                    print(f"     ⚡ {product.title}")
            else:
                print("   No energy storage products found")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total products in Parent-2: {total_parent2_products}")
        
        return matching_categories
    
    def find_all_energy_storage_products(self):
        """Find ALL energy storage products for this serial regardless of location"""
        print(f"\n🔍 FINDING ALL ENERGY STORAGE PRODUCTS FOR LSFAL11A4PA157987...")
        print("="*60)
        
        serial = 'LSFAL11A4PA157987'
        
        # Get all categories for this serial
        all_categories = Category.objects.filter(slug__contains=f'serial-{serial}')
        
        energy_keywords = ['BATTERY', 'ENERGY', 'POWER', 'ELECTRICAL', 'TRAY ASSEMBLY', 'INTELLIGENT', 'BOARD']
        
        all_energy_products = []
        
        for cat in all_categories:
            products = cat.product_set.all()
            
            for product in products:
                title_upper = product.title.upper()
                
                # Check if this looks like an energy storage product
                for keyword in energy_keywords:
                    if keyword in title_upper:
                        # Extract parent number from slug
                        parent_num = None
                        slug_parts = cat.slug.split('-')
                        for i, part in enumerate(slug_parts):
                            if part == 'parent' and i + 1 < len(slug_parts):
                                parent_num = slug_parts[i + 1]
                                break
                        
                        all_energy_products.append({
                            'product': product,
                            'category': cat,
                            'parent_number': parent_num,
                            'keyword_matched': keyword
                        })
                        
                        print(f"⚡ FOUND: {product.title}")
                        print(f"   In: {cat.name} (Parent-{parent_num})")
                        print(f"   Slug: {cat.slug}")
                        break
        
        print(f"\n📊 TOTAL ENERGY STORAGE PRODUCTS FOUND: {len(all_energy_products)}")
        
        # Group by parent
        by_parent = defaultdict(list)
        for item in all_energy_products:
            by_parent[item['parent_number']].append(item)
        
        print("\n📋 BY PARENT CATEGORY:")
        for parent_num, items in sorted(by_parent.items()):
            print(f"  Parent-{parent_num}: {len(items)} products")
            for item in items[:3]:  # Show first 3
                print(f"    • {item['product'].title}")
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more")
        
        return all_energy_products
    
    def run(self):
        """Main execution method"""
        print("🌐 REMOTE PRODUCTION DATABASE ANALYZER")
        print("="*60)
        print(f"🎯 Target: {os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}")
        print(f"🗄️ Database: {os.environ.get('DB_NAME')}")
        print()
        
        # Step 1: Test connection
        if not self.test_connection():
            print("❌ Cannot connect to remote database!")
            return False
        
        # Step 2: Analyze the specific problem
        matching_cats = self.analyze_energy_storage_problem()
        
        # Step 3: Find ALL energy storage products
        all_energy_products = self.find_all_energy_storage_products()
        
        return True


if __name__ == "__main__":
    fixer = RemoteProductionFixer()
    fixer.run()