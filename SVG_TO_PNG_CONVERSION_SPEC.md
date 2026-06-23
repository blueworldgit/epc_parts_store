# SVG to PNG Conversion - Technical Specification

## Overview
This document specifies the requirements for converting SVG diagrams from HTML files into PNG images for WooCommerce product galleries.

---

## Input Specifications

### Source Files
- **Location**: HTML files in nested directory structure
- **Format**: HTML5 with embedded SVG elements
- **SVG Namespace**: `xmlns="http://www.w3.org/2000/svg"`
- **SVG Location**: Within `<svg>` tag in HTML body

### Directory Structure
```
LSFAL11A4PA157987/
  ├── category_name/
  │   ├── diagram1.html
  │   ├── diagram2.html
  │   └── ...
  └── another_category/
      └── diagram3.html
```

---

## Output Specifications

### Image Format: PNG
**Why PNG over JPG**:
- Lossless compression (no quality degradation)
- Sharp text rendering (callout numbers remain crisp)
- Better for line drawings and technical diagrams
- Transparency support (if needed)
- No compression artifacts around edges

### Output Resolutions

#### Full-Size Image
- **Width**: 2000 pixels
- **Aspect Ratio**: Preserved from original SVG
- **Use Case**: Product main image, lightbox zoom
- **Naming**: `{original_filename}.png`
- **Estimated Size**: 300-800 KB per file

#### Thumbnail Image
- **Width**: 600 pixels
- **Aspect Ratio**: Preserved from original SVG
- **Use Case**: Product gallery thumbnails, category listings
- **Naming**: `{original_filename}_thumb.png`
- **Estimated Size**: 50-150 KB per file

#### Optional: Medium Size
- **Width**: 1200 pixels
- **Aspect Ratio**: Preserved from original SVG
- **Use Case**: Product page default view (before zoom)
- **Naming**: `{original_filename}_medium.png`
- **Estimated Size**: 150-400 KB per file

### Output Directory Structure
Mirror input structure for easy reference:
```
converted_images/
  ├── LSFAL11A4PA157987/
  │   ├── air_intake_system/
  │   │   ├── air_filter.png
  │   │   ├── air_filter_thumb.png
  │   │   └── intake_manifold.png
  │   └── brakes/
  │       ├── front_brakes.png
  │       └── front_brakes_thumb.png
  └── conversion_metadata.json
```

---

## Technical Implementation

### Python Libraries

#### Primary: cairosvg
```python
import cairosvg

# Advantages:
# - Excellent SVG standard compliance
# - Handles complex SVG features
# - Direct SVG → PNG conversion
# - Good text rendering

# Installation:
pip install cairosvg

# Dependencies (Windows):
# - GTK+ runtime (included with pycairo)
# - Cairo graphics library
```

#### Alternative: svglib + reportlab
```python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Advantages:
# - Pure Python (easier Windows install)
# - No C dependencies

# Disadvantages:
# - Limited SVG feature support
# - May not handle complex SVGs well
```

#### Fallback: Selenium + Chrome Headless
```python
from selenium import webdriver

# Last resort if SVG libraries fail
# Render HTML in browser, screenshot
# Slow but guaranteed to work
```

### Conversion Algorithm

```python
def extract_svg_from_html(html_path):
    """
    Extract SVG element from HTML file
    
    Returns:
        str: Raw SVG markup as string
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    svg = soup.find('svg', attrs={"xmlns": "http://www.w3.org/2000/svg"})
    
    if not svg:
        raise ValueError(f"No SVG found in {html_path}")
    
    return str(svg)


def convert_svg_to_png(svg_string, output_path, width):
    """
    Convert SVG string to PNG file
    
    Args:
        svg_string (str): Complete SVG markup
        output_path (str): Where to save PNG
        width (int): Output width in pixels
    
    Returns:
        dict: Metadata about conversion
    """
    try:
        # Convert using cairosvg
        cairosvg.svg2png(
            bytestring=svg_string.encode('utf-8'),
            write_to=output_path,
            output_width=width,
            background_color='white'  # Fill transparent areas
        )
        
        # Get actual dimensions
        from PIL import Image
        img = Image.open(output_path)
        
        return {
            "success": True,
            "output_path": output_path,
            "width": img.width,
            "height": img.height,
            "size_bytes": os.path.getsize(output_path)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def process_html_file(html_path, output_dir, sizes=[2000, 600]):
    """
    Process one HTML file: extract SVG, create multiple PNG sizes
    
    Args:
        html_path (str): Path to HTML file
        output_dir (str): Base output directory
        sizes (list): List of widths to generate
    
    Returns:
        dict: Results for this file
    """
    # Extract SVG
    svg_string = extract_svg_from_html(html_path)
    
    # Get output filename (without .html)
    base_name = os.path.splitext(os.path.basename(html_path))[0]
    
    # Create output subdirectory
    rel_dir = os.path.relpath(os.path.dirname(html_path), ROOT_DATA_DIR)
    out_subdir = os.path.join(output_dir, rel_dir)
    os.makedirs(out_subdir, exist_ok=True)
    
    results = {
        "source": html_path,
        "conversions": []
    }
    
    # Convert to each size
    for width in sizes:
        suffix = "_thumb" if width == 600 else ""
        output_path = os.path.join(out_subdir, f"{base_name}{suffix}.png")
        
        result = convert_svg_to_png(svg_string, output_path, width)
        results["conversions"].append({
            "width": width,
            **result
        })
    
    return results
```

---

## Conversion Settings

### Image Quality
```python
CONVERSION_SETTINGS = {
    "full_size": {
        "width": 2000,
        "background": "white",
        "dpi": 300,  # High quality
        "compression": 6  # PNG compression level (0-9)
    },
    "thumbnail": {
        "width": 600,
        "background": "white",
        "dpi": 150,
        "compression": 6
    }
}
```

### Performance Settings
```python
BATCH_SETTINGS = {
    "parallel_processes": 4,  # Process multiple files simultaneously
    "progress_interval": 10,  # Log progress every N files
    "checkpoint_interval": 50,  # Save checkpoint every N files
    "skip_existing": True  # Don't reconvert existing PNGs
}
```

---

## Error Handling

### Error Categories

#### 1. Missing SVG
```python
# HTML file exists but no SVG element found
# Action: Log warning, skip file, continue processing
{
    "error_type": "missing_svg",
    "file": "path/to/file.html",
    "action": "skipped"
}
```

#### 2. Malformed SVG
```python
# SVG exists but invalid markup
# Action: Try alternative parser, if fails log error
{
    "error_type": "invalid_svg",
    "file": "path/to/file.html",
    "svg_sample": "first 100 chars of SVG",
    "action": "attempted_fallback"
}
```

#### 3. Conversion Failure
```python
# cairosvg raised exception
# Action: Try alternative method (svglib), log if all fail
{
    "error_type": "conversion_failed",
    "file": "path/to/file.html",
    "exception": "CairoError: ...",
    "fallback_tried": ["svglib", "selenium"],
    "action": "failed_all_methods"
}
```

#### 4. File System Errors
```python
# Can't write output file (permissions, disk space)
# Action: Stop processing, report error immediately
{
    "error_type": "filesystem",
    "file": "path/to/output.png",
    "exception": "PermissionError: ...",
    "action": "abort"
}
```

### Error Recovery
```python
def safe_convert_file(html_path, output_dir, retry_count=2):
    """
    Convert with retry logic and fallbacks
    """
    methods = [
        ('cairosvg', convert_with_cairosvg),
        ('svglib', convert_with_svglib),
        ('selenium', convert_with_selenium)
    ]
    
    for method_name, method_func in methods:
        for attempt in range(retry_count):
            try:
                result = method_func(html_path, output_dir)
                logger.info(f"Success with {method_name} (attempt {attempt+1})")
                return result
            except Exception as e:
                logger.warning(f"{method_name} failed: {e}")
                if method_name == methods[-1][0] and attempt == retry_count - 1:
                    # Last method, last attempt
                    logger.error(f"All conversion methods failed for {html_path}")
                    return {"success": False, "error": str(e)}
                continue
```

---

## Logging & Reporting

### Log Levels
- **DEBUG**: SVG extraction details, dimension calculations
- **INFO**: Successful conversions, progress updates
- **WARNING**: Non-critical issues (missing optional attributes)
- **ERROR**: Conversion failures, file system errors
- **CRITICAL**: Process-stopping errors (disk full, permissions)

### Log Output
```python
# File: conversion.log
2025-12-27 10:15:30 INFO Starting batch conversion
2025-12-27 10:15:30 INFO Found 150 HTML files to process
2025-12-27 10:15:31 INFO [1/150] Converting: air_intake_system/air_filter.html
2025-12-27 10:15:32 INFO [1/150] Success: 2000x1500px, 456KB
2025-12-27 10:15:32 INFO [1/150] Success: 600x450px, 78KB
2025-12-27 10:15:33 WARNING [2/150] No SVG found in: broken/file.html
2025-12-27 10:15:34 ERROR [3/150] Conversion failed: invalid_svg.html
...
2025-12-27 10:45:30 INFO Batch complete: 148/150 successful, 2 failed
```

### Summary Report
```json
{
  "conversion_summary": {
    "start_time": "2025-12-27T10:15:30Z",
    "end_time": "2025-12-27T10:45:30Z",
    "duration_seconds": 1800,
    "total_files": 150,
    "successful": 148,
    "failed": 2,
    "skipped": 0,
    "total_output_size_mb": 125.6,
    "average_conversion_time_ms": 1200
  },
  "by_category": {
    "air_intake_system": {
      "files": 5,
      "successful": 5,
      "failed": 0
    },
    "brakes": {
      "files": 8,
      "successful": 7,
      "failed": 1
    }
  },
  "failed_files": [
    {
      "file": "brakes/broken_diagram.html",
      "reason": "Invalid SVG markup",
      "error_detail": "..."
    }
  ],
  "size_statistics": {
    "full_size_avg_kb": 512,
    "thumbnail_avg_kb": 85,
    "largest_file": "chassis/complex_diagram.png",
    "largest_size_mb": 2.3
  }
}
```

---

## Validation & Quality Control

### Post-Conversion Checks

#### 1. File Existence
```python
def validate_output(html_path, output_dir):
    """
    Verify both full and thumbnail PNGs were created
    """
    base_name = get_base_name(html_path)
    
    full_path = f"{output_dir}/{base_name}.png"
    thumb_path = f"{output_dir}/{base_name}_thumb.png"
    
    return (
        os.path.exists(full_path) and 
        os.path.exists(thumb_path) and
        os.path.getsize(full_path) > 1000 and  # At least 1KB
        os.path.getsize(thumb_path) > 500
    )
```

#### 2. Dimension Verification
```python
def check_dimensions(png_path, expected_width):
    """
    Verify PNG matches expected dimensions
    """
    from PIL import Image
    img = Image.open(png_path)
    
    tolerance = 10  # Allow ±10px
    return abs(img.width - expected_width) <= tolerance
```

#### 3. Visual Quality Spot Check
- Manually review 10 random conversions
- Verify text is readable
- Check for clipping or distortion
- Confirm colors match originals

### Acceptance Criteria
- ✅ 95%+ success rate (148+ of 150 files)
- ✅ All successful files have both full + thumb
- ✅ Full size images: 1990-2010px width
- ✅ Thumbnail images: 590-610px width
- ✅ No obvious visual artifacts in spot check
- ✅ Total output size under 200MB

---

## Performance Expectations

### Single File
- **HTML parsing**: <100ms
- **SVG extraction**: <50ms
- **PNG conversion (2000px)**: 500-2000ms
- **PNG conversion (600px)**: 200-800ms
- **Total per file**: ~1-3 seconds

### Batch Processing (150 files)
- **Sequential**: ~5-7 minutes
- **Parallel (4 workers)**: ~2-3 minutes
- **Progress updates**: Every 10 files (~every 20 seconds)

### Optimization Strategies
```python
# 1. Parallel processing with multiprocessing
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(process_html_file, html_files)

# 2. Skip already converted files
if skip_existing and os.path.exists(output_path):
    logger.info(f"Skipping existing: {output_path}")
    continue

# 3. Batch I/O operations
# Read multiple HTML files into memory before processing
html_contents = [read_file(f) for f in batch]
```

---

## Storage Requirements

### Disk Space Calculation
```
Input: 150 HTML files @ ~100KB each = 15MB
Output Full (2000px): 150 files @ 500KB = 75MB
Output Thumb (600px): 150 files @ 80KB = 12MB
Total: ~102MB for one vehicle serial

With 10 vehicle serials: ~1GB
With 50 vehicle serials: ~5GB
```

### Storage Recommendations
- **Development**: Local SSD (fast conversion)
- **Staging**: Network storage OK (upload to WordPress anyway)
- **Production**: Images will be in WordPress media library

---

## Metadata File Specification

### conversion_metadata.json
```json
{
  "conversion_info": {
    "version": "1.0",
    "date": "2025-12-27T10:45:30Z",
    "script": "01_convert_svg_to_png.py",
    "settings": {
      "full_width": 2000,
      "thumb_width": 600,
      "background": "white",
      "format": "png"
    }
  },
  "files": [
    {
      "source": "LSFAL11A4PA157987/air_intake_system/air_filter.html",
      "serial_number": "LSFAL11A4PA157987",
      "category": "air_intake_system",
      "diagram_name": "air_filter",
      "outputs": {
        "full": {
          "path": "converted_images/.../air_filter.png",
          "width": 2000,
          "height": 1500,
          "size_kb": 456
        },
        "thumbnail": {
          "path": "converted_images/.../air_filter_thumb.png",
          "width": 600,
          "height": 450,
          "size_kb": 78
        }
      },
      "conversion_time_ms": 1234,
      "status": "success"
    }
  ],
  "statistics": {
    "total_files": 150,
    "successful": 148,
    "failed": 2,
    "total_size_mb": 125.6
  }
}
```

This metadata file is used by subsequent scripts to:
- Map HTML files to PNG files
- Upload correct images to WooCommerce
- Associate diagrams with products
- Troubleshoot conversion issues

---

## Next Steps

1. **Install dependencies**: `pip install cairosvg beautifulsoup4 Pillow`
2. **Test on 5 files**: Validate conversion quality
3. **Run full batch**: Process all HTML files
4. **Review results**: Check conversion_metadata.json
5. **Fix errors**: Re-run failed conversions with fallback methods
6. **Archive originals**: Keep HTML files for reference

---

## Script Template

```python
#!/usr/bin/env python3
"""
SVG to PNG Batch Converter
Processes HTML files with embedded SVG diagrams
Outputs multiple PNG sizes for WooCommerce
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from multiprocessing import Pool

import cairosvg
from bs4 import BeautifulSoup
from PIL import Image

# Configuration
ROOT_DATA_DIR = "path/to/LSFAL11A4PA157987"
OUTPUT_DIR = "converted_images"
LOG_FILE = "conversion.log"

SIZES = {
    "full": 2000,
    "thumbnail": 600
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Main conversion logic goes here...

if __name__ == "__main__":
    main()
```

---

**Document Version**: 1.0  
**Date**: December 27, 2025  
**Status**: Implementation Ready
