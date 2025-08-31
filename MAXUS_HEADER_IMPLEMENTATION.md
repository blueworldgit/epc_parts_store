# Maxus Parts Direct Header Implementation

## Overview
This document outlines the implementation of a Maxus Parts Direct header that matches the branding and styling of the WordPress site at maxuspartsdirect.co.uk.

## Changes Made

### 1. Updated Phone Number
- Changed from `01953 528 800` to `01953 665 421` throughout the header
- Updated both sticky header and main header instances

### 2. Added Top Contact Banner
- Added a new top banner section with contact information
- Matches the WordPress site's layout with phone number and contact message
- Includes the message: "Contact us if your part isn't listed, we will be able to get it for you"

### 3. Updated Branding
- Replaced logo image with text-based "Maxus Parts Direct" branding
- Added tagline: "Quality Parts for Maxus Vehicles"
- Applied Maxus-specific styling and colors

### 4. Enhanced Styling
- Added Maxus-specific CSS (`maxus-header.css`)
- Maintained the sapphire blue color scheme (#0c2a5c)
- Enhanced buttons and contact information styling
- Improved responsive design for mobile devices

### 5. Context Processor Integration
- Added `maxus_branding` context processor for dynamic content
- Provides variables like `MAXUS_SHOP_NAME`, `MAXUS_PHONE`, etc.
- Allows easy customization of branding elements

## Files Modified

### Templates
- `templates/oscar/partials/header.html` - Main header with Maxus branding
- `templates/oscar/partials/maxus_header.html` - Alternative complete Maxus header
- `templates/oscar/storefront_base.html` - Added CSS link

### Styling
- `staticfiles/css/maxus-header.css` - Maxus-specific styles

### Backend
- `context_processors.py` - Added Maxus branding context
- `settings.py` - Added new context processor

## Key Features

### Contact Information
- **Phone**: 01953 665 421
- **Email**: info@maxuspartsdirect.co.uk
- **Message**: "Contact us if your part isn't listed, we will be able to get it for you"

### Branding Elements
- **Company Name**: Maxus Parts Direct
- **Tagline**: Quality Parts for Maxus Vehicles
- **Company Info**: Part of the Rentals Direct Group
- **Company Registration**: 06980659
- **VAT Number**: GB981390205

### Styling Features
- Consistent sapphire blue color scheme
- Professional typography (Arial font family)
- Enhanced contact button styling
- Responsive design for all device sizes
- Top banner with contact information
- Improved cart widget styling

## Usage Options

### Option 1: Current Implementation (Recommended)
The existing header has been updated with Maxus branding while maintaining the current structure and functionality.

### Option 2: Complete Maxus Header
A standalone `maxus_header.html` template is available for complete replacement if desired.

## To Switch to Complete Maxus Header

If you want to use the complete Maxus header instead:

1. In `storefront_base.html`, change:
   ```html
   {% include 'oscar/partials/header.html' %}
   ```
   to:
   ```html
   {% include 'oscar/partials/maxus_header.html' %}
   ```

## Responsive Design
The header is fully responsive and adapts to:
- Desktop (1200px+)
- Tablet (768px - 1199px)  
- Mobile (up to 767px)

## Color Scheme
- **Primary Blue**: #0c2a5c (sapphire blue)
- **Contact Button**: #28a745 (green)
- **Cart Widget**: #ffc107 (yellow/gold)
- **Background**: #f8f9fa (light gray for top banner)

## Testing
To test the implementation:
1. Clear browser cache
2. Restart Django development server
3. Visit the homepage to see the updated header
4. Test on different screen sizes for responsive behavior
5. Verify all links and functionality work correctly

## Future Customization
All branding elements can be easily customized through the context processor variables in `context_processors.py` without modifying templates directly.
