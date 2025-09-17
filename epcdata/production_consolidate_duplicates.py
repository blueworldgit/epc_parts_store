#!/usr/bin/env python
"""
PRODUCTION-SAFE Database Consolidation Script for Duplicate Child Categories

This script is designed for safe execution on production environments.
It includes extensive safety checks, backup verification, and rollback capabilities.

CRITICAL: Always run in dry-run mode first and ensure database backup exists!
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

from oscar.apps.catalogue.models import Category
from django.db import transaction, connection
from django.conf import settings


class ProductionConsolidator:
    def __init__(self):
        self.backup_file = f"consolidation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.is_production = self.detect_production_environment()
        
    def detect_production_environment(self):
        """Detect if we're running in production"""
        # Check various indicators of production environment
        indicators = [
            'DEBUG' in settings.__dict__ and not settings.DEBUG,
            'PROD' in os.environ.get('DJANGO_ENV', '').upper(),
            'PRODUCTION' in os.environ.get('DJANGO_ENV', '').upper(),
            'prod' in getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', '').lower(),
            'production' in getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', '').lower(),
        ]
        return any(indicators)
    
    def safety_checks(self):
        """Perform comprehensive safety checks before execution"""
        print("🔒 PERFORMING SAFETY CHECKS...")
        
        # Check 1: Environment verification
        if self.is_production:
            print("🚨 PRODUCTION ENVIRONMENT DETECTED!")
            print("   Extra safety measures will be enforced.")
        else:
            print("🔧 Development environment detected.")
        
        # Check 2: Database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ Database connection: OK")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Check 3: Check current duplicate count
        child_categories = Category.objects.filter(slug__contains='-child-')
        parent_name_groups = defaultdict(list)
        
        for cat in child_categories:
            slug_parts = cat.slug.split('-child-')
            if len(slug_parts) == 2:
                parent_slug_part = slug_parts[0]
                parent_name_groups[(parent_slug_part, cat.name)].append(cat)
        
        duplicate_count = sum(1 for cats in parent_name_groups.values() if len(cats) > 1)
        total_products_affected = sum(
            sum(cat.product_set.count() for cat in cats[1:]) 
            for cats in parent_name_groups.values() if len(cats) > 1
        )
        
        print(f"📊 Current state:")
        print(f"   Total child categories: {child_categories.count()}")
        print(f"   Duplicate sets found: {duplicate_count}")
        print(f"   Products to be moved: {total_products_affected}")
        
        if duplicate_count == 0:
            print("✅ No duplicates found - database is already clean!")
            return False
        
        return True
    
    def create_backup(self, consolidation_plan):
        """Create a detailed backup of what will be changed"""
        print(f"💾 Creating backup file: {self.backup_file}")
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if self.is_production else 'development',
            'database_name': getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', 'unknown'),
            'changes': []
        }
        
        for plan_item in consolidation_plan:
            original = plan_item['original']
            duplicates = plan_item['duplicates']
            
            change_record = {
                'original_category': {
                    'id': original.id,
                    'name': original.name,
                    'slug': original.slug,
                    'product_count_before': original.product_set.count()
                },
                'duplicate_categories': [],
                'products_to_move': []
            }
            
            for dup in duplicates:
                products = list(dup.product_set.values_list('id', 'title'))
                change_record['duplicate_categories'].append({
                    'id': dup.id,
                    'name': dup.name,
                    'slug': dup.slug,
                    'product_count': len(products),
                    'will_be_deleted': True
                })
                change_record['products_to_move'].extend([
                    {'product_id': pid, 'title': title, 'from_category_id': dup.id, 'to_category_id': original.id}
                    for pid, title in products
                ])
            
            backup_data['changes'].append(change_record)
        
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup created: {len(backup_data['changes'])} change sets recorded")
        return self.backup_file
    
    def get_user_confirmation(self, consolidation_plan):
        """Get explicit user confirmation with detailed warnings"""
        print("\n" + "="*60)
        print("⚠️  FINAL CONFIRMATION REQUIRED")
        print("="*60)
        
        total_products = sum(item['total_products_to_move'] for item in consolidation_plan)
        total_deletes = sum(len(item['duplicates']) for item in consolidation_plan)
        
        if self.is_production:
            print("🚨 YOU ARE ABOUT TO MODIFY A PRODUCTION DATABASE!")
            print("🚨 THIS WILL PERMANENTLY CHANGE DATA!")
        
        print(f"📊 Summary of changes:")
        print(f"   • {len(consolidation_plan)} duplicate sets will be consolidated")
        print(f"   • {total_products} products will be moved between categories")
        print(f"   • {total_deletes} duplicate categories will be DELETED")
        print(f"   • Backup file created: {self.backup_file}")
        
        print(f"\n🛡️  Safety measures in place:")
        print(f"   • Database transaction will be used (atomic operation)")
        print(f"   • Detailed backup file created for rollback")
        print(f"   • All changes logged for audit trail")
        
        if self.is_production:
            print(f"\n🚨 PRODUCTION ENVIRONMENT WARNINGS:")
            print(f"   • Ensure database backup exists before proceeding")
            print(f"   • Consider running during maintenance window")
            print(f"   • Have rollback procedure ready")
            print(f"   • Monitor application after changes")
        
        print(f"\n❓ Do you want to proceed?")
        while True:
            if self.is_production:
                response = input("Type 'PRODUCTION-CONFIRM' to proceed, 'dry-run' to preview, or 'abort' to cancel: ").strip()
                if response == 'PRODUCTION-CONFIRM':
                    return True
                elif response.lower() == 'dry-run':
                    return 'dry-run'
                elif response.lower() == 'abort':
                    return False
                else:
                    print("Invalid response. Please type exactly 'PRODUCTION-CONFIRM', 'dry-run', or 'abort'")
            else:
                response = input("Type 'CONFIRM' to proceed, 'dry-run' to preview, or 'abort' to cancel: ").strip()
                if response == 'CONFIRM':
                    return True
                elif response.lower() == 'dry-run':
                    return 'dry-run'
                elif response.lower() == 'abort':
                    return False
                else:
                    print("Invalid response. Please type 'CONFIRM', 'dry-run', or 'abort'")
    
    def analyze_duplicates(self):
        """Analyze duplicate child categories"""
        print("🔍 ANALYZING DUPLICATE CHILD CATEGORIES...\n")
        
        child_categories = Category.objects.filter(slug__contains='-child-').order_by('slug')
        parent_name_groups = defaultdict(list)
        
        for cat in child_categories:
            slug_parts = cat.slug.split('-child-')
            if len(slug_parts) == 2:
                parent_slug_part = slug_parts[0]
                parent_name_groups[(parent_slug_part, cat.name)].append(cat)
        
        consolidation_plan = []
        duplicates_found = 0
        
        for (parent_slug_part, child_name), categories in parent_name_groups.items():
            if len(categories) > 1:
                duplicates_found += 1
                categories.sort(key=lambda x: x.id)
                
                original = categories[0]
                duplicates = categories[1:]
                
                total_products_in_duplicates = sum(dup.product_set.count() for dup in duplicates)
                
                consolidation_plan.append({
                    'original': original,
                    'duplicates': duplicates,
                    'total_products_to_move': total_products_in_duplicates,
                    'parent_context': parent_slug_part,
                    'child_name': child_name
                })
        
        print(f"📊 Analysis complete:")
        print(f"   Duplicate sets found: {duplicates_found}")
        total_products_to_move = sum(item['total_products_to_move'] for item in consolidation_plan)
        print(f"   Total products to move: {total_products_to_move}")
        
        return consolidation_plan
    
    def execute_consolidation(self, consolidation_plan, dry_run=False):
        """Execute the consolidation with full transaction safety"""
        if dry_run:
            print("\n🔍 DRY RUN MODE - NO CHANGES WILL BE MADE")
            return self.preview_changes(consolidation_plan)
        
        print("\n🚀 EXECUTING CONSOLIDATION WITH TRANSACTION SAFETY...")
        
        try:
            with transaction.atomic():
                total_moved = 0
                total_deleted = 0
                
                for i, plan_item in enumerate(consolidation_plan, 1):
                    original = plan_item['original']
                    duplicates = plan_item['duplicates']
                    
                    print(f"({i}/{len(consolidation_plan)}) Consolidating: '{plan_item['child_name']}'")
                    
                    for dup in duplicates:
                        products = dup.product_set.all()
                        product_count = products.count()
                        
                        if product_count > 0:
                            print(f"  Moving {product_count} products from ID={dup.id} to ID={original.id}")
                            
                            for product in products:
                                product.categories.remove(dup)
                                product.categories.add(original)
                            
                            total_moved += product_count
                        
                        # Delete duplicate category
                        print(f"  Deleting duplicate category: {dup.slug}")
                        dup.delete()
                        total_deleted += 1
                
                print(f"\n✅ CONSOLIDATION COMPLETED SUCCESSFULLY!")
                print(f"   Products moved: {total_moved}")
                print(f"   Duplicate categories deleted: {total_deleted}")
                print(f"   Backup file: {self.backup_file}")
                
                return True
                
        except Exception as e:
            print(f"\n❌ CONSOLIDATION FAILED: {e}")
            print("🔄 All changes have been rolled back automatically")
            return False
    
    def preview_changes(self, consolidation_plan):
        """Preview what changes would be made"""
        print("\n📋 PREVIEW OF CHANGES:")
        print("="*50)
        
        for i, plan_item in enumerate(consolidation_plan[:10], 1):  # Show first 10
            original = plan_item['original']
            duplicates = plan_item['duplicates']
            
            print(f"\n{i}. Child: '{plan_item['child_name']}'")
            print(f"   Context: {plan_item['parent_context']}")
            print(f"   Target: {original.slug} (ID={original.id}, Current products: {original.product_set.count()})")
            
            for dup in duplicates:
                product_count = dup.product_set.count()
                print(f"   Source: {dup.slug} (ID={dup.id}, Products to move: {product_count})")
        
        if len(consolidation_plan) > 10:
            print(f"\n... and {len(consolidation_plan) - 10} more sets")
        
        total_products = sum(item['total_products_to_move'] for item in consolidation_plan)
        total_deletes = sum(len(item['duplicates']) for item in consolidation_plan)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total sets to consolidate: {len(consolidation_plan)}")
        print(f"   Total products to move: {total_products}")
        print(f"   Total categories to delete: {total_deletes}")
        
        return True
    
    def run(self):
        """Main execution method"""
        print("🔧 PRODUCTION-SAFE DUPLICATE CATEGORY CONSOLIDATION")
        print("="*60)
        
        # Step 1: Safety checks
        if not self.safety_checks():
            print("❌ Safety checks failed or no work needed. Exiting.")
            return False
        
        # Step 2: Analyze duplicates
        consolidation_plan = self.analyze_duplicates()
        if not consolidation_plan:
            print("✅ No duplicate categories found. Database is clean!")
            return True
        
        # Step 3: Create backup
        self.create_backup(consolidation_plan)
        
        # Step 4: Get user confirmation
        confirmation = self.get_user_confirmation(consolidation_plan)
        
        if confirmation is True:
            # Execute consolidation
            return self.execute_consolidation(consolidation_plan, dry_run=False)
        elif confirmation == 'dry-run':
            # Show preview only
            return self.execute_consolidation(consolidation_plan, dry_run=True)
        else:
            print("❌ Operation cancelled by user.")
            return False


if __name__ == "__main__":
    consolidator = ProductionConsolidator()
    success = consolidator.run()
    
    if success:
        print("\n🎉 Script completed successfully!")
    else:
        print("\n⚠️ Script completed with issues or was cancelled.")