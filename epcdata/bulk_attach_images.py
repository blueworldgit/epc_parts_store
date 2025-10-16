#!/usr/bin/env python
"""
Bulk Image Attachment Script
Attaches images from Rentals folder to matching Oscar categories across all serials
"""
import os
import django
from datetime import datetime
from pathlib import Path
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
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def bulk_attach_images(dry_run=True, similarity_threshold=0.6):
    """
    Attach images to categories
    dry_run=True: Show what would happen without making changes
    dry_run=False: Actually attach the images
    similarity_threshold: Minimum similarity to consider a match (0.6 = 60%)
    """
    
    print(f"🔄 Bulk Image Attachment Script")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will make changes)'}")
    print(f"Similarity threshold: {similarity_threshold*100:.0f}%")
    print("="*70)
    
    # Get image files from Rentals folder
    rentals_folder = Path("../Rentals")
    if not rentals_folder.exists():
        print(f"❌ Error: Folder {rentals_folder.resolve()} does not exist!")
        return None
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    available_images = {}
    
    for file_path in rentals_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_name = file_path.stem  # filename without extension
            available_images[image_name] = file_path
    
    print(f"📷 Found {len(available_images)} images in Rentals folder")
    
    # Get all categories and group by cleaned name
    categories = Category.objects.all()
    category_groups = {}  # Maps cleaned name to list of categories
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
    
    # Find matches between images and categories (exact + similarity)
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
    errors = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    mode_suffix = "_dry_run" if dry_run else "_live"
    threshold_suffix = f"_{int(similarity_threshold*100)}pct"
    report_filename = f'bulk_image_attachment{mode_suffix}{threshold_suffix}_{timestamp}.txt'
    
    print(f"📝 Generating report: {report_filename}")
    
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write(f"Bulk Image Attachment Report\n")
        report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
        report.write(f"Similarity threshold: {similarity_threshold*100:.0f}%\n")
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
            
            if match_type == 'exact':
                print(f"\n{i:3d}. Processing '{image_name}' (EXACT match)...")
                report.write(f"\n{i:3d}. Image: {image_name}.png (EXACT MATCH)\n")
            else:
                matched_name = match['matched_category_name']
                print(f"\n{i:3d}. Processing '{image_name}' → '{matched_name}' ({similarity_score:.1%})...")
                report.write(f"\n{i:3d}. Image: {image_name}.png → {matched_name} ({similarity_score:.1%})\n")
            
            report.write(f"     Path: {image_path}\n")
            report.write(f"     Categories to update: {len(categories)}\n")
            
            for j, category in enumerate(categories, 1):
                total_attachments += 1
                
                try:
                    if not dry_run:
                        # Actually attach the image
                        with open(image_path, 'rb') as img_file:
                            category.image.save(
                                f"{image_name}.png",
                                ImageFile(img_file),
                                save=True
                            )
                    
                    successful_attachments += 1
                    status = "✅ ATTACHED" if not dry_run else "✅ WOULD ATTACH"
                    print(f"     {j}. {status}: {category.name[:60]}...")
                    report.write(f"       {j}. {status}: {category.name}\n")
                    report.write(f"          ID: {category.id}, Slug: {category.slug}\n")
                    
                except Exception as e:
                    error_msg = f"Error attaching to {category.name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"     {j}. ❌ ERROR: {str(e)}")
                    report.write(f"       {j}. ❌ ERROR: {str(e)}\n")
        
        # Summary section
        report.write(f"\n{'='*80}\n")
        report.write(f"FINAL SUMMARY:\n")
        report.write(f"{'='*80}\n")
        report.write(f"Total attachment operations: {total_attachments}\n")
        report.write(f"Successful: {successful_attachments}\n")
        report.write(f"Errors: {len(errors)}\n")
        report.write(f"Success rate: {(successful_attachments/total_attachments*100):.1f}%\n")
        
        if errors:
            report.write(f"\nERRORS:\n")
            report.write("-"*20 + "\n")
            for error in errors:
                report.write(f"• {error}\n")
        
        if dry_run:
            report.write(f"\n⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE\n")
            report.write(f"To actually attach images, run with dry_run=False\n")
    
    print(f"\n📊 Final Results:")
    print(f"   Total operations: {total_attachments}")
    print(f"   Successful: {successful_attachments}")
    print(f"   Errors: {len(errors)}")
    print(f"   Success rate: {(successful_attachments/total_attachments*100):.1f}%")
    
    if dry_run:
        print(f"\n⚠️  THIS WAS A DRY RUN - NO CHANGES WERE MADE")
        print(f"   Review the report and run with dry_run=False to actually attach images")
    else:
        print(f"\n✅ LIVE RUN COMPLETED - Images have been attached!")
    
    print(f"\n📄 Full report saved to: {report_filename}")
    
    return report_filename, successful_attachments, len(errors)

if __name__ == "__main__":
    print("🖼️  Bulk Image Attachment Tool")
    print("="*50)
    
    try:
        # First run with 60% similarity threshold
        print("🚀 Running LIVE MODE to attach images (≥60% similarity)...")
        report_file, success, errors = bulk_attach_images(dry_run=False, similarity_threshold=0.6)
        
        if success > 0:
            print(f"\n💡 LIVE RUN completed successfully!")
            print(f"   Attached images to {success} categories")
            print(f"   Review report: {report_file}")
        else:
            print(f"❌ No successful matches found. Check the report for details.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()