from django.contrib import admin
from django.utils.safestring import mark_safe
from oscar.core.loading import get_model
from motorpartsdata.models import ChildTitle, Part

Product = get_model('catalogue', 'Product')

class ProductAdminExtended(admin.ModelAdmin):
    """Extended Product admin to show SVG diagrams"""
    list_display = ['title', 'upc', 'structure', 'has_svg_diagram']
    readonly_fields = ['svg_diagram_preview']
    
    def has_svg_diagram(self, obj):
        """Check if product has associated SVG diagram"""
        try:
            part = Part.objects.get(part_number=obj.upc)
            child_title = part.child_title
            return bool(child_title and child_title.svg_code)
        except (Part.DoesNotExist, ChildTitle.DoesNotExist):
            return False
    has_svg_diagram.boolean = True
    has_svg_diagram.short_description = 'Has SVG'
    
    def svg_diagram_preview(self, obj):
        """Display SVG diagram in admin"""
        try:
            part = Part.objects.get(part_number=obj.upc)
            child_title = part.child_title
            if child_title and child_title.svg_code:
                # Scale down the SVG for admin preview
                svg_html = f'''
                <div style="border: 1px solid #ccc; padding: 10px; max-width: 600px; max-height: 400px; overflow: auto;">
                    <h4>SVG Diagram for {child_title.title}</h4>
                    <div style="transform: scale(0.5); transform-origin: top left; width: 200%; height: 200%;">
                        {child_title.svg_code}
                    </div>
                </div>
                '''
                return mark_safe(svg_html)
            else:
                return "No SVG diagram available"
        except (Part.DoesNotExist, ChildTitle.DoesNotExist):
            return "No associated part data found"
    svg_diagram_preview.short_description = 'SVG Diagram'

# Unregister the default Product admin and register our extended version
admin.site.unregister(Product)
admin.site.register(Product, ProductAdminExtended)
