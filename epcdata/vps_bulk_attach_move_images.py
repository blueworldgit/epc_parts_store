#!/usr/bin/env python
"""
VPS Bulk Image Attachment Script
Attaches images from Rentals folder to categories AND moves them to production media folder
Designed for VPS deployment at /home/rentals/epc_parts_store/

Usage:
    python vps_bulk_attach_move_images.py                    # Dry run (preview only)
    python vps_bulk_attach_move_images.py --dry-run          # Dry run (explicit)
    python vps_bulk_attach_move_images.py --live             # Live run (makes changes)
    python vps_bulk_attach_move_images.py --threshold 0.7    # Custom similarity threshold
"""
import os
import django
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from django.core.files.images import ImageFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def clean_category_name(name):
    """Clean category name same way as other scripts"""
    if name and " - " in name:
        return name.split(" - ", 1)[1].strip()
    return name.strip() if name else ""

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def vps_bulk_attach_and_move_images(dry_run=True, similarity_threshold=0.6):
    """
    VPS version: Attach images to categories AND move to production media folder
    Auto-detects environment (Windows dev vs Linux VPS)
    OVERWRITES existing images and database references - fresh start every time
    """
    
    print(f"🚀 VPS Bulk Image Attachment & Move Script (FRESH OVERWRITE MODE)")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will make changes)'}")
    print(f"Similarity threshold: {similarity_threshold*100:.0f}%")
    print(f"🔄 OVERWRITE MODE: Will replace existing images and database references")
    print("="*70)
    
    # Auto-detect environment and set paths accordingly
    import platform
    current_os = platform.system()
    
    if current_os == "Windows":
        # Local Windows development paths
        base_path = Path("C:/pythonstuff/vansdirect/epc_parts_store")
        rentals_folder = base_path / "epcdata" / "Rentals"
        media_categories_folder = base_path / "epcdata" / "media" / "categories"
        print(f"🖥️ Environment: Windows (Local Development)")
    else:
        # Linux VPS paths
        base_path = Path("/home/rentals/epc_parts_store")
        rentals_folder = base_path / "epcdata" / "Rentals"
        media_categories_folder = base_path / "epcdata" / "media" / "categories"
        print(f"🐧 Environment: Linux (VPS Production)")
    
    print(f"📁 Paths:")
    print(f"   Source (Rentals): {rentals_folder}")
    print(f"   Target (Media): {media_categories_folder}")
    
    # Check if paths exist
    if not rentals_folder.exists():
        print(f"❌ Error: Rentals folder not found at {rentals_folder}")
        print(f"   Make sure you've pulled the repo and Rentals folder exists")
        return None
    
    if not media_categories_folder.exists():
        print(f"📁 Creating media/categories folder: {media_categories_folder}")
        if not dry_run:
            media_categories_folder.mkdir(parents=True, exist_ok=True)
    else:
        # Count existing images that will be overwritten
        existing_images = list(media_categories_folder.glob('*'))
        existing_count = len([f for f in existing_images if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}])
        if existing_count > 0:
            print(f"🔄 Found {existing_count} existing images in media folder - will overwrite as needed")
        else:
            print(f"📁 Media folder exists but is empty")
    
    # Get image files from Rentals folder
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    available_images = {}
    
    for file_path in rentals_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_name = file_path.stem  # filename without extension
            available_images[image_name] = file_path
    
    print(f"📷 Found {len(available_images)} images in Rentals folder")
    
    # Get all categories and group by cleaned name
    categories = Category.objects.all()
    category_groups = {}
    unique_category_names = set()
    
    for cat in categories:
        if cat.name:
            clean_name = clean_category_name(cat.name)
            unique_category_names.add(clean_name)
            if clean_name not in category_groups:
                category_groups[clean_name] = []
            category_groups[clean_name].append(cat)
    
    unique_category_names = sorted(list(unique_category_names))
    print(f"🏷️  Found {len(category_groups)} unique category names")
    
    # Find matches between images and categories
    matches = []
    for image_name, image_path in available_images.items():
        best_match = None
        best_score = 0
        
        # Check for exact match first
        if image_name in category_groups:
            matches.append({
                'image_name': image_name,
                'image_path': image_path,
                'categories': category_groups[image_name],
                'match_type': 'exact',
                'similarity': 1.0
            })
        else:
            # Find best similarity match
            for cat_name in unique_category_names:
                score = similarity(image_name, cat_name)
                if score > best_score:
                    best_score = score
                    best_match = cat_name
            
            if best_score >= similarity_threshold:
                matches.append({
                    'image_name': image_name,
                    'image_path': image_path,
                    'categories': category_groups[best_match],
                    'match_type': 'similarity',
                    'similarity': best_score,
                    'matched_category_name': best_match
                })
    
    exact_count = len([m for m in matches if m['match_type'] == 'exact'])
    similarity_count = len([m for m in matches if m['match_type'] == 'similarity'])
    
    print(f"✅ Found {exact_count} exact matches")
    print(f"🔄 Found {similarity_count} similarity matches (≥{similarity_threshold*100:.0f}%)")
    print(f"📊 Total matches: {len(matches)}")
    
    if not matches:
        print("❌ No matches found. Please check image names and category names.")
        return None
    
    # Process matches
    total_attachments = 0
    successful_attachments = 0
    total_file_moves = 0
    successful_file_moves = 0
    errors = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    mode_suffix = "_dry_run" if dry_run else "_live"
    threshold_suffix = f"_{int(similarity_threshold*100)}pct"
    report_filename = f'vps_bulk_attach_move{mode_suffix}{threshold_suffix}_{timestamp}.txt'
    
    print(f"📝 Generating report: {report_filename}")
    
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write(f"VPS Bulk Image Attachment & Move Report (OVERWRITE MODE)\n")
        report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        report.write(f"Overwrite Mode: ENABLED (replaces existing images and database references)\n")
        report.write(f"Similarity threshold: {similarity_threshold*100:.0f}%\n")
        report.write(f"VPS Base Path: {base_path}\n")
        report.write(f"Source Folder: {rentals_folder}\n")
        report.write(f"Media Folder: {media_categories_folder}\n")
        report.write("="*80 + "\n\n")
        
        report.write(f"SUMMARY:\n")
        report.write(f"Images available: {len(available_images)}\n")
        report.write(f"Unique categories: {len(category_groups)}\n")
        report.write(f"Exact matches: {exact_count}\n")
        report.write(f"Similarity matches: {similarity_count}\n")
        report.write(f"Total matches: {len(matches)}\n\n")
        
        report.write("PROCESSING RESULTS:\n")
        report.write("="*50 + "\n")
        
        for i, match in enumerate(matches, 1):
            image_name = match['image_name']
            image_path = match['image_path']
            categories = match['categories']
            match_type = match['match_type']
            similarity_score = match['similarity']
            
            # Generate target filename (clean for filesystem)
            clean_filename = image_name.replace(' ', '_').replace('&', '_').replace('(', '').replace(')', '')
            target_filename = f"{clean_filename}.png"
            target_path = media_categories_folder / target_filename
            
            if match_type == 'exact':
                print(f"\n{i:3d}. Processing '{image_name}' (EXACT match)...")
                report.write(f"\n{i:3d}. Image: {image_name} (EXACT MATCH)\n")
            else:
                matched_name = match['matched_category_name']
                print(f"\n{i:3d}. Processing '{image_name}' → '{matched_name}' ({similarity_score:.1%})...")
                report.write(f"\n{i:3d}. Image: {image_name} → {matched_name} ({similarity_score:.1%})\n")
            
            report.write(f"     Source: {image_path}\n")
            report.write(f"     Target: {target_path}\n")
            report.write(f"     Categories to update: {len(categories)}\n")
            
            # Step 1: Move/Copy file to media folder (OVERWRITE existing)
            total_file_moves += 1
            file_move_success = False
            
            # Check if target file already exists
            file_exists = target_path.exists()
            
            try:
                if not dry_run:
                    # Always overwrite - copy file to media folder (keeping original in Rentals)
                    shutil.copy2(image_path, target_path)
                    if file_exists:
                        print(f"     📁 OVERWRITTEN: {image_path.name} → {target_path}")
                    else:
                        print(f"     📁 MOVED: {image_path.name} → {target_path}")
                else:
                    if file_exists:
                        print(f"     📁 WOULD OVERWRITE: {image_path.name} → {target_path}")
                    else:
                        print(f"     📁 WOULD MOVE: {image_path.name} → {target_path}")
                
                successful_file_moves += 1
                file_move_success = True
                action = "OVERWRITTEN" if file_exists else "MOVED"
                report.write(f"       FILE: {'✅ ' + action if not dry_run else '✅ WOULD ' + action} to {target_path}\n")
                
            except Exception as e:
                error_msg = f"Error moving file {image_path} to {target_path}: {str(e)}"
                errors.append(error_msg)
                print(f"     📁 ❌ FILE MOVE ERROR: {str(e)}")
                report.write(f"       FILE: ❌ ERROR moving file: {str(e)}\n")
            
            # Step 2: Attach to categories (OVERWRITE existing database references)
            if file_move_success or dry_run:
                for j, category in enumerate(categories, 1):
                    total_attachments += 1
                    
                    # Check if category already has an image
                    had_image = bool(category.image)
                    
                    try:
                        if not dry_run:
                            # Clear existing image first (if any) to ensure clean attachment
                            if category.image:
                                try:
                                    # Delete old image file if it exists and is different
                                    old_image_path = category.image.path
                                    if old_image_path != str(target_path) and os.path.exists(old_image_path):
                                        os.remove(old_image_path)
                                except:
                                    pass  # Ignore errors deleting old files
                            
                            # Attach the new image (overwrites database reference)
                            with open(target_path, 'rb') as img_file:
                                category.image.save(
                                    target_filename,
                                    ImageFile(img_file),
                                    save=True
                                )
                        
                        successful_attachments += 1
                        if had_image:
                            status = "✅ REPLACED" if not dry_run else "✅ WOULD REPLACE"
                            print(f"       {j}. {status}: {category.name[:60]}...")
                            report.write(f"         {j}. {status}: {category.name}\n")
                        else:
                            status = "✅ ATTACHED" if not dry_run else "✅ WOULD ATTACH"
                            print(f"       {j}. {status}: {category.name[:60]}...")
                            report.write(f"         {j}. {status}: {category.name}\n")
                        report.write(f"            ID: {category.id}, Slug: {category.slug}\n")
                        
                    except Exception as e:
                        error_msg = f"Error attaching to {category.name}: {str(e)}"
                        errors.append(error_msg)
                        print(f"       {j}. ❌ ATTACH ERROR: {str(e)}")
                        report.write(f"         {j}. ❌ ATTACH ERROR: {str(e)}\n")
            else:
                # Skip category attachment if file move failed
                print(f"       ⏭️  SKIPPING category attachment (file move failed)")
                report.write(f"       ⏭️  SKIPPED category attachment (file move failed)\n")
        
        # Summary section
        report.write(f"\n{'='*80}\n")
        report.write(f"FINAL SUMMARY:\n")
        report.write(f"{'='*80}\n")
        report.write(f"File move operations: {total_file_moves}\n")
        report.write(f"Successful file moves: {successful_file_moves}\n")
        report.write(f"Category attachment operations: {total_attachments}\n")
        report.write(f"Successful attachments: {successful_attachments}\n")
        report.write(f"Total errors: {len(errors)}\n")
        report.write(f"File move success rate: {(successful_file_moves/total_file_moves*100):.1f}%\n")
        report.write(f"Attachment success rate: {(successful_attachments/total_attachments*100):.1f}% (if total > 0)\n")
        
        if errors:
            report.write(f"\nERRORS:\n")
            report.write("-"*20 + "\n")
            for error in errors:
                report.write(f"• {error}\n")
        
        if dry_run:
            report.write(f"\n⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE\n")
            report.write(f"To actually move files and attach images (OVERWRITING existing), run with --live\n")
        else:
            report.write(f"\n✅ LIVE RUN COMPLETED - IMAGES OVERWRITTEN/REPLACED\n")
            report.write(f"All matching images have been moved to media folder and attached to categories\n")
    
    print(f"\n📊 Final Results:")
    print(f"   File moves: {successful_file_moves}/{total_file_moves}")
    print(f"   Category attachments: {successful_attachments}/{total_attachments}")
    print(f"   Errors: {len(errors)}")
    
    if dry_run:
        print(f"\n⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        print(f"   Review the report and run with --live to actually process (WILL OVERWRITE existing)")
    else:
        print(f"\n✅ LIVE RUN COMPLETED!")
        print(f"   Images moved to: {media_categories_folder}")
        print(f"   Categories updated in database")
        print(f"   🔄 OVERWRITE MODE: Existing images and references were replaced")
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    return report_filename, successful_attachments, len(errors)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='VPS Bulk Image Attachment & Move Tool',
        epilog="""
Examples:
  python vps_bulk_attach_move_images.py                    # Dry run (safe preview)
  python vps_bulk_attach_move_images.py --live             # Live run (makes changes)
  python vps_bulk_attach_move_images.py --threshold 0.8    # 80% similarity threshold
  python vps_bulk_attach_move_images.py --live --threshold 0.7  # Live with 70% threshold
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add mutually exclusive group for dry-run vs live
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--dry-run', 
        action='store_true', 
        default=True,
        help='Preview changes without making them (default)'
    )
    mode_group.add_argument(
        '--live', 
        action='store_true',
        help='Actually make changes (move files and update database)'
    )
    
    parser.add_argument(
        '--threshold', 
        type=float, 
        default=0.6,
        help='Similarity threshold for matching (0.0-1.0, default: 0.6)'
    )
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.live  # If --live is specified, dry_run = False
    
    # Validate threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("❌ Error: Threshold must be between 0.0 and 1.0")
        exit(1)
    
    print("� VPS Bulk Image Attachment & Move Tool")
    print("="*50)
    print(f"Mode: {'🔍 DRY RUN (preview only)' if dry_run else '🚀 LIVE RUN (making changes)'}")
    print(f"Similarity threshold: {args.threshold*100:.0f}%")
    
    if dry_run:
        print("💡 TIP: Add --live flag to actually make changes")
    else:
        print("⚠️  WARNING: This will move files, modify the database, and OVERWRITE existing images!")
        print("   - Existing image files will be replaced")
        print("   - Database references will be updated")
        print("   - This provides a fresh start every time")
        response = input("Continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            exit(0)
    
    print()
    
    try:
        report_file, success, errors = vps_bulk_attach_and_move_images(
            dry_run=dry_run, 
            similarity_threshold=args.threshold
        )
        
        if success > 0:
            if dry_run:
                print(f"\n💡 DRY RUN completed successfully!")
                print(f"   Would process {success} category attachments")
                print(f"   To actually make changes, run: python {os.path.basename(__file__)} --live")
            else:
                print(f"\n✅ LIVE RUN completed successfully!")
                print(f"   Processed {success} category attachments")
                print(f"   Images are now available via nginx")
            
            print(f"   📄 Full report: {report_file}")
        else:
            print(f"❌ No successful matches found. Check the report for details.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()