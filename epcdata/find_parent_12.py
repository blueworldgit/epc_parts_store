#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epcdata.settings')
django.setup()

from motorpartsdata.models import Part, SerialNumber, ParentTitle, ChildTitle

def find_parent_12():
    print("============================================================")
    print("🔍 SEARCHING FOR PARENT #12 IN LSFAL11A4PA157987")
    print("============================================================")
    
    try:
        serial = SerialNumber.objects.get(serial="LSFAL11A4PA157987")
        parent_titles = serial.parent_titles.all().order_by('id')
        
        print(f"📂 Total parent titles: {parent_titles.count()}")
        print("\n📋 All parent titles with their index:")
        
        for idx, parent in enumerate(parent_titles, 1):
            child_count = parent.child_titles.count()
            parts_count = sum(child.parts.count() for child in parent.child_titles.all())
            print(f"   {idx:2d}. {parent.title} ({child_count} children, {parts_count} parts)")
            
            # Show children for parent #12
            if idx == 12:
                print(f"      📁 Children of Parent #{idx}:")
                for child_idx, child in enumerate(parent.child_titles.all(), 1):
                    parts_in_child = child.parts.count()
                    print(f"         {child_idx}. {child.title} ({parts_in_child} parts)")
                    
                    # Check if this matches "1.40" pattern
                    if "1.40" in child.title or "1_40" in child.title:
                        print(f"         ⭐ POTENTIAL MATCH: {child.title}")
        
        # Look for any child titles containing "1.40" or similar
        print(f"\n🔍 Searching for children containing '1.40' or '1_40':")
        all_children = ChildTitle.objects.filter(parent__serial_number=serial)
        matches = all_children.filter(title__icontains="1.40") | all_children.filter(title__icontains="1_40")
        
        for child in matches:
            parent_idx = list(parent_titles).index(child.parent) + 1
            print(f"   Parent #{parent_idx}: {child.parent.title}")
            print(f"   Child: {child.title} ({child.parts.count()} parts)")
        
        if not matches.exists():
            print("   ❌ No children found with '1.40' or '1_40' pattern")
            
        print(f"\n🔍 Alternative: Look for any children with '40' in the name:")
        forty_matches = all_children.filter(title__icontains="40")
        for child in forty_matches[:5]:  # Show first 5
            parent_idx = list(parent_titles).index(child.parent) + 1
            print(f"   Parent #{parent_idx}: {child.title} ({child.parts.count()} parts)")
            
    except SerialNumber.DoesNotExist:
        print("❌ Serial LSFAL11A4PA157987 not found")

if __name__ == "__main__":
    find_parent_12()