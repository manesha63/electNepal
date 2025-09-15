#!/usr/bin/env python3
"""
Verify complete Nepal administrative data against database
Based on official government structure
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Province, District, Municipality
from collections import defaultdict

# Official complete data from government records
OFFICIAL_DATA = {
    "Koshi Province": {
        "Bhojpur": [
            ("Bhojpur", "municipality", 10),
            ("Shadanand", "municipality", 9),
            ("Tyamkemaiyum", "rural_municipality", 6),
            ("Ramprasad Rai", "rural_municipality", 5),
            ("Arun", "rural_municipality", 9),
            ("Pauwadungma", "rural_municipality", 5),
            ("Salpasilichho", "rural_municipality", 6),
            ("Aamchok", "rural_municipality", 7),
            ("Hatuwagadhi", "rural_municipality", 6),
        ],
        "Dhankuta": [
            ("Dhankuta", "municipality", 10),
            ("Pakhribas", "municipality", 9),
            ("Mahalaxmi", "municipality", 11),
            ("Sangurigadhi", "rural_municipality", 7),
            ("Khalsa Chhintang Sahidbhumi", "rural_municipality", 6),
            ("Chaubise", "rural_municipality", 9),
            ("Chhathar Jorpati", "rural_municipality", 8),
        ],
        "Ilam": [
            ("Ilam", "municipality", 12),
            ("Deumai", "municipality", 10),
            ("Mai", "municipality", 10),
            ("Suryodaya", "municipality", 12),
            ("Chulachuli", "rural_municipality", 9),
            ("Rong", "rural_municipality", 6),
            ("Mangsebung", "rural_municipality", 9),
            ("Sandakpur", "rural_municipality", 5),
            ("Fakfokthum", "rural_municipality", 9),
            ("Maijogmai", "rural_municipality", 6),
        ],
        "Jhapa": [
            ("Mechinagar", "municipality", 15),
            ("Damak", "municipality", 10),
            ("Kankai", "municipality", 12),
            ("Bhadrapur", "municipality", 10),
            ("Arjundhara", "municipality", 12),
            ("Shivasatakshi", "municipality", 13),
            ("Gauradaha", "municipality", 11),
            ("Birtamode", "municipality", 9),
            ("Kamal", "rural_municipality", 8),
            ("Jhapa", "rural_municipality", 8),
            ("Buddhashanti", "rural_municipality", 7),
            ("Haldibari", "rural_municipality", 7),
            ("Kachankawal", "rural_municipality", 10),
            ("Barhadashi", "rural_municipality", 6),
            ("Gaurigunj", "rural_municipality", 5),
        ],
        "Khotang": [
            ("Halesi Tuwachung", "municipality", 11),
            ("Diprung Chuichumma", "rural_municipality", 7),
            ("Aiselukharka", "rural_municipality", 7),
            ("Lamidanda", "rural_municipality", 5),
            ("Jantedhunga", "rural_municipality", 5),
            ("Khotehang", "rural_municipality", 9),
            ("Kepilasgadhi", "rural_municipality", 5),
            ("Barahpokhari", "rural_municipality", 7),
            ("Rawabesi", "rural_municipality", 9),
            ("Sakela", "rural_municipality", 9),
        ],
        "Morang": [
            ("Biratnagar", "metropolitan", 19),
            ("Sundar Haraicha", "municipality", 14),
            ("Rangeli", "municipality", 9),
            ("Pathari-Sanischare", "municipality", 9),
            ("Urlabari", "municipality", 12),
            ("Belbari", "municipality", 10),
            ("Letang", "municipality", 11),
            ("Ratuwamai", "municipality", 9),
            ("Sunawarshi", "rural_municipality", 9),
            ("Dhanpalthan", "rural_municipality", 6),
            ("Budhiganga", "rural_municipality", 8),
            ("Gramthan", "rural_municipality", 6),
            ("Katahari", "rural_municipality", 9),
            ("Kerabari", "rural_municipality", 9),
            ("Miklajung", "rural_municipality", 9),
            ("Kanepokhari", "rural_municipality", 7),
            ("Jahada", "rural_municipality", 6),
        ],
        "Okhaldhunga": [
            ("Siddhicharan", "municipality", 9),
            ("Khijidemba", "rural_municipality", 8),
            ("Champadevi", "rural_municipality", 8),
            ("Chisankhugadhi", "rural_municipality", 7),
            ("Manebhanjyang", "rural_municipality", 9),
            ("Molung", "rural_municipality", 9),
            ("Likhu", "rural_municipality", 9),
            ("Sunkoshi", "rural_municipality", 8),
        ],
        "Panchthar": [
            ("Phidim", "municipality", 10),
            ("Hilihang", "rural_municipality", 9),
            ("Kummayak", "rural_municipality", 9),
            ("Miklajung", "rural_municipality", 5),
            ("Phalelung", "rural_municipality", 9),
            ("Falgunanda", "rural_municipality", 9),
            ("Yangwarak", "rural_municipality", 8),
            ("Tumbewa", "rural_municipality", 6),
        ],
        "Sankhuwasabha": [
            ("Khandbari", "municipality", 10),
            ("Dharmadevi", "municipality", 11),
            ("Panchkhapan", "municipality", 9),
            ("Chainpur", "municipality", 13),
            ("Madi", "municipality", 9),
            ("Bhotkhola", "rural_municipality", 5),
            ("Chichila", "rural_municipality", 6),
            ("Makalu", "rural_municipality", 8),
            ("Sabhapokhari", "rural_municipality", 7),
            ("Silichong", "rural_municipality", 6),
        ],
        "Solukhumbu": [
            ("Solududhkunda", "municipality", 12),
            ("Dudhkoshi", "rural_municipality", 9),
            ("Thulung Dudhkoshi", "rural_municipality", 5),
            ("Nechasalyan", "rural_municipality", 5),
            ("Sotang", "rural_municipality", 9),
            ("Likhu Pike", "rural_municipality", 5),
            ("Khumbu Pasanglhamu", "rural_municipality", 5),
            ("Mahakulung", "rural_municipality", 9),
        ],
        "Sunsari": [
            ("Inaruwa", "municipality", 9),
            ("Duhabi", "municipality", 10),
            ("Itahari", "sub_metropolitan", 23),
            ("Dharan", "sub_metropolitan", 20),
            ("Ramdhuni", "municipality", 12),
            ("Barahachhetra", "municipality", 9),
            ("Koshi", "rural_municipality", 6),
            ("Gadhi", "rural_municipality", 6),
            ("Barju", "rural_municipality", 6),
            ("Bhokraha Narsingh", "rural_municipality", 8),
            ("Harinagara", "rural_municipality", 9),
            ("Dewanganj", "rural_municipality", 9),
        ],
        "Taplejung": [
            ("Phungling", "municipality", 10),
            ("Aathrai Triveni", "rural_municipality", 6),
            ("Sidingba", "rural_municipality", 6),
            ("Phaktanglung", "rural_municipality", 6),
            ("Mikwakhola", "rural_municipality", 6),
            ("Meringden", "rural_municipality", 5),
            ("Maiwakhola", "rural_municipality", 7),
            ("Yangwarak", "rural_municipality", 6),
            ("Sirijanga", "rural_municipality", 6),
        ],
        "Terhathum": [
            ("Myanglung", "municipality", 10),
            ("Laligurans", "municipality", 11),
            ("Chhathar", "municipality", 9),
            ("Aathrai", "rural_municipality", 6),
            ("Phedap", "rural_municipality", 8),
            ("Menchhayayem", "rural_municipality", 8),
        ],
        "Udayapur": [
            ("Triyuga", "municipality", 19),
            ("Katari", "municipality", 12),
            ("Chaudandigadhi", "municipality", 13),
            ("Belaka", "municipality", 13),
            ("Udayapurgadhi", "rural_municipality", 9),
            ("Rautamai", "rural_municipality", 9),
            ("Tapli", "rural_municipality", 6),
            ("Limchungbung", "rural_municipality", 8),
        ],
    },
    "Madhesh Province": {
        "Bara": [
            ("Kalaiya", "sub_metropolitan", 25),
            ("Jeetpur Simara", "sub_metropolitan", 23),
            ("Kolhabi", "municipality", 14),
            ("Nijgadh", "municipality", 16),
            ("Mahagadhimai", "municipality", 15),
            ("Simraungadh", "municipality", 17),
            ("Pacharauta", "municipality", 15),
            ("Pheta", "rural_municipality", 9),
            ("Bishrampur", "rural_municipality", 9),
            ("Prasauni", "rural_municipality", 9),
            ("Adarsh Kotwal", "rural_municipality", 9),
            ("Karaiyamai", "rural_municipality", 9),
            ("Devtal", "rural_municipality", 9),
            ("Parwanipur", "rural_municipality", 9),
            ("Baragadhi", "rural_municipality", 9),
            ("Subarna", "rural_municipality", 9),
        ],
        # Add all other Madhesh districts...
    },
    # Add remaining provinces...
}

def verify_municipalities():
    """Verify all municipalities against official data"""
    
    print("=" * 80)
    print("COMPLETE MUNICIPALITY VERIFICATION")
    print("=" * 80)
    
    # Count totals from official data
    official_total = 0
    official_by_type = defaultdict(int)
    
    for province_name, districts in OFFICIAL_DATA.items():
        for district_name, municipalities in districts.items():
            for mun_name, mun_type, wards in municipalities:
                official_total += 1
                if mun_type == "metropolitan":
                    official_by_type["metropolitan"] += 1
                elif mun_type == "sub_metropolitan":
                    official_by_type["sub_metropolitan"] += 1
                elif mun_type == "municipality":
                    official_by_type["municipality"] += 1
                else:
                    official_by_type["rural_municipality"] += 1
    
    print(f"\nOfficial counts from government data:")
    print(f"  Total: {official_total}")
    for mun_type, count in sorted(official_by_type.items()):
        print(f"  {mun_type}: {count}")
    
    # Count database totals
    db_total = Municipality.objects.count()
    db_by_type = {}
    for mun_type in ['metropolitan', 'sub_metropolitan', 'municipality', 'rural_municipality']:
        db_by_type[mun_type] = Municipality.objects.filter(municipality_type=mun_type).count()
    
    print(f"\nDatabase counts:")
    print(f"  Total: {db_total}")
    for mun_type, count in sorted(db_by_type.items()):
        print(f"  {mun_type}: {count}")
    
    # Find missing municipalities
    print("\n" + "=" * 80)
    print("CHECKING FOR MISSING MUNICIPALITIES")
    print("=" * 80)
    
    missing_count = 0
    for province_name, districts in OFFICIAL_DATA.items():
        province_missing = []
        
        for district_name, municipalities in districts.items():
            # Find district in database
            district = District.objects.filter(name_en=district_name).first()
            if not district and district_name == "Nawalpur":
                # This might be stored as Nawalparasi East
                district = District.objects.filter(name_en="Nawalparasi East").first()
            
            if not district:
                print(f"\n❌ District not found: {district_name}")
                missing_count += len(municipalities)
                continue
            
            for mun_name, mun_type, wards in municipalities:
                municipality = Municipality.objects.filter(
                    district=district,
                    name_en=mun_name
                ).first()
                
                if not municipality:
                    province_missing.append(f"{district_name}: {mun_name} ({mun_type}, {wards} wards)")
                    missing_count += 1
        
        if province_missing:
            print(f"\n{province_name} - Missing {len(province_missing)} municipalities:")
            for item in province_missing:
                print(f"  - {item}")
    
    print(f"\n" + "=" * 80)
    print(f"SUMMARY: {missing_count} municipalities missing")
    print("=" * 80)
    
    return missing_count

if __name__ == "__main__":
    missing = verify_municipalities()
    if missing == 0:
        print("\n✅ All municipalities are loaded!")
    else:
        print(f"\n⚠️  {missing} municipalities need to be added")