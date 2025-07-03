""" from motorpartsdata.models import SerialNumber, Part

serial1 = "LSH14C4C5NA129710"  # Replace with your first serial number
serial2 = "LSH14J7C2MA122115"  # Replace with your second serial number

try:
    s1 = SerialNumber.objects.get(serial=serial1)
    s2 = SerialNumber.objects.get(serial=serial2)
except SerialNumber.DoesNotExist as e:
    print(f"Serial not found: {e}")
    parts_in_s2_not_s1 = []
else:
    parts1 = set(
        Part.objects.filter(child_title__parent__serial_number=s1)
        .values_list("part_number", flat=True)
    )
    parts2 = set(
        Part.objects.filter(child_title__parent__serial_number=s2)
        .values_list("part_number", flat=True)
    )
    # Find parts in serial2 that are NOT in serial1
    parts_in_s2_not_s1 = sorted(parts2 - parts1)

   
with open("next.txt", "w", encoding="utf-8") as f:
    f.write(str(parts_in_s2_not_s1)) """


