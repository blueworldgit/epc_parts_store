# Logo Installation Instructions

## How to add your Van Parts Direct logo:

1. Save the attached logo image as: `vans-direct-logo.png`

2. Place it in this directory:
   `c:\pythonstuff\vansdirect\epc_parts_store\epcdata\media\images\`

3. Replace the placeholder file:
   - Delete the file: `vans-direct-logo.png.placeholder`
   - Save your logo as: `vans-direct-logo.png`

## What has been implemented:

✅ **Logo placement**: Added to the left side of the breadcrumb area
✅ **Responsive design**: 
   - Desktop: Logo on left, breadcrumb navigation centered
   - Mobile: Logo centered above breadcrumb navigation
   - Smaller mobile: Reduced logo size for better fit

✅ **Size optimization**:
   - Desktop: Max height 60px (fits breadcrumb area)
   - Tablet: Max height 40px 
   - Mobile: Max height 35px

✅ **Styling**:
   - Maintains aspect ratio
   - Proper alignment and spacing
   - Works with existing breadcrumb shadow styling

## File locations modified:
- Template: `epcdata/templates/oscar/storefront_base.html`
- Logo location: `epcdata/media/images/vans-direct-logo.png`

## Notes:
- The logo uses the media directory (not static) to avoid collectstatic issues
- The template expects a PNG file, but you can use JPG by changing the file extension in the template
- Logo is automatically responsive and will scale appropriately on all devices
