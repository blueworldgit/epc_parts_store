#!/usr/bin/env python3
"""
Script to verify all CSS files exist and fix 404 errors
"""

from pathlib import Path

def check_css_files():
    """Check if all required CSS files exist"""
    print("🎨 Checking CSS Files")
    print("=" * 40)
    
    BASE_DIR = Path(__file__).resolve().parent
    
    # CSS files that should exist
    css_files = [
        {
            'name': 'Main Style CSS',
            'source': BASE_DIR / 'motortemplate' / 'uren' / 'assets' / 'css' / 'style.css',
            'static': BASE_DIR / 'staticfiles' / 'uren' / 'assets' / 'css' / 'style.css',
            'url': '/static/uren/assets/css/style.css'
        },
        {
            'name': 'Custom CSS',
            'source': BASE_DIR / 'motortemplate' / 'uren' / 'assets' / 'css' / 'custom.css',
            'static': BASE_DIR / 'staticfiles' / 'uren' / 'assets' / 'css' / 'custom.css',
            'url': '/static/uren/assets/css/custom.css'
        }
    ]
    
    all_good = True
    
    for css in css_files:
        print(f"\n📄 {css['name']}:")
        
        # Check source file
        if css['source'].exists():
            size = css['source'].stat().st_size
            print(f"  ✅ Source: {css['source']} ({size:,} bytes)")
        else:
            print(f"  ❌ Source missing: {css['source']}")
            all_good = False
        
        # Check static file
        if css['static'].exists():
            size = css['static'].stat().st_size
            print(f"  ✅ Static: {css['static']} ({size:,} bytes)")
        else:
            print(f"  ❌ Static missing: {css['static']}")
            all_good = False
        
        print(f"  🌐 URL: {css['url']}")
    
    # Check media file
    print(f"\n🖼️ Media File:")
    media_file = BASE_DIR / 'media' / 'images' / 'breadcrumb-van-interior.jpg'
    if media_file.exists():
        size = media_file.stat().st_size
        print(f"  ✅ Breadcrumb image: {media_file} ({size:,} bytes)")
        print(f"  🌐 URL: /media/images/breadcrumb-van-interior.jpg")
    else:
        print(f"  ❌ Missing: {media_file}")
        all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All files exist! No more 404 errors expected.")
        print("\n💡 If you still get 404s:")
        print("1. Restart Django development server")
        print("2. Clear browser cache (Ctrl+F5)")
        print("3. Check Django console for actual file requests")
    else:
        print("⚠️ Some files are missing - this will cause 404 errors")
        print("\n🔧 To fix:")
        print("1. Run: python manage.py collectstatic")
        print("2. Restart Django server")
    
    return all_good

if __name__ == "__main__":
    check_css_files()