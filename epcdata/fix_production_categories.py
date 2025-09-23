#!/usr/bin/env python
"""
PRODUCTION Product Reallocation Script for VanParts Server

This script connects to production database and fixes misplaced products
that are in wrong categories.
"""

import os
import sys
import django
from collections import defaultdict
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force production environment
os.environ['DJANGO_ENV'] = 'PRODUCTION'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category, Product
from django.db import transaction
from django.conf import settings


class ProductionProductReallocation:
    def __init__(self):
        self.backup_file = f"production_product_moves_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def analyze_problem_serial(self):
        """Focus on the known problematic serial LSFAL11A4PA157987"""
        print("🎯 ANALYZING KNOWN PROBLEM SERIAL: LSFAL11A4PA157987")
        print("="*60)
        
        serial = 'LSFAL11A4PA157987'
        
        # Find all categories for this serial
        categories = Category.objects.filter(slug__contains=f'serial-{serial}').filter(slug__contains='-child-')
        print(f"Found {len(categories)} child categories for {serial}")
        
        # Check where energy storage products currently are
        energy_products_found = []
        battery_products_found = []
        
        energy_keywords = ['BATTERY ASSEMBLY', 'TRAY ASSEMBLY-BATTERY', 'INTELLIGENT BATTERY SENSOR', 'BOARD-BATTERY']
        battery_harness_keywords = ['HARDNESS-BATTERY', 'HARNESS-BATTERY', 'NUT-AUXILIARY BATTERY']
        
        print("\n🔍 SCANNING ALL CATEGORIES FOR MISPLACED PRODUCTS...")
        
        for cat in categories:
            products = cat.product_set.all()
            
            for product in products:
                title_upper = product.title.upper()
                
                # Check for energy storage products
                for keyword in energy_keywords:
                    if keyword in title_upper:
                        # Extract parent number
                        parent_num = None
                        slug_parts = cat.slug.split('-')
                        for i, part in enumerate(slug_parts):
                            if part == 'parent' and i + 1 < len(slug_parts):
                                parent_num = slug_parts[i + 1]
                                break
                        
                        energy_products_found.append({
                            'product': product,
                            'current_category': cat,
                            'current_parent': parent_num,
                            'keyword_matched': keyword,
                            'should_be_parent': '2'  # Energy storage should be in parent-2
                        })
                        print(f"  ⚡ ENERGY: {product.title} in Parent-{parent_num} (should be Parent-2)")
                        break
                
                # Check for battery harness products
                for keyword in battery_harness_keywords:
                    if keyword in title_upper:
                        # Extract parent number
                        parent_num = None
                        slug_parts = cat.slug.split('-')
                        for i, part in enumerate(slug_parts):
                            if part == 'parent' and i + 1 < len(slug_parts):
                                parent_num = slug_parts[i + 1]
                                break
                        
                        battery_products_found.append({
                            'product': product,
                            'current_category': cat,
                            'current_parent': parent_num,
                            'keyword_matched': keyword,
                            'should_be_parent': '7'  # Battery harnesses should be in parent-7
                        })
                        print(f"  🔋 BATTERY: {product.title} in Parent-{parent_num} (should be Parent-7)")
                        break
        
        print(f"\n📊 MISPLACEMENT SUMMARY:")
        print(f"  Energy Storage products in wrong categories: {len(energy_products_found)}")
        print(f"  Battery Harness products in wrong categories: {len(battery_products_found)}")
        
        return energy_products_found, battery_products_found
    
    def find_correct_target_categories(self, misplaced_products, target_parent):
        """Find the correct categories to move products to"""
        print(f"\n🎯 FINDING TARGET CATEGORIES FOR PARENT-{target_parent}...")
        
        serial = 'LSFAL11A4PA157987'
        
        # Find categories in the target parent for this serial
        target_categories = Category.objects.filter(
            slug__contains=f'serial-{serial}'
        ).filter(
            slug__contains=f'-parent-{target_parent}-child-'
        )
        
        print(f"Found {len(target_categories)} categories in Parent-{target_parent}:")
        for cat in target_categories:
            product_count = cat.product_set.count()
            print(f"  • {cat.name} ({cat.slug}) - {product_count} products")
        
        # For energy storage (parent-2), look for battery/energy related categories
        if target_parent == '2':
            best_categories = []
            for cat in target_categories:
                name_lower = cat.name.lower()
                if any(keyword in name_lower for keyword in ['battery', 'energy', 'power', 'electrical']):
                    best_categories.append(cat)
            
            if not best_categories:
                best_categories = list(target_categories)  # Fallback to any in parent-2
            
            return best_categories
        
        # For battery harnesses (parent-7), look for harness/cable related categories
        elif target_parent == '7':
            best_categories = []
            for cat in target_categories:
                name_lower = cat.name.lower()
                if any(keyword in name_lower for keyword in ['harness', 'cable', 'battery']):
                    best_categories.append(cat)
            
            if not best_categories:
                best_categories = list(target_categories)  # Fallback to any in parent-7
            
            return best_categories
        
        return list(target_categories)
    
    def create_reallocation_plan(self, energy_products, battery_products):
        """Create a plan for moving products to correct categories"""
        print(f"\n📋 CREATING REALLOCATION PLAN...")
        
        moves = []
        
        # Handle energy storage products (should go to parent-2)
        if energy_products:
            target_cats = self.find_correct_target_categories(energy_products, '2')
            if target_cats:
                target_cat = target_cats[0]  # Use first available
                
                for item in energy_products:
                    if item['current_parent'] != '2':  # Only move if not already in parent-2
                        moves.append({
                            'product': item['product'],
                            'from_category': item['current_category'],
                            'to_category': target_cat,
                            'reason': f"Energy storage product in wrong parent (Parent-{item['current_parent']} → Parent-2)",
                            'type': 'energy_storage'
                        })
        
        # Handle battery harness products (should go to parent-7)
        if battery_products:
            target_cats = self.find_correct_target_categories(battery_products, '7')
            if target_cats:
                target_cat = target_cats[0]  # Use first available
                
                for item in battery_products:
                    if item['current_parent'] != '7':  # Only move if not already in parent-7
                        moves.append({
                            'product': item['product'],
                            'from_category': item['current_category'],
                            'to_category': target_cat,
                            'reason': f"Battery harness product in wrong parent (Parent-{item['current_parent']} → Parent-7)",
                            'type': 'battery_harness'
                        })
        
        return moves
    
    def preview_moves(self, moves):
        """Preview the moves that will be made"""
        print(f"\n📋 MOVE PREVIEW:")
        print("="*60)
        
        if not moves:
            print("✅ No moves needed - all products are in correct categories!")
            return False
        
        print(f"Products to move: {len(moves)}")
        print()
        
        for i, move in enumerate(moves, 1):
            product = move['product']
            from_cat = move['from_category']
            to_cat = move['to_category']
            
            print(f"{i}. {product.title}")
            print(f"   From: {from_cat.name}")
            print(f"   From Slug: {from_cat.slug}")
            print(f"   To: {to_cat.name}")
            print(f"   To Slug: {to_cat.slug}")
            print(f"   Reason: {move['reason']}")
            print(f"   Type: {move['type']}")
            print()
        
        return True
    
    def execute_moves(self, moves, dry_run=False):
        """Execute the product moves"""
        if dry_run:
            print("🔍 DRY RUN MODE - NO CHANGES WILL BE MADE")
            return self.preview_moves(moves)
        
        if not moves:
            print("✅ No moves to execute!")
            return True
        
        print(f"🚀 EXECUTING {len(moves)} PRODUCT MOVES...")
        
        try:
            with transaction.atomic():
                # Create backup record
                backup_data = []
                
                for i, move in enumerate(moves, 1):
                    product = move['product']
                    from_cat = move['from_category']
                    to_cat = move['to_category']
                    
                    print(f"({i}/{len(moves)}) Moving: {product.title}")
                    print(f"  From: {from_cat.name}")
                    print(f"  To: {to_cat.name}")
                    
                    # Backup original state
                    backup_data.append({
                        'product_id': product.id,
                        'product_title': product.title,
                        'from_category_id': from_cat.id,
                        'from_category_slug': from_cat.slug,
                        'to_category_id': to_cat.id,
                        'to_category_slug': to_cat.slug,
                        'reason': move['reason'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Execute the move
                    product.categories.remove(from_cat)
                    product.categories.add(to_cat)
                    
                    print(f"  ✅ Moved successfully")
                
                # Save backup
                with open(self.backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                print(f"\n✅ ALL MOVES COMPLETED SUCCESSFULLY!")
                print(f"📁 Backup saved to: {self.backup_file}")
                
                return True
                
        except Exception as e:
            print(f"\n❌ MOVE FAILED: {e}")
            print("🔄 All changes have been rolled back automatically")
            return False
    
    def get_user_confirmation(self, moves):
        """Get user confirmation"""
        print("\n" + "="*60)
        print("⚠️  PRODUCTION PRODUCT REALLOCATION CONFIRMATION")
        print("="*60)
        print("🚨 PRODUCTION DATABASE - PROCEED WITH CAUTION!")
        print(f"📊 {len(moves)} products will be moved to correct categories")
        print(f"🔙 Backup will be saved to: {self.backup_file}")
        
        while True:
            response = input("Type 'PRODUCTION-CONFIRM' to proceed, 'dry-run' to preview, or 'abort': ").strip()
            if response == 'PRODUCTION-CONFIRM':
                return True
            elif response.lower() == 'dry-run':
                return 'dry-run'
            elif response.lower() == 'abort':
                return False
            print("Invalid response. Please try again.")
    
    def run(self):
        """Main execution method"""
        print("🎯 PRODUCTION PRODUCT REALLOCATION FOR VANPARTS")
        print("="*60)
        print(f"🗄️ Database: {settings.DATABASES['default']['NAME']}")
        print()
        
        # Step 1: Analyze the problem
        energy_products, battery_products = self.analyze_problem_serial()
        
        # Step 2: Create reallocation plan
        moves = self.create_reallocation_plan(energy_products, battery_products)
        
        if not moves:
            print("✅ No misplaced products found!")
            return True
        
        # Step 3: Get user confirmation
        confirmation = self.get_user_confirmation(moves)
        
        if confirmation is True:
            return self.execute_moves(moves, dry_run=False)
        elif confirmation == 'dry-run':
            return self.execute_moves(moves, dry_run=True)
        else:
            print("❌ Operation cancelled by user.")
            return False


if __name__ == "__main__":
    reallocation = ProductionProductReallocation()
    success = reallocation.run()
    
    if success:
        print("\n🎉 Production reallocation completed!")
        print("💡 Test your energy storage URLs now!")
    else:
        print("\n⚠️ Reallocation had issues or was cancelled.")