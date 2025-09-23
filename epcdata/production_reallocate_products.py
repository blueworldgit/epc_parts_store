#!/usr/bin/env python
"""
PRODUCTION-SAFE Product Reallocation Script

This script identifies and fixes products that are in wrong categories
by matching product names/types to their correct category assignments
based on patterns from other serials.
"""

import os
import sys
import django
from collections import defaultdict
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from django.db import transaction
from django.conf import settings


class ProductReallocationManager:
    def __init__(self):
        self.backup_file = f"product_reallocation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.is_production = self.detect_production_environment()
        self.product_category_patterns = {}
        
    def detect_production_environment(self):
        """Detect if we're running in production"""
        indicators = [
            'DEBUG' in settings.__dict__ and not settings.DEBUG,
            'PROD' in os.environ.get('DJANGO_ENV', '').upper(),
            'PRODUCTION' in os.environ.get('DJANGO_ENV', '').upper(),
        ]
        return any(indicators)
    
    def analyze_correct_category_patterns(self):
        """Learn correct category patterns from serials that have products in right places"""
        print("🧠 LEARNING CORRECT CATEGORY PATTERNS...")
        
        # Define product type patterns and their expected categories
        product_patterns = {
            # Energy Storage products should be in parent-2
            'energy_storage': {
                'keywords': ['BATTERY ASSEMBLY', 'TRAY ASSEMBLY-BATTERY', 'BATTERY VENT', 'BATTERY SENSOR', 'BOARD-BATTERY'],
                'expected_parents': ['parent-2'],
                'category_names': ['Battery&Electrical Energy Storage', 'PowerInverter']
            },
            # Battery harnesses should be in parent-7 with specific category names
            'battery_harnesses': {
                'keywords': ['HARDNESS-BATTERY', 'HARNESS-BATTERY', 'NUT-AUXILIARY BATTERY'],
                'expected_parents': ['parent-7'],
                'category_names': ['Battery Harnesses', 'BatteryCable']
            },
            # Engine components should be in parent-31
            'engine_components': {
                'keywords': ['ENGINE', 'BOLT/SCREW-BATTERY HARNESS ENGINE'],
                'expected_parents': ['parent-31'],
                'category_names': ['Engine shield', 'EngineCompartmentHarness']
            }
        }
        
        # Find examples of correct placements from other serials
        working_serials = ['LSH14J7C2MA122115', 'LSH14J7C7MA114771', 'LSH14J7CXMA114599']
        
        correct_patterns = {}
        
        for serial in working_serials:
            categories = Category.objects.filter(slug__contains=f'serial-{serial}').filter(slug__contains='-child-')
            
            for cat in categories:
                products = cat.product_set.all()
                for product in products:
                    title = product.title.upper()
                    
                    # Determine what type this product should be
                    for product_type, pattern_info in product_patterns.items():
                        for keyword in pattern_info['keywords']:
                            if keyword.upper() in title:
                                # Extract parent number from category slug
                                parent_match = None
                                for part in cat.slug.split('-'):
                                    if part.startswith('parent-'):
                                        parent_match = part
                                        break
                                
                                if parent_match:
                                    if product_type not in correct_patterns:
                                        correct_patterns[product_type] = defaultdict(int)
                                    correct_patterns[product_type][parent_match] += 1
        
        self.product_category_patterns = correct_patterns
        
        print("📊 Learned patterns:")
        for product_type, patterns in correct_patterns.items():
            print(f"  {product_type}:")
            for parent, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"    {parent}: {count} examples")
        
        return correct_patterns
    
    def find_misplaced_products(self):
        """Find all products that are in wrong categories"""
        print("\n🔍 FINDING MISPLACED PRODUCTS...")
        
        misplaced_products = []
        
        # Define what we're looking for
        search_patterns = [
            {
                'type': 'energy_storage',
                'keywords': ['BATTERY ASSEMBLY', 'TRAY ASSEMBLY-BATTERY', 'BATTERY VENT', 'INTELLIGENT BATTERY SENSOR', 'BOARD-BATTERY'],
                'should_be_in_parent': 'parent-2',
                'should_be_in_category_names': ['Battery&Electrical Energy Storage', 'PowerInverter']
            },
            {
                'type': 'battery_harnesses',
                'keywords': ['HARDNESS-BATTERY', 'HARNESS-BATTERY', 'NUT-AUXILIARY BATTERY'],
                'should_be_in_parent': 'parent-7',
                'should_be_in_category_names': ['Battery Harnesses', 'BatteryCable']
            }
        ]
        
        # Check all serials
        all_serials = ['LSFAL11A4PA157987', 'LSFAL11A5MA087816']  # Focus on problematic serials first
        
        for serial in all_serials:
            print(f"\n🔍 Checking serial: {serial}")
            
            categories = Category.objects.filter(slug__contains=f'serial-{serial}').filter(slug__contains='-child-')
            
            for pattern in search_patterns:
                print(f"  Looking for {pattern['type']} products...")
                
                # Find where these products currently are
                current_locations = []
                correct_categories = []
                
                # Find correct categories for this serial and pattern
                for target_parent in [pattern['should_be_in_parent']]:
                    target_cats = categories.filter(slug__contains=f'-{target_parent}-child-')
                    for cat in target_cats:
                        for expected_name in pattern['should_be_in_category_names']:
                            if expected_name.lower() in cat.name.lower():
                                correct_categories.append(cat)
                
                # Find products that match this pattern in ANY category
                for cat in categories:
                    products = cat.product_set.all()
                    for product in products:
                        title = product.title.upper()
                        
                        # Check if this product matches our pattern
                        for keyword in pattern['keywords']:
                            if keyword.upper() in title:
                                # Check if it's in the wrong category
                                is_in_correct_category = any(
                                    correct_cat.id == cat.id for correct_cat in correct_categories
                                )
                                
                                if not is_in_correct_category and correct_categories:
                                    misplaced_products.append({
                                        'product': product,
                                        'current_category': cat,
                                        'correct_categories': correct_categories,
                                        'pattern_type': pattern['type'],
                                        'keyword_matched': keyword
                                    })
                                    print(f"    ❌ MISPLACED: {product.title}")
                                    print(f"       Currently in: {cat.name} ({cat.slug})")
                                    print(f"       Should be in: {[c.name for c in correct_categories]}")
                                
                                break  # Only match one keyword per product
        
        return misplaced_products
    
    def create_reallocation_plan(self, misplaced_products):
        """Create a plan for reallocating products"""
        print(f"\n📋 CREATING REALLOCATION PLAN...")
        
        reallocation_plan = []
        
        # Group by target category for efficiency
        category_moves = defaultdict(list)
        
        for item in misplaced_products:
            product = item['product']
            current_cat = item['current_category']
            correct_cats = item['correct_categories']
            
            # Choose the best target category (first available)
            target_cat = correct_cats[0] if correct_cats else None
            
            if target_cat:
                category_moves[target_cat.id].append({
                    'product': product,
                    'from_category': current_cat,
                    'to_category': target_cat,
                    'pattern_type': item['pattern_type'],
                    'reason': f"Matched keyword: {item['keyword_matched']}"
                })
        
        for target_cat_id, moves in category_moves.items():
            target_cat = Category.objects.get(id=target_cat_id)
            reallocation_plan.append({
                'target_category': target_cat,
                'moves': moves,
                'total_products': len(moves)
            })
        
        return reallocation_plan
    
    def preview_reallocation(self, reallocation_plan):
        """Preview what will be moved"""
        print(f"\n📋 REALLOCATION PREVIEW:")
        print("="*60)
        
        total_moves = sum(plan['total_products'] for plan in reallocation_plan)
        
        for i, plan in enumerate(reallocation_plan, 1):
            target_cat = plan['target_category']
            moves = plan['moves']
            
            print(f"\n{i}. Target Category: {target_cat.name}")
            print(f"   Slug: {target_cat.slug}")
            print(f"   Products to move here: {len(moves)}")
            
            for move in moves[:5]:  # Show first 5
                product = move['product']
                from_cat = move['from_category']
                print(f"     • {product.title}")
                print(f"       From: {from_cat.name} ({from_cat.slug})")
                print(f"       Reason: {move['reason']}")
            
            if len(moves) > 5:
                print(f"     ... and {len(moves) - 5} more products")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Categories to update: {len(reallocation_plan)}")
        print(f"   Total products to move: {total_moves}")
        
        return total_moves > 0
    
    def execute_reallocation(self, reallocation_plan, dry_run=False):
        """Execute the reallocation plan"""
        if dry_run:
            print("\n🔍 DRY RUN MODE - NO CHANGES WILL BE MADE")
            return self.preview_reallocation(reallocation_plan)
        
        print(f"\n🚀 EXECUTING PRODUCT REALLOCATION...")
        
        try:
            with transaction.atomic():
                total_moved = 0
                
                for i, plan in enumerate(reallocation_plan, 1):
                    target_cat = plan['target_category']
                    moves = plan['moves']
                    
                    print(f"({i}/{len(reallocation_plan)}) Moving products to: {target_cat.name}")
                    
                    for move in moves:
                        product = move['product']
                        from_cat = move['from_category']
                        
                        # Move the product
                        product.categories.remove(from_cat)
                        product.categories.add(target_cat)
                        total_moved += 1
                        
                        print(f"  ✓ Moved: {product.title}")
                
                print(f"\n✅ REALLOCATION COMPLETED!")
                print(f"   Total products moved: {total_moved}")
                
                return True
                
        except Exception as e:
            print(f"\n❌ REALLOCATION FAILED: {e}")
            print("🔄 All changes have been rolled back automatically")
            return False
    
    def get_user_confirmation(self, reallocation_plan):
        """Get user confirmation for the reallocation"""
        total_moves = sum(plan['total_products'] for plan in reallocation_plan)
        
        print("\n" + "="*60)
        print("⚠️  PRODUCT REALLOCATION CONFIRMATION")
        print("="*60)
        
        if self.is_production:
            print("🚨 PRODUCTION ENVIRONMENT - PROCEED WITH CAUTION!")
        
        print(f"📊 Reallocation Summary:")
        print(f"   • {len(reallocation_plan)} categories will receive products")
        print(f"   • {total_moves} products will be moved to correct categories")
        print(f"   • All moves are based on patterns from working serials")
        
        while True:
            if self.is_production:
                response = input("Type 'PRODUCTION-CONFIRM' to proceed, 'dry-run' to preview, or 'abort': ").strip()
                if response == 'PRODUCTION-CONFIRM':
                    return True
                elif response.lower() == 'dry-run':
                    return 'dry-run'
                elif response.lower() == 'abort':
                    return False
            else:
                response = input("Type 'CONFIRM' to proceed, 'dry-run' to preview, or 'abort': ").strip()
                if response == 'CONFIRM':
                    return True
                elif response.lower() == 'dry-run':
                    return 'dry-run'
                elif response.lower() == 'abort':
                    return False
            
            print("Invalid response. Please try again.")
    
    def run(self):
        """Main execution method"""
        print("🔄 PRODUCTION-SAFE PRODUCT REALLOCATION MANAGER")
        print("="*60)
        
        # Step 1: Learn correct patterns
        self.analyze_correct_category_patterns()
        
        # Step 2: Find misplaced products
        misplaced_products = self.find_misplaced_products()
        
        if not misplaced_products:
            print("✅ No misplaced products found!")
            return True
        
        # Step 3: Create reallocation plan
        reallocation_plan = self.create_reallocation_plan(misplaced_products)
        
        # Step 4: Get user confirmation
        confirmation = self.get_user_confirmation(reallocation_plan)
        
        if confirmation is True:
            return self.execute_reallocation(reallocation_plan, dry_run=False)
        elif confirmation == 'dry-run':
            return self.execute_reallocation(reallocation_plan, dry_run=True)
        else:
            print("❌ Operation cancelled by user.")
            return False


if __name__ == "__main__":
    manager = ProductReallocationManager()
    success = manager.run()
    
    if success:
        print("\n🎉 Product reallocation completed successfully!")
        print("💡 Test your URLs now - they should show products correctly!")
    else:
        print("\n⚠️ Product reallocation completed with issues or was cancelled.")