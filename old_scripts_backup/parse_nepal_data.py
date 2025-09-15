import json
import re

# Parse the text data into structured JSON
def parse_nepal_data():
    data = {
        "provinces": []
    }
    
    # Province 1 - Koshi
    province1 = {
        "code": "P1",
        "name_en": "Koshi Province", 
        "name_ne": "कोशी प्रदेश",
        "capital": "Biratnagar",
        "districts": []
    }
    
    # Bhojpur District
    bhojpur = {
        "code": "D01",
        "name_en": "Bhojpur",
        "name_ne": "भोजपुर",
        "municipalities": [
            {"name_en": "Bhojpur", "name_ne": "भोजपुर", "type": "municipality", "wards": 10},
            {"name_en": "Shadanand", "name_ne": "षडानन्द", "type": "municipality", "wards": 9},
            {"name_en": "Tyamkemaiyum", "name_ne": "ट्याम्केमैयुम", "type": "rural_municipality", "wards": 6},
            {"name_en": "Ramprasad Rai", "name_ne": "रामप्रसाद राई", "type": "rural_municipality", "wards": 5},
            {"name_en": "Arun", "name_ne": "अरुण", "type": "rural_municipality", "wards": 9},
            {"name_en": "Pauwadungma", "name_ne": "पौवादुङमा", "type": "rural_municipality", "wards": 5},
            {"name_en": "Salpasilichho", "name_ne": "साल्पासिलिछो", "type": "rural_municipality", "wards": 6},
            {"name_en": "Aamchok", "name_ne": "आमचोक", "type": "rural_municipality", "wards": 7},
            {"name_en": "Hatuwagadhi", "name_ne": "हतुवागढी", "type": "rural_municipality", "wards": 6}
        ]
    }
    
    # Dhankuta District  
    dhankuta = {
        "code": "D02",
        "name_en": "Dhankuta",
        "name_ne": "धनकुटा",
        "municipalities": [
            {"name_en": "Dhankuta", "name_ne": "धनकुटा", "type": "municipality", "wards": 10},
            {"name_en": "Pakhribas", "name_ne": "पाख्रिबास", "type": "municipality", "wards": 9},
            {"name_en": "Mahalaxmi", "name_ne": "महालक्ष्मी", "type": "municipality", "wards": 11},
            {"name_en": "Sangurigadhi", "name_ne": "सागुरीगढी", "type": "rural_municipality", "wards": 7},
            {"name_en": "Khalsa Chhintang Sahidbhumi", "name_ne": "खाल्सा छिन्ताङ सहिदभूमि", "type": "rural_municipality", "wards": 6},
            {"name_en": "Chaubise", "name_ne": "चौबिसे", "type": "rural_municipality", "wards": 9},
            {"name_en": "Chhathar Jorpati", "name_ne": "छथर जोरपाटी", "type": "rural_municipality", "wards": 8}
        ]
    }
    
    # Ilam District
    ilam = {
        "code": "D03",
        "name_en": "Ilam",
        "name_ne": "इलाम",
        "municipalities": [
            {"name_en": "Ilam", "name_ne": "इलाम", "type": "municipality", "wards": 12},
            {"name_en": "Deumai", "name_ne": "देउमाई", "type": "municipality", "wards": 10},
            {"name_en": "Mai", "name_ne": "माई", "type": "municipality", "wards": 10},
            {"name_en": "Suryodaya", "name_ne": "सूर्योदय", "type": "municipality", "wards": 12},
            {"name_en": "Chulachuli", "name_ne": "चुलाचुली", "type": "rural_municipality", "wards": 9},
            {"name_en": "Rong", "name_ne": "रोङ", "type": "rural_municipality", "wards": 6},
            {"name_en": "Mangsebung", "name_ne": "माङसेबुङ", "type": "rural_municipality", "wards": 9},
            {"name_en": "Sandakpur", "name_ne": "सन्दकपुर", "type": "rural_municipality", "wards": 5},
            {"name_en": "Fakfokthum", "name_ne": "फाकफोकथुम", "type": "rural_municipality", "wards": 9},
            {"name_en": "Maijogmai", "name_ne": "माईजोगमाई", "type": "rural_municipality", "wards": 6}
        ]
    }
    
    # Jhapa District
    jhapa = {
        "code": "D04",
        "name_en": "Jhapa",
        "name_ne": "झापा",
        "municipalities": [
            {"name_en": "Mechinagar", "name_ne": "मेचीनगर", "type": "municipality", "wards": 15},
            {"name_en": "Damak", "name_ne": "दमक", "type": "municipality", "wards": 10},
            {"name_en": "Kankai", "name_ne": "कनकाई", "type": "municipality", "wards": 12},
            {"name_en": "Bhadrapur", "name_ne": "भद्रपुर", "type": "municipality", "wards": 10},
            {"name_en": "Arjundhara", "name_ne": "अर्जुनधारा", "type": "municipality", "wards": 12},
            {"name_en": "Shivasatakshi", "name_ne": "शिवसताक्षी", "type": "municipality", "wards": 13},
            {"name_en": "Gauradaha", "name_ne": "गौरादह", "type": "municipality", "wards": 11},
            {"name_en": "Birtamode", "name_ne": "बिर्तामोड", "type": "municipality", "wards": 9},
            {"name_en": "Kamal", "name_ne": "कमल", "type": "rural_municipality", "wards": 8},
            {"name_en": "Jhapa", "name_ne": "झापा", "type": "rural_municipality", "wards": 8},
            {"name_en": "Buddhashanti", "name_ne": "बुद्धशान्ति", "type": "rural_municipality", "wards": 7},
            {"name_en": "Haldibari", "name_ne": "हल्दीबारी", "type": "rural_municipality", "wards": 7},
            {"name_en": "Kachankawal", "name_ne": "कचनकवल", "type": "rural_municipality", "wards": 10},
            {"name_en": "Barhadashi", "name_ne": "बाह्रदशी", "type": "rural_municipality", "wards": 6},
            {"name_en": "Gaurigunj", "name_ne": "गौरीगंज", "type": "rural_municipality", "wards": 5}
        ]
    }
    
    # Continue with remaining districts...
    # Due to space, I'll create a comprehensive file
    
    province1["districts"] = [bhojpur, dhankuta, ilam, jhapa]
    data["provinces"].append(province1)
    
    return data

# Write the parsed data
parsed_data = parse_nepal_data()
with open('/home/manesha/electNepal/data/nepal_complete.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=2)

print("Created initial structure. Now creating full parser...")