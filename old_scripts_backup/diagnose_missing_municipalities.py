#!/usr/bin/env python3
"""
Diagnose missing municipalities by comparing MUNICIPALITY_DATA with database
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, '/home/manesha/electNepal')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import District, Municipality
from load_complete_municipalities import MUNICIPALITY_DATA

def diagnose_missing_municipalities():
    """Compare MUNICIPALITY_DATA with database to find missing municipalities"""
    
    print("=" * 80)
    print("MUNICIPALITY DIAGNOSTIC REPORT")
    print("=" * 80)
    
    # Count total municipalities in MUNICIPALITY_DATA
    total_in_data = 0
    for district_name, municipalities in MUNICIPALITY_DATA.items():
        total_in_data += len(municipalities)
    
    print(f"\nTotal municipalities in MUNICIPALITY_DATA: {total_in_data}")
    
    # Count municipalities in database
    db_count = Municipality.objects.count()
    print(f"Total municipalities in database: {db_count}")
    print(f"Difference: {total_in_data - db_count}")
    
    # Track missing municipalities
    missing_municipalities = []
    district_issues = []
    
    print("\n" + "=" * 80)
    print("CHECKING EACH DISTRICT")
    print("=" * 80)
    
    for district_name, municipalities in MUNICIPALITY_DATA.items():
        # Try to find the district
        district = District.objects.filter(name_en=district_name).first()
        
        if not district:
            # Try with partial matching
            district = District.objects.filter(name_en__icontains=district_name.split()[0]).first()
        
        if not district:
            district_issues.append(district_name)
            print(f"\n❌ District NOT FOUND: {district_name}")
            print(f"   Municipalities that would be affected ({len(municipalities)}):")
            for mun in municipalities:
                # Handle tuple format: (name_en, name_ne, type, wards)
                name_en = mun[0] if isinstance(mun, tuple) else mun['name_en']
                mun_type = mun[2] if isinstance(mun, tuple) else mun['type']
                missing_municipalities.append((district_name, name_en))
                print(f"   - {name_en} ({mun_type})")
            continue
        
        # Check each municipality in this district
        district_missing = []
        for mun_data in municipalities:
            # Handle tuple format: (name_en, name_ne, type, wards)
            if isinstance(mun_data, tuple):
                name_en = mun_data[0]
                name_ne = mun_data[1]
                mun_type = mun_data[2]
                wards = mun_data[3]
            else:
                name_en = mun_data['name_en']
                name_ne = mun_data.get('name_ne', '')
                mun_type = mun_data['type']
                wards = mun_data['wards']
            
            municipality = Municipality.objects.filter(
                district=district,
                name_en=name_en
            ).first()
            
            if not municipality:
                district_missing.append((name_en, name_ne, mun_type, wards))
                missing_municipalities.append((district_name, name_en))
        
        if district_missing:
            print(f"\n⚠️  District: {district_name} (Found as: {district.name_en})")
            print(f"   Missing {len(district_missing)} municipalities:")
            for name_en, name_ne, mun_type, wards in district_missing:
                print(f"   - {name_en} ({mun_type}, {wards} wards)")
        else:
            print(f"✅ {district_name}: All {len(municipalities)} municipalities loaded")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if district_issues:
        print(f"\n❌ Districts with issues ({len(district_issues)}):")
        for district in district_issues:
            print(f"   - {district}")
    
    if missing_municipalities:
        print(f"\n❌ Total missing municipalities: {len(missing_municipalities)}")
        print("\nMissing municipalities by district:")
        for district, mun_name in missing_municipalities:
            print(f"   - {district}: {mun_name}")
    else:
        print("\n✅ All municipalities are loaded!")
    
    # Check for municipalities in DB but not in MUNICIPALITY_DATA
    print("\n" + "=" * 80)
    print("CHECKING FOR EXTRA MUNICIPALITIES IN DATABASE")
    print("=" * 80)
    
    db_municipalities = Municipality.objects.all()
    extra_count = 0
    
    for db_mun in db_municipalities:
        district_name = db_mun.district.name_en
        found = False
        
        # Check in MUNICIPALITY_DATA
        for data_district, municipalities in MUNICIPALITY_DATA.items():
            if data_district == district_name or district_name.startswith(data_district.split()[0]):
                for mun_data in municipalities:
                    # Handle tuple format
                    name_en = mun_data[0] if isinstance(mun_data, tuple) else mun_data['name_en']
                    if name_en == db_mun.name_en:
                        found = True
                        break
            if found:
                break
        
        if not found:
            extra_count += 1
            print(f"   - {db_mun.district.name_en}: {db_mun.name_en} (in DB but not in data)")
    
    if extra_count == 0:
        print("   No extra municipalities found in database")
    else:
        print(f"\n   Total extra municipalities in database: {extra_count}")
    
    # Check district name mismatches
    print("\n" + "=" * 80)
    print("DISTRICT NAME COMPARISON")
    print("=" * 80)
    
    data_districts = set(MUNICIPALITY_DATA.keys())
    db_districts = set(District.objects.values_list('name_en', flat=True))
    
    print(f"\nDistricts in MUNICIPALITY_DATA: {len(data_districts)}")
    print(f"Districts in database: {len(db_districts)}")
    
    only_in_data = data_districts - db_districts
    only_in_db = db_districts - data_districts
    
    if only_in_data:
        print(f"\n❌ Districts in MUNICIPALITY_DATA but not in DB ({len(only_in_data)}):")
        for d in sorted(only_in_data):
            print(f"   - {d}")
    
    if only_in_db:
        print(f"\n⚠️  Districts in DB but not in MUNICIPALITY_DATA ({len(only_in_db)}):")
        for d in sorted(only_in_db):
            print(f"   - {d}")
    
    return missing_municipalities, district_issues

if __name__ == "__main__":
    missing, issues = diagnose_missing_municipalities()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print(f"Missing municipalities: {len(missing)}")
    print(f"District issues: {len(issues)}")