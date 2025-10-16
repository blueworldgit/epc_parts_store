#!/usr/bin/env python
"""
Convert Category Images to Static Files
Moves images from media/ to static/ and updates Django models to use static URLs
This improves performance by leveraging Django's static file optimization
"""
import os
import django
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category
from django.conf import settings
from django.templatetags.static import static

def convert_media_to_static_images(dry_run=True):
    """
    Convert category images from media files to static files
    """
    
    print(f"🔄 Convert Category Images: Media → Static Files")
    print(f"Mode: {'🔍 DRY RUN (preview only)' if dry_run else '🚀 LIVE (making changes)'}")
    print("="*70)
    
    # Paths
    current_media_path = Path(settings.MEDIA_ROOT) / "categories"
    static_images_path = Path(settings.BASE_DIR) / "static" / "images" / "categories"
    
    print(f"📁 Paths:")
    print(f"   Current (Media): {current_media_path}")
    print(f"   Target (Static): {static_images_path}")
    
    # Check if media folder exists
    if not current_media_path.exists():
        print(f"❌ Error: Media categories folder not found at {current_media_path}")
        return None
    
    # Create static folder if needed
    if not static_images_path.exists():
        print(f"📁 Creating static images folder: {static_images_path}")
        if not dry_run:
            static_images_path.mkdir(parents=True, exist_ok=True)
    
    # Get all image files in media/categories
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    media_images = []
    
    for file_path in current_media_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            media_images.append(file_path)
    
    print(f"📷 Found {len(media_images)} images in media/categories")
    
    if not media_images:
        print("❌ No images found to convert")
        return None
    
    # Get categories with images
    categories_with_images = Category.objects.exclude(image='')
    print(f"🏷️  Found {categories_with_images.count()} categories with images in database")
    
    # Process conversion
    converted_files = 0
    updated_categories = 0
    errors = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    mode_suffix = "_dry_run" if dry_run else "_live"
    report_filename = f'convert_to_static{mode_suffix}_{timestamp}.txt'
    
    print(f"📝 Generating report: {report_filename}")
    
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write(f"Convert Category Images to Static Files Report\n")
        report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        report.write("="*80 + "\n\n")
        
        report.write(f"PATHS:\n")
        report.write(f"Media folder: {current_media_path}\n")
        report.write(f"Static folder: {static_images_path}\n")
        report.write(f"Images found: {len(media_images)}\n")
        report.write(f"Categories with images: {categories_with_images.count()}\n\n")
        
        # Step 1: Copy files from media to static
        report.write("STEP 1: COPY FILES TO STATIC FOLDER\n")
        report.write("="*50 + "\n")
        
        for i, media_file in enumerate(media_images, 1):
            static_file = static_images_path / media_file.name
            
            try:
                if not dry_run:
                    # Copy file to static folder
                    shutil.copy2(media_file, static_file)
                
                converted_files += 1
                status = "✅ COPIED" if not dry_run else "✅ WOULD COPY"
                print(f"   {i:3d}. {status}: {media_file.name}")
                report.write(f"{i:3d}. {status}: {media_file.name}\n")
                report.write(f"     From: {media_file}\n")
                report.write(f"     To:   {static_file}\n")
                
            except Exception as e:
                error_msg = f"Error copying {media_file.name}: {str(e)}"
                errors.append(error_msg)
                print(f"   {i:3d}. ❌ ERROR: {str(e)}")
                report.write(f"{i:3d}. ❌ ERROR: {str(e)}\n")
        
        # Step 2: Update database to use static URLs
        report.write(f"\nSTEP 2: UPDATE DATABASE REFERENCES\n")
        report.write("="*50 + "\n")
        
        for i, category in enumerate(categories_with_images, 1):
            old_image_path = str(category.image)
            
            # Extract filename from current image path
            if old_image_path:
                image_filename = Path(old_image_path).name
                
                # Check if corresponding static file exists (or would exist)
                static_file_path = static_images_path / image_filename
                
                if static_file_path.exists() or dry_run:
                    # Update to use static file reference
                    # Instead of storing file path, we'll store just the filename
                    # Template will use {% static 'images/categories/' %}{{ category.image }}
                    
                    try:
                        if not dry_run:
                            # Clear the image field (we'll use a different approach)
                            # Store the filename in a custom field or use the slug
                            category.image = f"images/categories/{image_filename}"
                            category.save()
                        
                        updated_categories += 1
                        status = "✅ UPDATED" if not dry_run else "✅ WOULD UPDATE"
                        print(f"   {i:3d}. {status}: {category.name[:50]}...")
                        report.write(f"{i:3d}. {status}: {category.name}\n")
                        report.write(f"     Old: {old_image_path}\n")
                        report.write(f"     New: images/categories/{image_filename}\n")
                        
                    except Exception as e:
                        error_msg = f"Error updating category {category.name}: {str(e)}"
                        errors.append(error_msg)
                        print(f"   {i:3d}. ❌ ERROR: {str(e)}")
                        report.write(f"{i:3d}. ❌ ERROR: {str(e)}\n")
                else:
                    print(f"   {i:3d}. ⏭️ SKIPPED: {category.name[:50]}... (no static file)")
                    report.write(f"{i:3d}. ⏭️ SKIPPED: {category.name} (no static file found)\n")
        
        # Summary
        report.write(f"\n{'='*80}\n")
        report.write(f"SUMMARY:\n")
        report.write(f"{'='*80}\n")
        report.write(f"Files copied: {converted_files}/{len(media_images)}\n")
        report.write(f"Categories updated: {updated_categories}/{categories_with_images.count()}\n")
        report.write(f"Errors: {len(errors)}\n")
        
        if errors:
            report.write(f"\nERRORS:\n")
            report.write("-"*20 + "\n")
            for error in errors:
                report.write(f"• {error}\n")
        
        if dry_run:
            report.write(f"\n⚠️ THIS WAS A DRY RUN - NO CHANGES WERE MADE\n")
            report.write(f"To actually convert files, run with --live flag\n")
        else:
            report.write(f"\n✅ CONVERSION COMPLETED!\n")
            report.write(f"Next steps:\n")
            report.write(f"1. Run: python manage.py collectstatic\n")
            report.write(f"2. Update templates to use static URLs\n")
            report.write(f"3. Test image loading on site\n")
    
    print(f"\n📊 Final Results:")
    print(f"   Files converted: {converted_files}/{len(media_images)}")
    print(f"   Categories updated: {updated_categories}/{categories_with_images.count()}")
    print(f"   Errors: {len(errors)}")
    
    if dry_run:
        print(f"\n⚠️ THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        print(f"   To actually convert, run with --live flag")
        print(f"   Then run: python manage.py collectstatic")
    else:
        print(f"\n✅ CONVERSION COMPLETED!")
        print(f"   📁 Images copied to: {static_images_path}")
        print(f"   🔄 Next: python manage.py collectstatic")
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    return report_filename, converted_files, len(errors)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Convert Category Images from Media to Static Files',
        epilog="""
Examples:
  python convert_to_static_images.py                    # Dry run (safe preview)
  python convert_to_static_images.py --live             # Live conversion
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
        help='Actually convert files and update database'
    )
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.live
    
    print("🔄 Convert Category Images: Media → Static Files")
    print("="*60)
    print(f"Mode: {'🔍 DRY RUN (preview only)' if dry_run else '🚀 LIVE (making changes)'}")
    
    if dry_run:
        print("💡 TIP: Add --live flag to actually convert files")
    else:
        print("⚠️  WARNING: This will move files and modify the database!")
        response = input("Continue? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            exit(0)
    
    print()
    
    try:
        report_file, converted, errors = convert_media_to_static_images(dry_run=dry_run)
        
        if converted > 0:
            if dry_run:
                print(f"\n💡 DRY RUN completed successfully!")
                print(f"   Would convert {converted} image files")
                print(f"   To actually convert: python convert_to_static_images.py --live")
            else:
                print(f"\n✅ CONVERSION completed successfully!")
                print(f"   Converted {converted} image files")
                print(f"   🔄 Now run: python manage.py collectstatic")
            
            print(f"   📄 Full report: {report_file}")
        else:
            print(f"❌ No files converted. Check the report for details.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()