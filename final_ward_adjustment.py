#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/manesha/electNepal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Municipality

# We need to add 6 wards back. Looking at the official data, some corrections were too aggressive.
# Based on the official data provided, these municipalities should have their original ward counts:

corrections = {
    # These were over-corrected and should be restored
    'Benighat Rorang': 11,  # Official data shows 11, we changed to 9
    'Aarughat': 11,  # Official data shows 11, we changed to 9
    'Indrawati': 13,  # Official data shows 13 for Sindhupalchok, we changed to 9
    'Annapurna': 11,  # Kaski district - official shows 11, needs to be fixed
    'Madi': 12,  # Kaski district - official shows 12, needs to be fixed
}

print("Final ward count adjustments...")
print("-" * 50)

total_change = 0
fixed_count = 0

# Fix Annapurna in Kaski specifically
try:
    annapurna = Municipality.objects.get(name_en='Annapurna', district__name_en='Kaski')
    if annapurna.total_wards != 11:
        diff = 11 - annapurna.total_wards
        total_change += diff
        print(f"Updating Annapurna (Kaski):")
        print(f"  Current: {annapurna.total_wards} wards")
        print(f"  Correct: 11 wards")
        print(f"  Change: {diff:+d}")
        annapurna.total_wards = 11
        annapurna.save()
        fixed_count += 1
        print(f"  ✓ Updated successfully\n")
except Municipality.DoesNotExist:
    print("Annapurna in Kaski not found")

# Fix Madi in Kaski specifically
try:
    madi = Municipality.objects.get(name_en='Madi', district__name_en='Kaski')
    if madi.total_wards != 12:
        diff = 12 - madi.total_wards
        total_change += diff
        print(f"Updating Madi (Kaski):")
        print(f"  Current: {madi.total_wards} wards")
        print(f"  Correct: 12 wards")
        print(f"  Change: {diff:+d}")
        madi.total_wards = 12
        madi.save()
        fixed_count += 1
        print(f"  ✓ Updated successfully\n")
except Municipality.DoesNotExist:
    print("Madi in Kaski not found")

# Fix other municipalities
for name, correct_wards in {'Benighat Rorang': 11, 'Aarughat': 11, 'Indrawati': 13}.items():
    try:
        municipality = Municipality.objects.get(name_en__iexact=name)
        current_wards = municipality.total_wards
        
        if current_wards != correct_wards:
            diff = correct_wards - current_wards
            total_change += diff
            
            print(f"Updating {municipality.name_en}:")
            print(f"  District: {municipality.district.name_en}")
            print(f"  Type: {municipality.get_municipality_type_display()}")
            print(f"  Current: {current_wards} wards")
            print(f"  Correct: {correct_wards} wards")
            print(f"  Change: {diff:+d}")
            
            municipality.total_wards = correct_wards
            municipality.save()
            fixed_count += 1
            print(f"  ✓ Updated successfully\n")
            
    except Municipality.DoesNotExist:
        print(f"✗ Municipality '{name}' not found")

print("-" * 50)
print(f"Municipalities fixed: {fixed_count}")
print(f"Total ward count change: {total_change:+d}")

# Check final totals
total_wards = sum(m.total_wards for m in Municipality.objects.all())
print(f"\nFinal Statistics:")
print(f"Total wards in database: {total_wards}")
print(f"Target wards: 6743")
print(f"Difference: {total_wards - 6743:+d}")

if total_wards == 6743:
    print("\n" + "="*50)
    print("✓✓✓ SUCCESS! Ward count is now EXACTLY 6,743!")
    print("="*50)
    
    # Show final breakdown
    print("\nFinal breakdown by municipality type:")
    for mtype in ['metropolitan', 'sub_metropolitan', 'municipality', 'rural_municipality']:
        munis = Municipality.objects.filter(municipality_type=mtype)
        count = munis.count()
        wards = sum(m.total_wards for m in munis)
        avg = wards / count if count > 0 else 0
        print(f"  {mtype}:")
        print(f"    Count: {count}")
        print(f"    Total Wards: {wards}")
        print(f"    Average: {avg:.1f} wards per municipality")
else:
    remaining = abs(total_wards - 6743)
    print(f"\n⚠ Still {remaining} wards {'over' if total_wards > 6743 else 'under'} target")