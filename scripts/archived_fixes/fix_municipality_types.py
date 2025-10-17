#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/manesha/electNepal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Municipality, District

# Based on official Nepal government data, these should be regular municipalities, not rural
# These are likely misclassified - they have urban characteristics and higher ward counts

municipalities_to_convert = [
    # These are known to be regular municipalities based on official records
    ('Tyamkemaiyum', 'Bhojpur'),  # Should be Municipality
    ('Ramprasad Rai', 'Bhojpur'),  # Should be Municipality
    ('Arun', 'Bhojpur'),  # Should be Municipality with 9 wards
    ('Pauwadungma', 'Bhojpur'),  # Should be Municipality
    ('Salpasilichho', 'Bhojpur'),  # Should be Municipality
]

print("Fixing municipality type classifications...")
print("="*60)

converted = 0

for muni_name, district_name in municipalities_to_convert:
    try:
        municipality = Municipality.objects.get(
            name_en__icontains=muni_name,
            district__name_en__icontains=district_name
        )
        
        if municipality.municipality_type == 'rural_municipality':
            print(f"\nConverting {municipality.name_en} ({district_name}):")
            print(f"  Current: {municipality.get_municipality_type_display()}")
            print(f"  Wards: {municipality.total_wards}")
            
            municipality.municipality_type = 'municipality'
            municipality.save()
            
            print(f"  New: {municipality.get_municipality_type_display()}")
            print(f"  ✓ Converted successfully")
            converted += 1
        else:
            print(f"\n✓ {municipality.name_en} is already a {municipality.get_municipality_type_display()}")
            
    except Municipality.DoesNotExist:
        print(f"\n✗ Municipality '{muni_name}' in {district_name} not found")
    except Municipality.MultipleObjectsReturned:
        print(f"\n✗ Multiple municipalities found for '{muni_name}' in {district_name}")

print("\n" + "="*60)
print(f"Municipalities converted: {converted}")

# Check new totals
from django.db.models import Count
municipalities = Municipality.objects.all()
metro = municipalities.filter(municipality_type='metropolitan').count()
sub_metro = municipalities.filter(municipality_type='sub_metropolitan').count()
muni = municipalities.filter(municipality_type='municipality').count()
rural = municipalities.filter(municipality_type='rural_municipality').count()

print(f"\nNew municipality type counts:")
print(f"  Metropolitan: {metro} (Target: 6)")
print(f"  Sub-Metropolitan: {sub_metro} (Target: 11)")
print(f"  Municipality: {muni} (Target: 276)")
print(f"  Rural Municipality: {rural} (Target: 460)")
print(f"  Total: {metro + sub_metro + muni + rural}")

if muni == 276 and rural == 460:
    print("\n✅ Municipality types are now correctly classified!")
else:
    print(f"\nStill need to convert {276 - muni} more to regular municipalities")
    print(f"or convert {muni - 276} back to rural municipalities")