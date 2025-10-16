#!/usr/bin/env python
"""
VPS Clean Duplicate Category Images
Removes duplicate images created by Django's auto-generated suffixes
Uses VPS-specific paths: /home/rentals/epc_parts_store/epcdata/media/categories/
"""
import os
import django
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from django.conf import settings

def clean_duplicate_images_vps(dry_run=True):
    """
    Clean duplicate category images on VPS, keeping only the original file
    """
    
    print(f"🧹 VPS Clean Duplicate Category Images")
    print(f"Mode: {'🔍 DRY RUN (preview only)' if dry_run else '🚀 LIVE (making changes)'}")
    print("="*70)
    
    # VPS-specific path to media categories
    vps_media_categories_path = Path("/home/rentals/epc_parts_store/epcdata/media/categories")
    
    print(f"📁 VPS Media Path: {vps_media_categories_path}")
    
    if not vps_media_categories_path.exists():
        print(f"❌ Error: Categories folder not found at {vps_media_categories_path}")
        print(f"   Make sure you're running this on the VPS and the path exists")
        return None
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    all_images = []
    
    for file_path in vps_media_categories_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            all_images.append(file_path)
    
    print(f"📷 Found {len(all_images)} total image files")
    
    # Group images by base name (before Django suffix)
    image_groups = defaultdict(list)
    
    for img_path in all_images:
        filename = img_path.name
        
        # Extract base name (remove Django auto-generated suffix)
        if '_' in filename:
            # Check if it has Django pattern like _abc123.png
            name_parts = filename.rsplit('_', 1)
            if len(name_parts) == 2:
                base_name, suffix_part = name_parts
                
                # Check if suffix looks like Django pattern (alphanumeric + extension)
                suffix_without_ext = suffix_part.split('.')[0]
                if suffix_without_ext.isalnum() and len(suffix_without_ext) >= 6:
                    # This looks like a Django duplicate
                    image_groups[base_name].append(img_path)
                else:
                    # This is part of the original name
                    image_groups[filename].append(img_path)
            else:
                image_groups[filename].append(img_path)
        else:
            # No underscore, original file
            image_groups[filename].append(img_path)
    
    # Identify groups with duplicates
    duplicate_groups = {k: v for k, v in image_groups.items() if len(v) > 1}
    unique_images = {k: v for k, v in image_groups.items() if len(v) == 1}
    
    print(f"📊 Analysis:")
    print(f"   Unique images (no duplicates): {len(unique_images)}")
    print(f"   Image groups with duplicates: {len(duplicate_groups)}")
    
    total_duplicates = sum(len(files) - 1 for files in duplicate_groups.values())
    print(f"   Total duplicate files to remove: {total_duplicates}")
    
    if not duplicate_groups:
        print("✅ No duplicate images found!")
        return None
    
    # Process cleanup
    removed_files = 0
    updated_categories = 0
    errors = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    mode_suffix = "_dry_run" if dry_run else "_live"
    report_filename = f'vps_clean_duplicates{mode_suffix}_{timestamp}.txt'
    
    print(f"\n📝 Processing duplicates...")
    
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write(f"VPS Clean Duplicate Category Images Report\n")
        report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        report.write(f"VPS Media Path: {vps_media_categories_path}\n")
        report.write("="*80 + "\n\n")
        
        report.write(f"ANALYSIS:\n")
        report.write(f"Total images found: {len(all_images)}\n")
        report.write(f"Unique images: {len(unique_images)}\n")
        report.write(f"Duplicate groups: {len(duplicate_groups)}\n")
        report.write(f"Duplicates to remove: {total_duplicates}\n\n")
        
        report.write("DUPLICATE GROUPS:\n")
        report.write("="*50 + "\n")
        
        for i, (base_name, file_list) in enumerate(duplicate_groups.items(), 1):
            report.write(f"\n{i:3d}. Base: {base_name} ({len(file_list)} files)\n")
            
            # Sort files - prefer original (shortest name)
            sorted_files = sorted(file_list, key=lambda x: (len(x.name), x.name))
            keep_file = sorted_files[0]  # Keep the shortest/original filename
            remove_files = sorted_files[1:]  # Remove the rest
            
            report.write(f"     KEEP: {keep_file.name}\n")
            
            # Remove duplicate files
            for j, remove_file in enumerate(remove_files, 1):
                try:
                    if not dry_run:
                        remove_file.unlink()  # Delete file
                    
                    removed_files += 1
                    status = "✅ REMOVED" if not dry_run else "✅ WOULD REMOVE"
                    print(f"   {i:3d}.{j} {status}: {remove_file.name}")
                    report.write(f"     {status}: {remove_file.name}\n")
                    
                except Exception as e:
                    error_msg = f"Error removing {remove_file.name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   {i:3d}.{j} ❌ ERROR: {str(e)}")
                    report.write(f"     ❌ ERROR: {str(e)}\n")
            
            # Update categories that reference removed files
            if not dry_run:
                categories_using_removed = Category.objects.filter(
                    image__in=[f"categories/{f.name}" for f in remove_files]
                )
                
                for category in categories_using_removed:
                    try:
                        # Update to use the kept file
                        category.image = f"categories/{keep_file.name}"
                        category.save()
                        updated_categories += 1
                        print(f"       ↳ Updated category: {category.name[:50]}...")
                        report.write(f"       ↳ Updated category: {category.name}\n")
                        
                    except Exception as e:
                        error_msg = f"Error updating category {category.name}: {str(e)}"
                        errors.append(error_msg)
                        report.write(f"       ↳ ❌ ERROR updating category: {str(e)}\n")
        
        # Summary
        report.write(f"\n{'='*80}\n")
        report.write(f"SUMMARY:\n")
        report.write(f"{'='*80}\n")
        report.write(f"Files removed: {removed_files}/{total_duplicates}\n")
        report.write(f"Categories updated: {updated_categories}\n")
        report.write(f"Errors: {len(errors)}\n")
        report.write(f"Space saved: ~{removed_files * 50}KB (estimated)\n")
        
        if errors:
            report.write(f"\nERRORS:\n")
            report.write("-"*20 + "\n")
            for error in errors:
                report.write(f"• {error}\n")
        
        if dry_run:
            report.write(f"\n⚠️ THIS WAS A DRY RUN - NO CHANGES WERE MADE\n")
        else:
            report.write(f"\n✅ VPS CLEANUP COMPLETED!\n")
    
    print(f"\n📊 Final Results:")
    print(f"   Files removed: {removed_files}/{total_duplicates}")
    print(f"   Categories updated: {updated_categories}")
    print(f"   Errors: {len(errors)}")
    print(f"   Estimated space saved: ~{removed_files * 50}KB")
    
    if dry_run:
        print(f"\n⚠️ THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        print(f"   To actually clean files, run with --live flag")
    else:
        print(f"\n✅ VPS CLEANUP COMPLETED!")
        print(f"   Removed {removed_files} duplicate files")
        print(f"   Your VPS pages should load much faster now!")
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    return report_filename, removed_files, len(errors)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='VPS Clean Duplicate Category Images',
        epilog="""
Examples:
  python vps_clean_duplicate_images.py                    # Dry run (preview)
  python vps_clean_duplicate_images.py --live             # Clean duplicates on VPS
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--dry-run', action='store_true', default=True, help='Preview changes (default)')
    mode_group.add_argument('--live', action='store_true', help='Actually clean files on VPS')
    
    args = parser.parse_args()
    dry_run = not args.live
    
    print("🧹 VPS Clean Duplicate Category Images")
    print("="*50)
    print("🐧 Designed for VPS paths: /home/rentals/epc_parts_store/epcdata/media/categories/")
    
    if not dry_run:
        print("⚠️  WARNING: This will permanently delete duplicate files on VPS!")
        response = input("Continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            exit(0)
    
    try:
        result = clean_duplicate_images_vps(dry_run=dry_run)
        if result:
            report_file, removed, errors = result
            print(f"\n✅ VPS Process completed! Check report: {report_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()