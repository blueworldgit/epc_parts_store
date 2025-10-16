#!/usr/bin/env python
"""
Cross-reference script to match image files with category names
Shows exact matches, close matches, and mismatches
"""
import os
import django
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def clean_category_name(name):
    """Clean category name same way as the unique names script"""
    if name and " - " in name:
        return name.split(" - ", 1)[1].strip()
    return name.strip() if name else ""

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def cross_reference_images_categories():
    """Cross-reference image files with category names"""
    
    print("🔍 Cross-referencing images with categories...")
    
    # Get image files from Rentals folder
    rentals_folder = Path("../Rentals")
    if not rentals_folder.exists():
        print(f"❌ Error: Folder {rentals_folder.resolve()} does not exist!")
        return None
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for file_path in rentals_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path.stem)  # filename without extension
    
    image_files.sort()
    
    # Get unique category names (cleaned)
    categories = Category.objects.all()
    unique_category_names = set()
    category_mapping = {}  # Maps cleaned name to list of original categories
    
    for cat in categories:
        if cat.name:
            clean_name = clean_category_name(cat.name)
            unique_category_names.add(clean_name)
            
            if clean_name not in category_mapping:
                category_mapping[clean_name] = []
            category_mapping[clean_name].append(cat)
    
    unique_category_names = sorted(list(unique_category_names))
    
    # Perform matching
    exact_matches = []
    close_matches = []
    no_matches = []
    
    for image_name in image_files:
        best_match = None
        best_score = 0
        
        # Check for exact match first
        if image_name in unique_category_names:
            exact_matches.append({
                'image': image_name,
                'category': image_name,
                'categories_count': len(category_mapping[image_name])
            })
        else:
            # Find best similarity match
            for cat_name in unique_category_names:
                score = similarity(image_name, cat_name)
                if score > best_score:
                    best_score = score
                    best_match = cat_name
            
            if best_score > 0.7:  # 70% similarity threshold
                close_matches.append({
                    'image': image_name,
                    'category': best_match,
                    'similarity': best_score,
                    'categories_count': len(category_mapping[best_match])
                })
            else:
                no_matches.append({
                    'image': image_name,
                    'best_match': best_match,
                    'similarity': best_score
                })
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'image_category_cross_reference_{timestamp}.txt'
    
    print(f"📊 Analysis Results:")
    print(f"   📷 Total images: {len(image_files)}")
    print(f"   🏷️  Total unique categories: {len(unique_category_names)}")
    print(f"   ✅ Exact matches: {len(exact_matches)}")
    print(f"   🔄 Close matches (>70%): {len(close_matches)}")
    print(f"   ❌ No good matches: {len(no_matches)}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Image-Category Cross Reference Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"Total images: {len(image_files)}\n")
        f.write(f"Total unique categories: {len(unique_category_names)}\n")
        f.write(f"Exact matches: {len(exact_matches)}\n")
        f.write(f"Close matches (>70%): {len(close_matches)}\n")
        f.write(f"No good matches: {len(no_matches)}\n\n")
        
        # Exact matches
        f.write("="*80 + "\n")
        f.write("EXACT MATCHES (Ready to attach!):\n")
        f.write("="*80 + "\n")
        for i, match in enumerate(exact_matches, 1):
            f.write(f"{i:3d}. '{match['image']}.png' → '{match['category']}' ({match['categories_count']} categories)\n")
            print(f"✅ {match['image']}.png → {match['category']} ({match['categories_count']} categories)")
        
        if not exact_matches:
            f.write("    No exact matches found.\n")
        
        # Close matches
        f.write(f"\n{'='*80}\n")
        f.write("CLOSE MATCHES (May need renaming):\n")
        f.write("="*80 + "\n")
        for i, match in enumerate(close_matches, 1):
            f.write(f"{i:3d}. '{match['image']}.png' → '{match['category']}' (similarity: {match['similarity']:.1%})\n")
            f.write(f"     Will attach to {match['categories_count']} categories\n")
            print(f"🔄 {match['image']}.png → {match['category']} ({match['similarity']:.1%})")
        
        if not close_matches:
            f.write("    No close matches found.\n")
        
        # No matches
        f.write(f"\n{'='*80}\n")
        f.write("NO GOOD MATCHES (Need manual review):\n")
        f.write("="*80 + "\n")
        for i, item in enumerate(no_matches, 1):
            f.write(f"{i:3d}. '{item['image']}.png' (best: '{item['best_match']}' at {item['similarity']:.1%})\n")
            print(f"❌ {item['image']}.png (no good match)")
        
        if not no_matches:
            f.write("    All images have good matches!\n")
        
        # Categories without images
        categories_with_images = set([m['category'] for m in exact_matches + close_matches])
        categories_without_images = [cat for cat in unique_category_names if cat not in categories_with_images]
        
        f.write(f"\n{'='*80}\n")
        f.write(f"CATEGORIES WITHOUT MATCHING IMAGES ({len(categories_without_images)}):\n")
        f.write("="*80 + "\n")
        for i, cat in enumerate(categories_without_images[:20], 1):  # Show first 20
            f.write(f"{i:3d}. {cat}\n")
        
        if len(categories_without_images) > 20:
            f.write(f"... and {len(categories_without_images) - 20} more\n")
        
        # Recommendations
        f.write(f"\n{'='*80}\n")
        f.write("RECOMMENDATIONS:\n")
        f.write("="*80 + "\n")
        f.write(f"1. READY TO ATTACH: {len(exact_matches)} images can be attached immediately\n")
        f.write(f"2. REVIEW CLOSE MATCHES: {len(close_matches)} images may need renaming for exact match\n")
        f.write(f"3. MANUAL REVIEW: {len(no_matches)} images need manual review/renaming\n")
        f.write(f"4. MISSING IMAGES: {len(categories_without_images)} categories still need images\n")
    
    print(f"\n✅ Cross-reference report saved to: {filename}")
    
    return filename, len(exact_matches), len(close_matches), len(no_matches)

if __name__ == "__main__":
    print("🔄 Image-Category Cross Reference Tool")
    print("="*50)
    
    try:
        filename, exact, close, none = cross_reference_images_categories()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Report file: {filename}")
        print(f"   Ready to attach: {exact} images")
        print(f"   Need review: {close + none} images")
        
        if exact > 0:
            print(f"\n💡 Next step: Run bulk image attachment script for {exact} exact matches!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()