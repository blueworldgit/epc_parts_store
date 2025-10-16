#!/usr/bin/env python
"""
List all image files in the Rentals folder for cross-referencing with category names
"""
import os
from datetime import datetime
from pathlib import Path

def list_rental_images():
    """List all image files in the Rentals folder"""
    
    # Define the rentals folder path
    rentals_folder = Path("../Rentals")  # Relative to epcdata directory
    
    print(f"🔍 Scanning folder: {rentals_folder.resolve()}")
    
    if not rentals_folder.exists():
        print(f"❌ Error: Folder {rentals_folder.resolve()} does not exist!")
        return None, 0
    
    # Common image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    # Get all files in the folder
    all_files = []
    image_files = []
    
    for file_path in rentals_folder.iterdir():
        if file_path.is_file():
            all_files.append(file_path.name)
            if file_path.suffix.lower() in image_extensions:
                image_files.append(file_path.name)
    
    # Sort the lists
    all_files.sort()
    image_files.sort()
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'rentals_folder_contents_{timestamp}.txt'
    
    print(f"📝 Found {len(all_files)} total files")
    print(f"📷 Found {len(image_files)} image files")
    print(f"📄 Saving to: {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Rentals Folder Contents Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Folder: {rentals_folder.resolve()}\n")
        f.write(f"Total files: {len(all_files)}\n")
        f.write(f"Image files: {len(image_files)}\n")
        f.write("="*80 + "\n\n")
        
        # List all image files
        f.write("IMAGE FILES (for category matching):\n")
        f.write("-" * 50 + "\n")
        for i, img_file in enumerate(image_files, 1):
            # Show filename and what it would match (without extension)
            base_name = Path(img_file).stem  # filename without extension
            f.write(f"{i:3d}. {img_file:<40} → matches '{base_name}'\n")
            print(f"{i:3d}. {img_file:<40} → matches '{base_name}'")
        
        if not image_files:
            f.write("    No image files found!\n")
            print("    No image files found!")
        
        # List all files (for reference)
        f.write(f"\n\nALL FILES IN FOLDER:\n")
        f.write("-" * 50 + "\n")
        for i, file_name in enumerate(all_files, 1):
            file_path = rentals_folder / file_name
            file_size = file_path.stat().st_size if file_path.exists() else 0
            file_size_kb = file_size / 1024
            f.write(f"{i:3d}. {file_name:<40} ({file_size_kb:.1f} KB)\n")
        
        # Summary
        f.write(f"\n\nSUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Folder scanned: {rentals_folder.resolve()}\n")
        f.write(f"Total files: {len(all_files)}\n")
        f.write(f"Image files: {len(image_files)}\n")
        f.write(f"Supported extensions: {', '.join(sorted(image_extensions))}\n")
        
        if image_files:
            f.write(f"\nNext step: Compare these image names with category names\n")
            f.write(f"from unique_category_names_*.txt to see matches\n")
    
    print(f"\n✅ Report saved to: {filename}")
    
    if image_files:
        print(f"\n💡 Next steps:")
        print(f"   1. Review the image files in {filename}")
        print(f"   2. Compare with category names from unique_category_names_*.txt")
        print(f"   3. Rename any images that don't match category names")
        print(f"   4. Run the bulk image attachment script")
    else:
        print(f"\n⚠️  No image files found in {rentals_folder.resolve()}")
        print(f"   Please check the folder path and add some images")
    
    return filename, len(image_files)

def show_folder_structure():
    """Show the current directory structure for context"""
    current_dir = Path.cwd()
    print(f"\n📁 Current directory: {current_dir}")
    print(f"📁 Looking for Rentals at: {(current_dir / '../Rentals').resolve()}")
    
    # Check if folder exists
    rentals_path = Path("../Rentals")
    if rentals_path.exists():
        print(f"✅ Rentals folder found!")
    else:
        print(f"❌ Rentals folder not found!")
        print(f"   Expected at: {rentals_path.resolve()}")

if __name__ == "__main__":
    print("📂 Rentals Folder Image Scanner")
    print("="*50)
    
    try:
        # Show folder context
        show_folder_structure()
        
        # List the images
        filename, count = list_rental_images()
        
        print(f"\n🎯 SUMMARY:")
        if filename:
            print(f"   Report file: {filename}")
            print(f"   Image files found: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()