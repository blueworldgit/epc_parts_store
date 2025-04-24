import os
import sys
import django

# Add the project root (where manage.py is) to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')

# Setup Django
django.setup()

# Now safe to import from your app
from motorpartsdata.serializers import (
    SerialNumberSerializer,
    ParentTitleSerializer,
    ChildTitleSerializer,
    PartSerializer
)

# After scraping your data with BeautifulSoup, suppose you get:

serial_data = {"serial": "ABC123"}
serial_serializer = SerialNumberSerializer(data=serial_data)
if serial_serializer.is_valid():
    serial_instance = serial_serializer.save()
else:
    print(serial_serializer.errors)

parent_data = {"title": "Engine Parts", "serial_number": serial_instance.id}
parent_serializer = ParentTitleSerializer(data=parent_data)
if parent_serializer.is_valid():
    parent_instance = parent_serializer.save()
else:
    print(parent_serializer.errors)

child_data = {
    "title": "Piston Assembly",
    "parent": parent_instance.id,
    "svg_code": "<svg>...</svg>",
}
child_serializer = ChildTitleSerializer(data=child_data)
if child_serializer.is_valid():
    child_instance = child_serializer.save()
else:
    print(child_serializer.errors)

part_data = {
    "child_title": child_instance.id,
    "call_out_order": 1,
    "part_number": "123-456",
    "usage_name": "Main Piston",
    "unit_qty": 2,
    "lr": "L",
    "remark": "High pressure",
    "nn_note": "Install carefully",
}
part_serializer = PartSerializer(data=part_data)
if part_serializer.is_valid():
    part_serializer.save()
else:
    print(part_serializer.errors)

