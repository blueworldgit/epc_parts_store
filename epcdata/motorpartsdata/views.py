from django.shortcuts import render, get_object_or_404
from .models import SerialNumber, ParentTitle, ChildTitle, Part, PricingData

def serial_lookup(request):
    serial_value = request.GET.get('serial')
    parent_titles = []
    if serial_value:
        try:
            serial = SerialNumber.objects.get(serial=serial_value)
            parent_titles = serial.parent_titles.all()
        except SerialNumber.DoesNotExist:
            serial = None
    return render(request, 'motorparts/serial_lookup.html', {'serial': serial_value, 'parent_titles': parent_titles})

def parent_detail(request, parent_id):
    parent = get_object_or_404(ParentTitle, id=parent_id)
    child_titles = parent.child_titles.all()
    return render(request, 'motorparts/parent_detail.html', {'parent': parent, 'child_titles': child_titles})

def child_detail(request, child_id):
    child = get_object_or_404(ChildTitle, id=child_id)
    parts = child.parts.all()
    return render(request, 'motorparts/child_detail.html', {'child': child, 'parts': parts})

def parts_pricing_view(request, serial_number):
    """
    Display all parts for a given serial number with their pricing information
    """
    try:
        serial = SerialNumber.objects.get(serial=serial_number)
    except SerialNumber.DoesNotExist:
        return render(request, 'motorparts/parts_pricing.html', {
            'error': f'Serial number "{serial_number}" not found',
            'serial_number': serial_number
        })
    
    # Get all parts for this serial number through the relationship chain
    parts_data = []
    seen_part_numbers = set()
    
    # Navigate through SerialNumber -> ParentTitle -> ChildTitle -> Part
    for parent_title in serial.parent_titles.all():
        for child_title in parent_title.child_titles.all():
            for part in child_title.parts.all():
                if part.part_number in seen_part_numbers:
                    continue
                seen_part_numbers.add(part.part_number)
                try:
                    # Try to get pricing data for this part
                    pricing_data = PricingData.objects.get(part_number=part)
                    parts_data.append({
                        'part': part,
                        'description': pricing_data.description or 'N/A',
                        'list_price': pricing_data.list_price or 'N/A',
                        'stock_order': pricing_data.stock_order or 'N/A',
                        'has_pricing': True,
                        'parent_title': parent_title.title,
                        'child_title': child_title.title
                    })
                except PricingData.DoesNotExist:
                    parts_data.append({
                        'part': part,
                        'description': 'Data Missing',
                        'list_price': 'Data Missing',
                        'stock_order': 'Data Missing',
                        'has_pricing': False,
                        'parent_title': parent_title.title,
                        'child_title': child_title.title
                    })
    
    # Sort by has_pricing (False first, so "Data Missing" entries come first)
    parts_data.sort(key=lambda x: x['has_pricing'])
    
    return render(request, 'motorparts/parts_pricing.html', {
        'serial': serial,
        'serial_number': serial_number,
        'parts_data': parts_data,
        'total_parts': len(parts_data),
        'missing_pricing': len([p for p in parts_data if not p['has_pricing']]),
        'with_pricing': len([p for p in parts_data if p['has_pricing']])
    })

def part_pricing_detail(request, part_number):
    """
    Display pricing data for a specific part number
    """
    # Get the first part instance with this part number
    part = Part.objects.filter(part_number=part_number).first()
    
    if not part:
        return render(request, 'motorparts/part_pricing_detail.html', {
            'error': f'Part number "{part_number}" not found',
            'part_number': part_number
        })
    
    # Get pricing data for this part
    pricing_data = PricingData.objects.filter(part_number=part).first()
    has_pricing = pricing_data is not None
    
    return render(request, 'motorparts/part_pricing_detail.html', {
        'part': part,
        'part_number': part_number,
        'pricing_data': pricing_data,
        'has_pricing': has_pricing
    })

def parts_pricing_debug(request, serial_number):
    """
    Debug version to understand the pricing data matching issue
    """
    try:
        serial = SerialNumber.objects.get(serial=serial_number)
    except SerialNumber.DoesNotExist:
        return render(request, 'motorparts/parts_pricing.html', {
            'error': f'Serial number "{serial_number}" not found',
            'serial_number': serial_number
        })
    
    # Get all parts for this serial number through the relationship chain
    parts_data = []
    seen_part_numbers = set()
    debug_info = []
    
    # Navigate through SerialNumber -> ParentTitle -> ChildTitle → Part
    for parent_title in serial.parent_titles.all():
        for child_title in parent_title.child_titles.all():
            for part in child_title.parts.all():
                if part.part_number in seen_part_numbers:
                    continue
                seen_part_numbers.add(part.part_number)
                
                # Debug: Check all parts with this part_number
                all_parts_with_same_number = Part.objects.filter(part_number=part.part_number)
                parts_with_pricing = []
                for p in all_parts_with_same_number:
                    pricing_exists = PricingData.objects.filter(part_number=p).exists()
                    parts_with_pricing.append(f"Part ID {p.id}: {'Yes' if pricing_exists else 'No'}")
                
                debug_info.append({
                    'part_number': part.part_number,
                    'current_part_id': part.id,
                    'all_parts_info': parts_with_pricing
                })
                
                # Try to get pricing data for this specific part
                pricing_data = PricingData.objects.filter(part_number=part).first()
                
                if pricing_data:
                    parts_data.append({
                        'part': part,
                        'description': pricing_data.description or 'N/A',
                        'list_price': pricing_data.list_price or 'N/A',
                        'stock_order': pricing_data.stock_order or 'N/A',
                        'has_pricing': True,
                        'parent_title': parent_title.title,
                        'child_title': child_title.title
                    })
                else:
                    parts_data.append({
                        'part': part,
                        'description': 'Data Missing',
                        'list_price': 'Data Missing',
                        'stock_order': 'Data Missing',
                        'has_pricing': False,
                        'parent_title': parent_title.title,
                        'child_title': child_title.title
                    })
    
    # Sort by has_pricing (False first, so "Data Missing" entries come first)
    parts_data.sort(key=lambda x: x['has_pricing'])
    
    return render(request, 'motorparts/parts_pricing_debug.html', {
        'serial': serial,
        'serial_number': serial_number,
        'parts_data': parts_data,
        'debug_info': debug_info,
        'total_parts': len(parts_data),
        'missing_pricing': len([p for p in parts_data if not p['has_pricing']]),
        'with_pricing': len([p for p in parts_data if p['has_pricing']])
    })
