from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from motorpartsdata.models import Part, ChildTitle

@require_http_methods(["GET"])
def svg_diagram_view(request, upc):
    """Return SVG diagram data for a product UPC"""
    try:
        part = Part.objects.get(part_number=upc)
        child_title = part.child_title
        
        if child_title and child_title.svg_code:
            return JsonResponse({
                'success': True,
                'title': child_title.title,
                'svg_code': child_title.svg_code
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No SVG diagram available'
            })
    except (Part.DoesNotExist, ChildTitle.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Part not found'
        })
