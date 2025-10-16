#!/usr/bin/env python
"""
Check Categories Without Images
Shows which unique category names still don't have images attached
"""
import os
import django
from datetime import datetime
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from oscar.apps.catalogue.models import Category

def clean_category_name(name):
    """Clean category name same way as other scripts"""
    if name and " - " in name:
        return name.split(" - ", 1)[1].strip()
    return name.strip() if name else ""

def check_categories_without_images():
    """Check which unique category names don't have images"""
    
    print("🔍 Checking categories without images...")
    
    # Get all categories and group by cleaned name
    categories = Category.objects.all()
    category_groups = {}  # Maps cleaned name to list of categories
    
    for cat in categories:
        if cat.name:
            clean_name = clean_category_name(cat.name)
            if clean_name not in category_groups:
                category_groups[clean_name] = []
            category_groups[clean_name].append(cat)
    
    print(f"🏷️  Found {len(category_groups)} unique category names")
    
    # Check which categories have/don't have images
    categories_with_images = set()
    categories_without_images = set()
    detailed_results = []
    
    for clean_name, cat_list in category_groups.items():
        has_image = False
        image_count = 0
        no_image_count = 0
        sample_categories = []
        
        for cat in cat_list:
            sample_categories.append({
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'has_image': bool(cat.image)
            })
            
            if cat.image:
                has_image = True
                image_count += 1
            else:
                no_image_count += 1
        
        if has_image:
            categories_with_images.add(clean_name)
        else:
            categories_without_images.add(clean_name)
        
        detailed_results.append({
            'clean_name': clean_name,
            'has_image': has_image,
            'total_categories': len(cat_list),
            'with_images': image_count,
            'without_images': no_image_count,
            'sample_categories': sample_categories[:5]  # Show first 5 as samples
        })
    
    # Sort results
    detailed_results.sort(key=lambda x: (x['has_image'], x['clean_name']))
    categories_without_images = sorted(list(categories_without_images))
    categories_with_images = sorted(list(categories_with_images))
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'categories_without_images_{timestamp}.txt'
    
    print(f"📊 Analysis Results:")
    print(f"   ✅ Categories WITH images: {len(categories_with_images)}")
    print(f"   ❌ Categories WITHOUT images: {len(categories_without_images)}")
    print(f"   📊 Coverage: {(len(categories_with_images)/len(category_groups)*100):.1f}%")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Categories Without Images Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"SUMMARY:\n")
        f.write(f"Total unique category names: {len(category_groups)}\n")
        f.write(f"Categories WITH images: {len(categories_with_images)}\n")
        f.write(f"Categories WITHOUT images: {len(categories_without_images)}\n")
        f.write(f"Coverage: {(len(categories_with_images)/len(category_groups)*100):.1f}%\n\n")
        
        # Categories WITHOUT images (priority list)
        f.write("="*80 + "\n")
        f.write("CATEGORIES WITHOUT IMAGES (Need attention!):\n")
        f.write("="*80 + "\n")
        
        without_image_results = [r for r in detailed_results if not r['has_image']]
        
        if without_image_results:
            for i, result in enumerate(without_image_results, 1):
                f.write(f"\n{i:3d}. {result['clean_name']}\n")
                f.write(f"     Total instances: {result['total_categories']}\n")
                f.write(f"     Sample categories:\n")
                
                for j, sample in enumerate(result['sample_categories'], 1):
                    f.write(f"       {j}. {sample['name']} (ID: {sample['id']})\n")
                
                print(f"❌ {i:3d}. {result['clean_name']} ({result['total_categories']} instances)")
        else:
            f.write("    🎉 All categories have images!\n")
        
        # Categories WITH images (success list)
        f.write(f"\n{'='*80}\n")
        f.write("CATEGORIES WITH IMAGES (Success!):\n")
        f.write("="*80 + "\n")
        
        with_image_results = [r for r in detailed_results if r['has_image']]
        
        for i, result in enumerate(with_image_results, 1):
            coverage = f"({result['with_images']}/{result['total_categories']})" if result['without_images'] > 0 else "(all)"
            f.write(f"{i:3d}. {result['clean_name']} {coverage}\n")
        
        # Detailed breakdown
        f.write(f"\n{'='*80}\n")
        f.write("DETAILED BREAKDOWN:\n")
        f.write("="*80 + "\n")
        
        for result in detailed_results:
            status = "✅ HAS IMAGES" if result['has_image'] else "❌ NO IMAGES"
            f.write(f"\n{status}: {result['clean_name']}\n")
            f.write(f"   Total categories: {result['total_categories']}\n")
            f.write(f"   With images: {result['with_images']}\n")
            f.write(f"   Without images: {result['without_images']}\n")
            
            if result['sample_categories']:
                f.write(f"   Sample categories:\n")
                for sample in result['sample_categories']:
                    img_status = "📷" if sample['has_image'] else "❌"
                    f.write(f"     {img_status} {sample['name']}\n")
        
        # Recommendations
        f.write(f"\n{'='*80}\n")
        f.write("RECOMMENDATIONS:\n")
        f.write("="*80 + "\n")
        
        if without_image_results:
            f.write(f"1. PRIORITY: Add images for {len(without_image_results)} category types\n")
            f.write(f"2. Focus on categories with multiple instances first\n")
            f.write(f"3. Create/source images with names matching the category names\n")
            f.write(f"4. Use the bulk_attach_images.py script to attach them\n")
            f.write(f"5. Re-run this script to verify improvements\n\n")
            
            # Top priorities (by instance count)
            priority_list = sorted(without_image_results, key=lambda x: x['total_categories'], reverse=True)[:10]
            f.write(f"TOP PRIORITY CATEGORIES (by instance count):\n")
            for i, result in enumerate(priority_list, 1):
                f.write(f"   {i}. {result['clean_name']} ({result['total_categories']} instances)\n")
        else:
            f.write(f"🎉 CONGRATULATIONS! All category types have images!\n")
            f.write(f"Your category thumbnail system is 100% complete.\n")
    
    print(f"\n✅ Report saved to: {filename}")
    
    return filename, len(categories_without_images), len(categories_with_images)

def get_image_statistics():
    """Get overall image statistics"""
    
    total_categories = Category.objects.count()
    categories_with_images = Category.objects.filter(image__isnull=False).exclude(image='').count()
    categories_without_images = total_categories - categories_with_images
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total category records: {total_categories}")
    print(f"   Records with images: {categories_with_images}")
    print(f"   Records without images: {categories_without_images}")
    print(f"   Record coverage: {(categories_with_images/total_categories*100):.1f}%")

if __name__ == "__main__":
    print("🖼️  Categories Without Images Checker")
    print("="*50)
    
    try:
        # Check categories without images
        filename, without_count, with_count = check_categories_without_images()
        
        # Show overall statistics
        get_image_statistics()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Report file: {filename}")
        print(f"   Unique categories WITHOUT images: {without_count}")
        print(f"   Unique categories WITH images: {with_count}")
        
        if without_count > 0:
            print(f"\n💡 Next steps:")
            print(f"   1. Review categories without images in {filename}")
            print(f"   2. Create/source images for missing categories")
            print(f"   3. Name images to match category names exactly")
            print(f"   4. Add images to Rentals folder")
            print(f"   5. Run bulk_attach_images.py to attach them")
        else:
            print(f"\n🎉 All unique categories have images! System is complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()