from django.shortcuts import render, get_object_or_404
from .models import SerialNumber, ParentTitle, ChildTitle, Part

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
