#!/usr/bin/env python3
"""
Test script to verify media configuration and breadcrumb image setup
"""

import os
from pathlib import Path

def test_media_setup():
    """Test if media configuration is correct"""
    print("🔍 Testing Media Configuration")
    print("=" * 50)
    
    # Get Django project paths
    BASE_DIR = Path(__file__).resolve().parent
    MEDIA_DIR = BASE_DIR / 'media' / 'images'
    IMAGE_PATH = MEDIA_DIR / 'breadcrumb-van-interior.jpg'
    
    print(f"📂 Base directory: {BASE_DIR}")
    print(f"📁 Media directory: {MEDIA_DIR}")
    print(f"🖼️ Image path: {IMAGE_PATH}")
    
    # Check if directories exist
    if MEDIA_DIR.exists():
        print("✅ Media directory exists")
    else:
        print("❌ Media directory missing")
        return False
    
    # Check if image exists
    if IMAGE_PATH.exists():
        size = IMAGE_PATH.stat().st_size
        print(f"✅ Breadcrumb image exists ({size:,} bytes)")
        
        # Check if it's a valid image size
        if size > 1000:
            print("✅ Image size looks good")
        else:
            print("⚠️ Image might be too small or corrupted")
            
    else:
        print("❌ Breadcrumb image missing")
        return False
    
    # Test URL path
    expected_url = "/media/images/breadcrumb-van-interior.jpg"
    print(f"🌐 Expected URL: {expected_url}")
    
    # Check CSS files for the reference
    css_files = [
        BASE_DIR / 'motortemplate' / 'uren' / 'assets' / 'css' / 'style.css',
        BASE_DIR / 'staticfiles' / 'uren' / 'assets' / 'css' / 'style.css'
    ]
    
    print("\n🎨 Checking CSS files:")
    for css_file in css_files:
        if css_file.exists():
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'breadcrumb-van-interior.jpg' in content:
                        print(f"✅ {css_file.name} references the image correctly")
                    else:
                        print(f"❌ {css_file.name} doesn't reference the image")
            except Exception as e:
                print(f"⚠️ Error reading {css_file.name}: {e}")
        else:
            print(f"❌ {css_file.name} not found")
    
    print("\n" + "=" * 50)
    print("🎯 SOLUTIONS:")
    print("1. Make sure Django DEBUG=True for development media serving")
    print("2. Check your Django URLs include media file serving")
    print("3. Refresh your browser cache (Ctrl+F5)")
    print("4. Check Django console for media file requests")
    
    return True

if __name__ == "__main__":
    test_media_setup()