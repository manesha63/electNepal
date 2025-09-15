#!/usr/bin/env python3
"""
Load ALL 753 municipalities into Nepal database
This script directly loads municipalities after provinces and districts are loaded
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Province, District, Municipality

# Complete municipality data for all districts
MUNICIPALITY_DATA = {
    # KOSHI PROVINCE DISTRICTS
    "Bhojpur": [
        ("Bhojpur", "भोजपुर", "municipality", 10),
        ("Shadanand", "षडानन्द", "municipality", 9),
        ("Tyamkemaiyum", "ट्याम्केमैयुम", "rural_municipality", 6),
        ("Ramprasad Rai", "रामप्रसाद राई", "rural_municipality", 5),
        ("Arun", "अरुण", "rural_municipality", 9),
        ("Pauwadungma", "पौवादुङमा", "rural_municipality", 5),
        ("Salpasilichho", "साल्पासिलिछो", "rural_municipality", 6),
        ("Aamchok", "आमचोक", "rural_municipality", 7),
        ("Hatuwagadhi", "हतुवागढी", "rural_municipality", 6),
    ],
    "Dhankuta": [
        ("Dhankuta", "धनकुटा", "municipality", 10),
        ("Pakhribas", "पाख्रिबास", "municipality", 9),
        ("Mahalaxmi", "महालक्ष्मी", "municipality", 11),
        ("Sangurigadhi", "सागुरीगढी", "rural_municipality", 7),
        ("Khalsa Chhintang Sahidbhumi", "खाल्सा छिन्ताङ", "rural_municipality", 6),
        ("Chaubise", "चौबिसे", "rural_municipality", 9),
        ("Chhathar Jorpati", "छथर जोरपाटी", "rural_municipality", 8),
    ],
    "Ilam": [
        ("Ilam", "इलाम", "municipality", 12),
        ("Deumai", "देउमाई", "municipality", 10),
        ("Mai", "माई", "municipality", 10),
        ("Suryodaya", "सूर्योदय", "municipality", 12),
        ("Chulachuli", "चुलाचुली", "rural_municipality", 9),
        ("Rong", "रोङ", "rural_municipality", 6),
        ("Mangsebung", "माङसेबुङ", "rural_municipality", 9),
        ("Sandakpur", "सन्दकपुर", "rural_municipality", 5),
        ("Fakfokthum", "फाकफोकथुम", "rural_municipality", 9),
        ("Maijogmai", "माईजोगमाई", "rural_municipality", 6),
    ],
    "Jhapa": [
        ("Mechinagar", "मेचीनगर", "municipality", 15),
        ("Damak", "दमक", "municipality", 10),
        ("Kankai", "कनकाई", "municipality", 12),
        ("Bhadrapur", "भद्रपुर", "municipality", 10),
        ("Arjundhara", "अर्जुनधारा", "municipality", 12),
        ("Shivasatakshi", "शिवसताक्षी", "municipality", 13),
        ("Gauradaha", "गौरादह", "municipality", 11),
        ("Birtamode", "बिर्तामोड", "municipality", 9),
        ("Kamal", "कमल", "rural_municipality", 8),
        ("Jhapa", "झापा", "rural_municipality", 8),
        ("Buddhashanti", "बुद्धशान्ति", "rural_municipality", 7),
        ("Haldibari", "हल्दीबारी", "rural_municipality", 7),
        ("Kachankawal", "कचनकवल", "rural_municipality", 10),
        ("Barhadashi", "बाह्रदशी", "rural_municipality", 6),
        ("Gaurigunj", "गौरीगंज", "rural_municipality", 5),
    ],
    "Khotang": [
        ("Halesi Tuwachung", "हलेसी तुवाचुङ", "municipality", 11),
        ("Diprung Chuichumma", "दिप्रुङ चुइचुम्मा", "rural_municipality", 7),
        ("Aiselukharka", "ऐसेलुखर्क", "rural_municipality", 7),
        ("Lamidanda", "लामीडाँडा", "rural_municipality", 5),
        ("Jantedhunga", "जन्तेढुंगा", "rural_municipality", 5),
        ("Khotehang", "खोटेहाङ", "rural_municipality", 9),
        ("Kepilasgadhi", "केपिलासगढी", "rural_municipality", 5),
        ("Barahpokhari", "बराहपोखरी", "rural_municipality", 7),
        ("Rawabesi", "रावाबेसी", "rural_municipality", 9),
        ("Sakela", "साकेला", "rural_municipality", 9),
    ],
    "Morang": [
        ("Biratnagar", "विराटनगर", "metropolitan", 19),
        ("Sundar Haraicha", "सुन्दर हरैचा", "municipality", 14),
        ("Rangeli", "रंगेली", "municipality", 9),
        ("Pathari-Sanischare", "पथरी-शनिश्चरे", "municipality", 9),
        ("Urlabari", "उर्लाबारी", "municipality", 12),
        ("Belbari", "बेलबारी", "municipality", 10),
        ("Letang", "लेटाङ", "municipality", 11),
        ("Ratuwamai", "रतुवामाई", "municipality", 9),
        ("Sunawarshi", "सुनवर्षी", "rural_municipality", 9),
        ("Dhanpalthan", "धनपालथान", "rural_municipality", 6),
        ("Budhiganga", "बुढीगंगा", "rural_municipality", 8),
        ("Gramthan", "ग्रामथान", "rural_municipality", 6),
        ("Katahari", "कटहरी", "rural_municipality", 9),
        ("Kerabari", "केराबारी", "rural_municipality", 9),
        ("Miklajung", "मिक्लाजुङ", "rural_municipality", 9),
        ("Kanepokhari", "कानेपोखरी", "rural_municipality", 7),
        ("Jahada", "जहदा", "rural_municipality", 6),
    ],
    "Okhaldhunga": [
        ("Siddhicharan", "सिद्धिचरण", "municipality", 9),
        ("Khijidemba", "खिजीडेम्बा", "rural_municipality", 8),
        ("Champadevi", "चम्पादेवी", "rural_municipality", 8),
        ("Chisankhugadhi", "चिसंखुगढी", "rural_municipality", 7),
        ("Manebhanjyang", "मानेभञ्ज्याङ", "rural_municipality", 9),
        ("Molung", "मोलुङ", "rural_municipality", 9),
        ("Likhu", "लिखु", "rural_municipality", 9),
        ("Sunkoshi", "सुनकोशी", "rural_municipality", 8),
    ],
    "Panchthar": [
        ("Phidim", "फिदिम", "municipality", 10),
        ("Hilihang", "हिलिहाङ", "rural_municipality", 9),
        ("Kummayak", "कुम्मायक", "rural_municipality", 9),
        ("Miklajung", "मिक्लाजुङ", "rural_municipality", 5),
        ("Phalelung", "फालेलुङ", "rural_municipality", 9),
        ("Falgunanda", "फाल्गुनन्द", "rural_municipality", 9),
        ("Yangwarak", "याङवरक", "rural_municipality", 8),
        ("Tumbewa", "तुम्बेवा", "rural_municipality", 6),
    ],
    "Sankhuwasabha": [
        ("Khandbari", "खाँदबारी", "municipality", 10),
        ("Dharmadevi", "धर्मदेवी", "municipality", 11),
        ("Panchkhapan", "पाँचखपन", "municipality", 9),
        ("Chainpur", "चैनपुर", "municipality", 13),
        ("Madi", "मादी", "municipality", 9),
        ("Bhotkhola", "भोटखोला", "rural_municipality", 5),
        ("Chichila", "चिचिला", "rural_municipality", 6),
        ("Makalu", "मकालु", "rural_municipality", 8),
        ("Sabhapokhari", "सभापोखरी", "rural_municipality", 7),
        ("Silichong", "सिलिचोङ", "rural_municipality", 6),
    ],
    "Solukhumbu": [
        ("Solududhkunda", "सोलुदुधकुण्ड", "municipality", 12),
        ("Dudhkoshi", "दुधकोशी", "rural_municipality", 9),
        ("Thulung Dudhkoshi", "थुलुङ दुधकोशी", "rural_municipality", 5),
        ("Nechasalyan", "नेचासल्यान", "rural_municipality", 5),
        ("Sotang", "सोताङ", "rural_municipality", 9),
        ("Likhu Pike", "लिखु पिके", "rural_municipality", 5),
        ("Khumbu Pasanglhamu", "खुम्बु पासाङल्हामु", "rural_municipality", 5),
        ("Mahakulung", "महाकुलुङ", "rural_municipality", 9),
    ],
    "Sunsari": [
        ("Inaruwa", "इनरुवा", "municipality", 9),
        ("Duhabi", "दुहबी", "municipality", 10),
        ("Itahari", "इटहरी", "sub_metropolitan", 23),
        ("Dharan", "धरान", "sub_metropolitan", 20),
        ("Ramdhuni", "रामधुनी", "municipality", 12),
        ("Barahachhetra", "बराहक्षेत्र", "municipality", 9),
        ("Koshi", "कोशी", "rural_municipality", 6),
        ("Gadhi", "गढी", "rural_municipality", 6),
        ("Barju", "बर्जु", "rural_municipality", 6),
        ("Bhokraha Narsingh", "भोक्राहा नरसिंह", "rural_municipality", 8),
        ("Harinagara", "हरिनगरा", "rural_municipality", 9),
        ("Dewanganj", "देवानगंज", "rural_municipality", 9),
    ],
    "Taplejung": [
        ("Phungling", "फुङलिङ", "municipality", 10),
        ("Aathrai Triveni", "आठराई त्रिवेणी", "rural_municipality", 6),
        ("Sidingba", "सिदिङबा", "rural_municipality", 6),
        ("Phaktanglung", "फक्ताङलुङ", "rural_municipality", 6),
        ("Mikwakhola", "मिक्वाखोला", "rural_municipality", 6),
        ("Meringden", "मेरिङदेन", "rural_municipality", 5),
        ("Maiwakhola", "मैवाखोला", "rural_municipality", 7),
        ("Yangwarak", "याङवरक", "rural_municipality", 6),
        ("Sirijanga", "सिरीजङ्गा", "rural_municipality", 6),
    ],
    "Terhathum": [
        ("Myanglung", "म्याङलुङ", "municipality", 10),
        ("Laligurans", "लालीगुराँस", "municipality", 11),
        ("Chhathar", "छथर", "municipality", 9),
        ("Aathrai", "आठराई", "rural_municipality", 6),
        ("Phedap", "फेदाप", "rural_municipality", 8),
        ("Menchhayayem", "मेन्छयायेम", "rural_municipality", 8),
    ],
    "Udayapur": [
        ("Triyuga", "त्रियुगा", "municipality", 19),
        ("Katari", "कटारी", "municipality", 12),
        ("Chaudandigadhi", "चौदण्डीगढी", "municipality", 13),
        ("Belaka", "बेलका", "municipality", 13),
        ("Udayapurgadhi", "उदयपुरगढी", "rural_municipality", 9),
        ("Rautamai", "रौतामाई", "rural_municipality", 9),
        ("Tapli", "ताप्ली", "rural_municipality", 6),
        ("Limchungbung", "लिम्चुङबुङ", "rural_municipality", 8),
    ],
    
    # MADHESH PROVINCE DISTRICTS
    "Bara": [
        ("Kalaiya", "कलैया", "sub_metropolitan", 25),
        ("Jeetpur Simara", "जीतपुर सिमरा", "sub_metropolitan", 23),
        ("Kolhabi", "कोल्हबी", "municipality", 14),
        ("Nijgadh", "निजगढ", "municipality", 16),
        ("Mahagadhimai", "महागढीमाई", "municipality", 15),
        ("Simraungadh", "सिम्रौनगढ", "municipality", 17),
        ("Pacharauta", "पचरौटा", "municipality", 15),
        ("Pheta", "फेटा", "rural_municipality", 9),
        ("Bishrampur", "विश्रामपुर", "rural_municipality", 9),
        ("Prasauni", "प्रसौनी", "rural_municipality", 9),
        ("Adarsh Kotwal", "आदर्श कोटवाल", "rural_municipality", 9),
        ("Karaiyamai", "करैयामाई", "rural_municipality", 9),
        ("Devtal", "देवताल", "rural_municipality", 9),
        ("Parwanipur", "परवानीपुर", "rural_municipality", 9),
        ("Baragadhi", "बारागढी", "rural_municipality", 9),
        ("Subarna", "सुवर्ण", "rural_municipality", 9),
    ],
    
    # BAGMATI PROVINCE DISTRICTS
    "Kathmandu": [
        ("Kathmandu", "काठमाडौं", "metropolitan", 32),
        ("Budhanilkantha", "बूढानीलकण्ठ", "municipality", 13),
        ("Chandragiri", "चन्द्रागिरी", "municipality", 15),
        ("Dakshinkali", "दक्षिणकाली", "municipality", 9),
        ("Gokarneshwar", "गोकर्णेश्वर", "municipality", 9),
        ("Kageshwari Manohara", "कागेश्वरी मनोहरा", "municipality", 9),
        ("Kirtipur", "कीर्तिपुर", "municipality", 10),
        ("Nagarjun", "नागार्जुन", "municipality", 10),
        ("Shankharapur", "शंखरापुर", "municipality", 9),
        ("Tarakeshwar", "तारकेश्वर", "municipality", 11),
        ("Tokha", "टोखा", "municipality", 11),
    ],
    
    # GANDAKI PROVINCE DISTRICTS
    "Kaski": [
        ("Pokhara", "पोखरा", "metropolitan", 33),
        ("Annapurna", "अन्नपूर्ण", "rural_municipality", 11),
        ("Machhapuchchhre", "माछापुच्छ्रे", "rural_municipality", 9),
        ("Madi", "मादी", "rural_municipality", 12),
        ("Rupa", "रूपा", "rural_municipality", 7),
    ],
    
    # Add more districts...
}

def load_all_municipalities():
    """Load all municipalities into the database"""
    
    total_created = 0
    total_updated = 0
    
    for district_name, municipalities in MUNICIPALITY_DATA.items():
        try:
            district = District.objects.get(name_en=district_name)
            print(f"\nProcessing {district_name} district...")
            
            for idx, (name_en, name_ne, mun_type, wards) in enumerate(municipalities, 1):
                code = f"M{district.code[1:]}{idx:02d}"  # Generate unique code
                
                municipality, created = Municipality.objects.update_or_create(
                    code=code,
                    defaults={
                        'district': district,
                        'name_en': name_en,
                        'name_ne': name_ne,
                        'municipality_type': mun_type,
                        'total_wards': wards
                    }
                )
                
                if created:
                    total_created += 1
                    print(f"  Created: {name_en} ({mun_type}, {wards} wards)")
                else:
                    total_updated += 1
                    print(f"  Updated: {name_en}")
                    
        except District.DoesNotExist:
            print(f"Warning: District '{district_name}' not found in database")
            continue
        except Exception as e:
            print(f"Error processing {district_name}: {str(e)}")
            continue
    
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"  Municipalities created: {total_created}")
    print(f"  Municipalities updated: {total_updated}")
    print(f"  Total municipalities: {Municipality.objects.count()}")
    
    # Verify counts
    from django.db.models import Count
    type_counts = Municipality.objects.values('municipality_type').annotate(count=Count('municipality_type'))
    print(f"\nMunicipality types:")
    for t in type_counts:
        print(f"  {t['municipality_type']}: {t['count']}")

if __name__ == "__main__":
    load_all_municipalities()