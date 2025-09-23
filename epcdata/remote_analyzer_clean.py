#!/usr/bin/env python
"""
REMOTE Production Database Connection Script

This script connects directly to the remote production database
and analyzes the actual problem.
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


class RemoteProductionAnalyzer:
    def __init__(self):
        pass
        
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
    
    def analyze_specific_url_category(self):
        """Analyze the specific category that should have products"""
        print("\\n🎯 ANALYZING SPECIFIC URL CATEGORY...")
        print("="*60)
        
        # The URL pattern suggests looking for parent-12, child-1
        serial = 'LSFAL11A4PA157987'
        target_patterns = [
            f'serial-{serial}-parent-12-child-1',
            f'serial-{serial}-parent-2-child-1'
        ]
        
        for pattern in target_patterns:
            print(f"\\n🔍 Searching for: {pattern}")
            categories = Category.objects.filter(slug__icontains=pattern)
            
            print(f"Found {len(categories)} categories:")
            
            for cat in categories:
                products = cat.product_set.all()
                print(f"\\n📁 {cat.name}")
                print(f"   Slug: {cat.slug}")
                print(f"   ID: {cat.id}")
                print(f"   Products: {products.count()}")
                
                if products.exists():
                    print("   Products in this category:")
                    for product in products[:5]:  # Show first 5
                        print(f"     • {product.title}")
                    if products.count() > 5:
                        print(f"     ... and {products.count() - 5} more")
                else:
                    print("   ❌ NO PRODUCTS IN THIS CATEGORY")
    
    def find_all_energy_products_for_serial(self):
        """Find ALL products that might be energy storage related"""
        print("\\n⚡ FINDING ALL ENERGY STORAGE PRODUCTS...")
        print("="*60)
        
        serial = 'LSFAL11A4PA157987'
        
        # Search for products with energy-related keywords
        energy_keywords = [
            'BATTERY', 'ENERGY', 'POWER', 'ELECTRICAL',
            'TRAY ASSEMBLY', 'INTELLIGENT', 'BOARD'
        ]
        
        all_energy_products = []
        
        # Get all categories for this serial
        categories = Category.objects.filter(slug__icontains=f'serial-{serial}')
        print(f"Scanning {len(categories)} categories for {serial}...")
        
        for cat in categories:
            products = cat.product_set.all()
            
            for product in products:
                title_upper = product.title.upper()
                
                # Check if this is an energy storage product
                matched_keywords = []
                for keyword in energy_keywords:
                    if keyword in title_upper:
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    # Extract parent number
                    parent_num = 'unknown'
                    slug_parts = cat.slug.split('-')
                    for i, part in enumerate(slug_parts):
                        if part == 'parent' and i + 1 < len(slug_parts):
                            parent_num = slug_parts[i + 1]
                            break
                    
                    all_energy_products.append({
                        'title': product.title,
                        'category_name': cat.name,
                        'category_slug': cat.slug,
                        'parent_number': parent_num,
                        'keywords': matched_keywords
                    })
        
        print(f"\\n📊 FOUND {len(all_energy_products)} ENERGY STORAGE PRODUCTS:")
        
        # Group by parent
        by_parent = defaultdict(list)
        for item in all_energy_products:
            by_parent[item['parent_number']].append(item)
        
        for parent_num in sorted(by_parent.keys()):
            items = by_parent[parent_num]
            print(f"\\n🏷️  Parent-{parent_num}: {len(items)} products")
            
            for item in items:
                print(f"   • {item['title']}")
                print(f"     Category: {item['category_name']}")
                print(f"     Keywords: {', '.join(item['keywords'])}")
        
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
        
        # Step 2: Analyze the specific URL category
        self.analyze_specific_url_category()
        
        # Step 3: Find all energy storage products
        self.find_all_energy_products_for_serial()
        
        print("\\n✅ Analysis complete!")
        return True


if __name__ == "__main__":
    analyzer = RemoteProductionAnalyzer()
    analyzer.run()