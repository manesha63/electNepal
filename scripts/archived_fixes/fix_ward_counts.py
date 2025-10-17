#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/manesha/electNepal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Municipality

# Official ward counts based on the provided data
# These are municipalities that need correction
corrections = {
    # Municipality name: correct ward count
    'Lahan': 16,  # Currently 24, should be 16
    'Siraha': 19,  # Currently 22, should be 19
    'Itahari': 20,  # Sub-Metropolitan, currently might be wrong
    'Butwal': 19,  # Sub-Metropolitan, should be 19
    'Jeetpur Simara': 23,  # Sub-Metropolitan, should be 23
    'Kalaiya': 25,  # Sub-Metropolitan, should be 25
    'Dharan': 20,  # Sub-Metropolitan
    'Hetauda': 19,  # Sub-Metropolitan
    'Ghorahi': 19,  # Sub-Metropolitan
    'Tulsipur': 19,  # Sub-Metropolitan
}

print("Fixing ward counts...")
print("-" * 50)

total_change = 0

for name, correct_wards in corrections.items():
    try:
        municipality = Municipality.objects.get(name_en__iexact=name)
        current_wards = municipality.total_wards
        
        if current_wards != correct_wards:
            diff = correct_wards - current_wards
            total_change += diff
            
            print(f"Updating {municipality.name_en}:")
            print(f"  Type: {municipality.get_municipality_type_display()}")
            print(f"  Current: {current_wards} wards")
            print(f"  Correct: {correct_wards} wards")
            print(f"  Change: {diff:+d}")
            
            municipality.total_wards = correct_wards
            municipality.save()
            print(f"  ✓ Updated successfully")
            print()
        else:
            print(f"✓ {municipality.name_en} already has correct ward count: {correct_wards}")
            
    except Municipality.DoesNotExist:
        print(f"✗ Municipality '{name}' not found")
    except Municipality.MultipleObjectsReturned:
        print(f"✗ Multiple municipalities found for '{name}'")

print("-" * 50)
print(f"Total ward count change: {total_change:+d}")

# Check final totals
total_wards = sum(m.total_wards for m in Municipality.objects.all())
print(f"Total wards in database: {total_wards}")
print(f"Target wards: 6743")
print(f"Difference: {total_wards - 6743}")

if total_wards == 6743:
    print("✓ Ward count is now correct!")
else:
    print(f"Still {abs(total_wards - 6743)} wards {'over' if total_wards > 6743 else 'under'} target")