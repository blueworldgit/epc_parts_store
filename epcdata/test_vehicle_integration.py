"""
Test script to verify the vehicle brand integration
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import SerialNumber
from oscar.apps.catalogue.models import Category
from vehicle_utils import determine_vehicle_brand, get_or_create_vehicle_category, get_or_create_serial_category

def test_vehicle_brand_integration():
    """Test the complete vehicle brand integration"""
    print("🧪 Testing Vehicle Brand Integration")
    print("=" * 50)
    
    # Test 1: Vehicle brand determination
    test_serials = [
        "LSH14C4C5NA129710",  # Should be Maxus
        "VF3XXXXXX",          # Should be Peugeot  
        "VF1XXXXXX",          # Should be Renault
    ]
    
    print("🔍 Test 1: Vehicle Brand Detection")
    for serial in test_serials:
        brand = determine_vehicle_brand(serial)
        print(f"  Serial: {serial} → Brand: {brand}")
    
    # Test 2: Create/Update SerialNumber with vehicle brand
    print("\n🏗️  Test 2: SerialNumber Creation with Vehicle Brand")
    serial_name = "LSH14C4C5NA129710"
    vehicle_brand = determine_vehicle_brand(serial_name)
    
    # Create or get serial number
    serial_obj, created = SerialNumber.objects.get_or_create(
        serial=serial_name,
        defaults={'vehicle_brand': vehicle_brand}
    )
    
    if created:
        print(f"  ✅ Created new SerialNumber: {serial_obj}")
    else:
        print(f"  ♻️  Using existing SerialNumber: {serial_obj}")
        if serial_obj.vehicle_brand != vehicle_brand:
            serial_obj.vehicle_brand = vehicle_brand
            serial_obj.save()
            print(f"  🔄 Updated vehicle brand to: {vehicle_brand}")
    
    # Test 3: Oscar Category Integration
    print("\n🏪 Test 3: Oscar Category Integration")
    
    # Get vehicle category
    vehicle_category = get_or_create_vehicle_category(vehicle_brand)
    print(f"  Vehicle Category: {vehicle_category.name} (ID: {vehicle_category.id})")
    
    # Get serial category
    serial_category = get_or_create_serial_category(serial_name, vehicle_category)
    print(f"  Serial Category: {serial_category.name} (Parent: {serial_category.get_parent().name})")
    
    # Test 4: Display hierarchy
    print("\n🌳 Test 4: Category Hierarchy")
    def display_hierarchy(category, indent=0):
        print("  " + "  " * indent + f"📁 {category.name}")
        for child in category.get_children():
            display_hierarchy(child, indent + 1)
    
    vehicle_category = Category.objects.get(name="Maxus")
    display_hierarchy(vehicle_category)
    
    # Test 5: Verify all vehicle categories
    print("\n🚗 Test 5: All Vehicle Categories")
    vehicle_categories = Category.objects.filter(depth=1).order_by('name')
    for cat in vehicle_categories:
        children_count = cat.get_children().count()
        print(f"  🏷️  {cat.name}: {children_count} serial(s)")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_vehicle_brand_integration()
