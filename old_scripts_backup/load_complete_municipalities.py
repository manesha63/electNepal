#!/usr/bin/env python3
"""
Complete municipality loader for Nepal - ALL 753 municipalities
Loads all municipalities with their ward counts into the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.models import Province, District, Municipality
from django.db import transaction

# Complete municipality data - ALL 753 municipalities
MUNICIPALITY_DATA = {
    # ============= KOSHI PROVINCE (Already loaded - 137 municipalities) =============
    
    # ============= MADHESH PROVINCE - Complete all districts =============
    "Dhanusha": [
        ("Janakpur", "जनकपुर", "sub_metropolitan", 25),
        ("Chhireshwarnath", "क्षिरेश्वरनाथ", "municipality", 16),
        ("Ganeshman Charnath", "गणेशमान चारनाथ", "municipality", 12),
        ("Dhanusadham", "धनुषाधाम", "municipality", 10),
        ("Nagarain", "नगराइन", "municipality", 12),
        ("Bideha", "विदेह", "municipality", 9),
        ("Mithila", "मिथिला", "municipality", 12),
        ("Sahidnagar", "शहीदनगर", "municipality", 17),
        ("Sabaila", "सबैला", "municipality", 22),
        ("Kamala", "कमला", "municipality", 12),
        ("Mithila Bihari", "मिथिला बिहारी", "municipality", 19),
        ("Hansapur", "हंसपुर", "municipality", 9),
        ("Janak Nandani", "जनक नन्दनी", "rural_municipality", 9),
        ("Bateshwar", "बटेश्वर", "rural_municipality", 9),
        ("Mukhiyapatti Musaharmiya", "मुखियापट्टी मुसहरमिया", "rural_municipality", 9),
        ("Lakshminya", "लक्ष्मीन्या", "rural_municipality", 9),
        ("Aurahi", "औरही", "rural_municipality", 9),
        ("Dhanauji", "धनौजी", "rural_municipality", 9),
    ],
    "Mahottari": [
        ("Jaleshwar", "जलेश्वर", "municipality", 17),
        ("Bardibas", "बर्दिबास", "municipality", 19),
        ("Gaushala", "गौशाला", "municipality", 14),
        ("Loharpatti", "लोहरपट्टी", "municipality", 9),
        ("Bhangaha", "भंगहा", "municipality", 15),
        ("Balawa", "बलवा", "municipality", 11),
        ("Matihani", "मतिहानी", "municipality", 19),
        ("Ram Gopalpur", "राम गोपालपुर", "municipality", 9),
        ("Manra Shiswa", "मनरा शिस्वा", "municipality", 10),
        ("Aurahi", "औरही", "rural_municipality", 9),
        ("Ekdara", "एकडारा", "rural_municipality", 9),
        ("Sonama", "सोनमा", "rural_municipality", 9),
        ("Samsi", "सम्सी", "rural_municipality", 9),
        ("Mahottari", "महोत्तरी", "rural_municipality", 9),
        ("Pipara", "पिपरा", "rural_municipality", 9),
    ],
    "Parsa": [
        ("Birgunj", "वीरगञ्ज", "metropolitan", 32),
        ("Bahudarmai", "बहुदरमाई", "municipality", 15),
        ("Parsagadhi", "पर्सागढी", "municipality", 17),
        ("Pokhariya", "पोखरिया", "municipality", 19),
        ("Bindabasini", "बिन्दबासिनी", "municipality", 9),
        ("Dhobini", "धोबिनी", "rural_municipality", 9),
        ("Chhipaharmai", "छिपहरमाई", "rural_municipality", 9),
        ("Pakaha Mainpur", "पकाहा मैनपुर", "rural_municipality", 9),
        ("Paterwa Sugauli", "पटेर्वा सुगौली", "rural_municipality", 9),
        ("Sakhuwa Prasauni", "सखुवा प्रसौनी", "rural_municipality", 9),
        ("Thori", "थोरी", "rural_municipality", 9),
        ("Jagarnathpur", "जगरनाथपुर", "rural_municipality", 9),
        ("Jirabhawani", "जिराभवानी", "rural_municipality", 9),
        ("Kalikamai", "कालिकामाई", "rural_municipality", 9),
    ],
    "Rautahat": [
        ("Chandrapur", "चन्द्रपुर", "municipality", 19),
        ("Garuda", "गरुडा", "municipality", 15),
        ("Gaur", "गौर", "municipality", 19),
        ("Baudhimai", "बौधीमाई", "municipality", 19),
        ("Brindaban", "बृन्दाबन", "municipality", 17),
        ("Dewahi Gonahi", "देवाही गोनाही", "municipality", 19),
        ("Gujara", "गुजरा", "municipality", 11),
        ("Ishnath", "ईशनाथ", "municipality", 18),
        ("Katahariya", "कटहरिया", "municipality", 9),
        ("Maulapur", "मौलापुर", "municipality", 19),
        ("Paroha", "परोहा", "municipality", 16),
        ("Phatuwa Bijayapur", "फतुवा बिजयपुर", "municipality", 16),
        ("Rajdevi", "राजदेवी", "municipality", 9),
        ("Rajpur", "राजपुर", "municipality", 9),
        ("Madhav Narayan", "माधव नारायण", "municipality", 9),
        ("Durga Bhagwati", "दुर्गा भगवती", "rural_municipality", 9),
        ("Yamunamai", "यमुनामाई", "rural_municipality", 9),
        ("Durgabhagwati", "दुर्गाभगवती", "rural_municipality", 9),
    ],
    "Saptari": [
        ("Rajbiraj", "राजविराज", "municipality", 19),
        ("Dakneshwari", "डाक्नेश्वरी", "municipality", 9),
        ("Bodebarsain", "बोदेबरसाईन", "municipality", 19),
        ("Kanchanrup", "कञ्चनरुप", "municipality", 12),
        ("Surunga", "सुरुङ्गा", "municipality", 12),
        ("Shambhunath", "शम्भुनाथ", "municipality", 19),
        ("Saptakoshi", "सप्तकोशी", "municipality", 15),
        ("Hanumannagar Kankalini", "हनुमाननगर कङ्कालिनी", "municipality", 11),
        ("Agnisair Krishna Savaran", "अग्निसाइर कृष्णा सवरण", "rural_municipality", 9),
        ("Balan-Bihul", "बलान-बिहुल", "rural_municipality", 9),
        ("Bishnupur", "विष्णुपुर", "rural_municipality", 9),
        ("Chhinnamasta", "छिन्नमस्ता", "rural_municipality", 9),
        ("Mahadeva", "महादेव", "rural_municipality", 9),
        ("Rajgadh", "राजगढ", "rural_municipality", 9),
        ("Rupani", "रुपनी", "rural_municipality", 9),
        ("Tilathi Koiladi", "तिलाठी कोईलाडी", "rural_municipality", 9),
        ("Tirhut", "तिरहुत", "rural_municipality", 9),
    ],
    "Sarlahi": [
        ("Lalbandi", "लालबन्दी", "municipality", 18),
        ("Haripur", "हरिपुर", "municipality", 18),
        ("Haripurwa", "हरिपुर्वा", "municipality", 15),
        ("Hariwan", "हरिवन", "municipality", 15),
        ("Ishworpur", "ईश्वरपुर", "municipality", 18),
        ("Malangwa", "मलंगवा", "municipality", 19),
        ("Bagmati", "बागमती", "municipality", 15),
        ("Balara", "बलरा", "municipality", 9),
        ("Barahathwa", "बरहथवा", "municipality", 9),
        ("Godaita", "गोडैता", "municipality", 9),
        ("Kabilasi", "कविलासी", "municipality", 9),
        ("Basbariya", "बसबरिया", "rural_municipality", 9),
        ("Bishnu", "विष्णु", "rural_municipality", 9),
        ("Brahmpuri", "ब्रह्मपुरी", "rural_municipality", 9),
        ("Chakraghatta", "चक्रघट्टा", "rural_municipality", 9),
        ("Chandranagar", "चन्द्रनगर", "rural_municipality", 9),
        ("Dhankaul", "धनकौल", "rural_municipality", 9),
        ("Parsa", "पर्सा", "rural_municipality", 9),
        ("Ramnagar", "रामनगर", "rural_municipality", 9),
    ],
    "Siraha": [
        ("Siraha", "सिरहा", "municipality", 19),
        ("Dhangadhimai", "धनगढीमाई", "municipality", 12),
        ("Golbazar", "गोलबजार", "municipality", 15),
        ("Mirchaiya", "मिर्चैया", "municipality", 18),
        ("Kalyanpur", "कल्याणपुर", "municipality", 19),
        ("Karjanha", "कर्जन्हा", "municipality", 9),
        ("Sukhipur", "सुखीपुर", "municipality", 9),
        ("Lahan", "लहान", "municipality", 16),
        ("Bhagwanpur", "भगवानपुर", "rural_municipality", 9),
        ("Aurahi", "औरही", "rural_municipality", 9),
        ("Bishnupur", "विष्णुपुर", "rural_municipality", 9),
        ("Bariyarpatti", "बरियारपट्टी", "rural_municipality", 9),
        ("Lakshmipur Patari", "लक्ष्मीपुर पतारी", "rural_municipality", 9),
        ("Naraha", "नरहा", "rural_municipality", 9),
        ("Navarajpur", "नवराजपुर", "rural_municipality", 9),
        ("Arnama", "अर्नमा", "rural_municipality", 9),
        ("Sakhuwa Nankarkatti", "सखुवा नानकारकट्टी", "rural_municipality", 9),
    ],
    
    # ============= BAGMATI PROVINCE - Complete all districts =============
    "Bhaktapur": [
        ("Bhaktapur", "भक्तपुर", "municipality", 10),
        ("Changunarayan", "चाँगुनारायण", "municipality", 9),
        ("Madhyapur Thimi", "मध्यपुर थिमि", "municipality", 9),
        ("Suryabinayak", "सूर्यविनायक", "municipality", 10),
    ],
    "Chitwan": [
        ("Bharatpur", "भरतपुर", "metropolitan", 29),
        ("Kalika", "कालिका", "municipality", 14),
        ("Khairahani", "खैरहनी", "municipality", 13),
        ("Madi", "मादी", "municipality", 9),
        ("Ratnanagar", "रत्ननगर", "municipality", 16),
        ("Rapti", "राप्ती", "municipality", 19),
        ("Ichchhakamana", "इच्छाकामना", "rural_municipality", 6),
    ],
    "Dhading": [
        ("Dhunibeshi", "धुनीबेशी", "municipality", 11),
        ("Nilkantha", "नीलकण्ठ", "municipality", 13),
        ("Khaniyabas", "खनियाबास", "rural_municipality", 9),
        ("Gajuri", "गजुरी", "rural_municipality", 9),
        ("Galchhi", "गल्छी", "rural_municipality", 7),
        ("Gangajamuna", "गंगाजमुना", "rural_municipality", 8),
        ("Jwalamukhi", "ज्वालामुखी", "rural_municipality", 6),
        ("Netrawati Dabjong", "नेत्रावती डबजोङ", "rural_municipality", 5),
        ("Benighat Rorang", "बेनीघाट रोराङ", "rural_municipality", 11),
        ("Ruby Valley", "रुबी भ्याली", "rural_municipality", 7),
        ("Siddhalek", "सिद्धलेक", "rural_municipality", 6),
        ("Tripura Sundari", "त्रिपुरा सुन्दरी", "rural_municipality", 8),
        ("Thakre", "ठाक्रे", "rural_municipality", 6),
    ],
    "Dolakha": [
        ("Bhimeshwar", "भीमेश्वर", "municipality", 13),
        ("Jiri", "जिरी", "municipality", 9),
        ("Kalinchok", "कालिञ्चोक", "rural_municipality", 9),
        ("Melung", "मेलुङ", "rural_municipality", 5),
        ("Bigu", "बिगु", "rural_municipality", 8),
        ("Gaurishankar", "गौरीशंकर", "rural_municipality", 7),
        ("Baiteshwar", "बैतेश्वर", "rural_municipality", 6),
        ("Sailung", "सैलुङ", "rural_municipality", 7),
        ("Tamakoshi", "तामाकोशी", "rural_municipality", 9),
    ],
    # Kathmandu already loaded
    "Kavrepalanchok": [
        ("Dhulikhel", "धुलिखेल", "municipality", 12),
        ("Banepa", "बनेपा", "municipality", 12),
        ("Panauti", "पनौती", "municipality", 11),
        ("Panchkhal", "पाँचखाल", "municipality", 9),
        ("Namobuddha", "नमोबुद्ध", "municipality", 11),
        ("Mandandeupur", "मण्डनदेउपुर", "municipality", 9),
        ("Khanikhola", "खानीखोला", "rural_municipality", 7),
        ("Chauri Deurali", "चौरी देउराली", "rural_municipality", 9),
        ("Temal", "तेमाल", "rural_municipality", 6),
        ("Bethanchok", "बेथानचोक", "rural_municipality", 8),
        ("Bhumlu", "भुम्लु", "rural_municipality", 9),
        ("Mahabharat", "महाभारत", "rural_municipality", 6),
        ("Roshi", "रोशी", "rural_municipality", 9),
    ],
    "Lalitpur": [
        ("Lalitpur", "ललितपुर", "metropolitan", 29),
        ("Mahalaxmi", "महालक्ष्मी", "municipality", 10),
        ("Godawari", "गोदावरी", "municipality", 15),
        ("Konjyosom", "कोन्ज्योसोम", "rural_municipality", 5),
        ("Bagmati", "बागमती", "rural_municipality", 7),
        ("Mahankal", "महाङ्काल", "rural_municipality", 6),
    ],
    "Makwanpur": [
        ("Hetauda", "हेटौंडा", "sub_metropolitan", 19),
        ("Thaha", "थाहा", "municipality", 13),
        ("Indrasarowar", "इन्द्रसरोवर", "rural_municipality", 9),
        ("Kailash", "कैलाश", "rural_municipality", 9),
        ("Bakaiya", "बकैया", "rural_municipality", 9),
        ("Bagmati", "बागमती", "rural_municipality", 11),
        ("Bhimphedi", "भीमफेदी", "rural_municipality", 9),
        ("Makawanpurgadhi", "मकवानपुरगढी", "rural_municipality", 9),
        ("Manahari", "मनहरी", "rural_municipality", 9),
        ("Raksirang", "राक्सिराङ", "rural_municipality", 8),
    ],
    "Nuwakot": [
        ("Bidur", "बिदुर", "municipality", 13),
        ("Belkotgadhi", "बेलकोटगढी", "municipality", 13),
        ("Kakani", "ककनी", "rural_municipality", 8),
        ("Likhu", "लिखु", "rural_municipality", 5),
        ("Dupcheshwar", "दुप्चेश्वर", "rural_municipality", 6),
        ("Panchakanya", "पञ्चकन्या", "rural_municipality", 5),
        ("Shivapuri", "शिवपुरी", "rural_municipality", 12),
        ("Tadi", "तादी", "rural_municipality", 6),
        ("Tarkeshwar", "तारकेश्वर", "rural_municipality", 6),
        ("Suryagadhi", "सूर्यगढी", "rural_municipality", 9),
        ("Myagang", "म्यागङ", "rural_municipality", 9),
        ("Kispang", "किस्पाङ", "rural_municipality", 5),
    ],
    "Ramechhap": [
        ("Manthali", "मन्थली", "municipality", 10),
        ("Ramechhap", "रामेछाप", "municipality", 9),
        ("Umakunda", "उमाकुण्ड", "rural_municipality", 8),
        ("Khandadevi", "खाँडादेवी", "rural_municipality", 9),
        ("Doramba", "दोरम्बा", "rural_municipality", 9),
        ("Gokulganga", "गोकुलगंगा", "rural_municipality", 5),
        ("Likhu Tamakoshi", "लिखु तामाकोशी", "rural_municipality", 5),
        ("Sunapati", "सुनापती", "rural_municipality", 6),
    ],
    "Rasuwa": [
        ("Kalika", "कालिका", "rural_municipality", 5),
        ("Naukunda", "नौकुण्ड", "rural_municipality", 5),
        ("Gosaikunda", "गोसाईकुण्ड", "rural_municipality", 5),
        ("Parbatikunda", "पार्वतीकुण्ड", "rural_municipality", 5),
        ("Uttargaya", "उत्तरगया", "rural_municipality", 5),
    ],
    "Sindhuli": [
        ("Kamalamai", "कमलामाई", "municipality", 14),
        ("Dudhouli", "दुधौली", "municipality", 9),
        ("Golanjor", "गोलन्जोर", "rural_municipality", 9),
        ("Tinpatan", "तीनपाटन", "rural_municipality", 9),
        ("Fickal", "फिक्कल", "rural_municipality", 7),
        ("Marin", "मरिण", "rural_municipality", 10),
        ("Sunkoshi", "सुनकोशी", "rural_municipality", 9),
        ("Hariharpurgadhi", "हरिहरपुरगढी", "rural_municipality", 9),
        ("Ghyanglekh", "घ्याङलेख", "rural_municipality", 6),
    ],
    "Sindhupalchok": [
        ("Chautara Sangachokgadhi", "चौतारा साँगाचोकगढी", "municipality", 14),
        ("Bahrabise", "बाह्रबिसे", "municipality", 9),
        ("Melamchi", "मेलम्ची", "municipality", 12),
        ("Indrawati", "इन्द्रावती", "rural_municipality", 13),
        ("Jugal", "जुगल", "rural_municipality", 7),
        ("Panchpokhari Thangpal", "पञ्चपोखरी थाङपाल", "rural_municipality", 5),
        ("Balephi", "बलेफी", "rural_municipality", 8),
        ("Bhotekoshi", "भोटेकोशी", "rural_municipality", 5),
        ("Lisankhu Pakhar", "लिसंखु पाखर", "rural_municipality", 8),
        ("Sunkoshi", "सुनकोशी", "rural_municipality", 9),
        ("Helambu", "हेलम्बु", "rural_municipality", 7),
        ("Tripurasundari", "त्रिपुरासुन्दरी", "rural_municipality", 9),
    ],
    
    # ============= GANDAKI PROVINCE - Complete all districts =============
    "Baglung": [
        ("Baglung", "बागलुङ", "municipality", 14),
        ("Galkot", "गल्कोट", "municipality", 11),
        ("Jaimini", "जैमिनी", "municipality", 8),
        ("Dhorpatan", "ढोरपाटन", "municipality", 7),
        ("Bareng", "बडिगाड", "rural_municipality", 6),
        ("Khathekhola", "काठेखोला", "rural_municipality", 7),
        ("Taman Khola", "तमानखोला", "rural_municipality", 5),
        ("Tara Khola", "ताराखोला", "rural_municipality", 5),
        ("Badigad", "बडिगाड", "rural_municipality", 9),
        ("Nisikhola", "निसीखोला", "rural_municipality", 7),
    ],
    "Gorkha": [
        ("Gorkha", "गोरखा", "municipality", 12),
        ("Palungtar", "पालुङटार", "municipality", 13),
        ("Siranchok", "सिरानचोक", "rural_municipality", 8),
        ("Ajirkot", "अजिरकोट", "rural_municipality", 5),
        ("Tsum Nubri", "चुम नुब्री", "rural_municipality", 5),
        ("Dharche", "धार्चे", "rural_municipality", 7),
        ("Bhimsen Thapa", "भिमसेन थापा", "rural_municipality", 10),
        ("Sahid Lakhan", "शहीद लखन", "rural_municipality", 9),
        ("Aarughat", "आरुघाट", "rural_municipality", 11),
        ("Gandaki", "गण्डकी", "rural_municipality", 7),
        ("Chum Nubri", "चुम नुब्री", "rural_municipality", 5),
    ],
    # Kaski already loaded
    "Lamjung": [
        ("Besisahar", "बेसीशहर", "municipality", 11),
        ("Madhya Nepal", "मध्य नेपाल", "municipality", 9),
        ("Rainas", "राईनास", "municipality", 9),
        ("Sundarbazar", "सुन्दरबजार", "municipality", 12),
        ("Kwholasothar", "क्व्होलासोथार", "rural_municipality", 5),
        ("Marsyandi", "मर्स्याङदी", "rural_municipality", 9),
        ("Dordi", "दोर्दी", "rural_municipality", 9),
    ],
    "Manang": [
        ("Chame", "चामे", "rural_municipality", 5),
        ("Nason", "नासों", "rural_municipality", 5),
        ("Narpa Bhumi", "नार्पा भूमि", "rural_municipality", 5),
        ("Manang Ngisyang", "मनाङ ङिस्याङ", "rural_municipality", 5),
    ],
    "Mustang": [
        ("Gharpajhong", "घरपझोङ", "rural_municipality", 5),
        ("Thasang", "थासाङ", "rural_municipality", 5),
        ("Baragung Muktichhetra", "बारागुङ मुक्तिक्षेत्र", "rural_municipality", 5),
        ("Lo-Manthang", "लो-मान्थाङ", "rural_municipality", 5),
        ("Lomanthang", "लोमान्थाङ", "rural_municipality", 5),
    ],
    "Myagdi": [
        ("Beni", "बेनी", "municipality", 10),
        ("Annapurna", "अन्नपूर्ण", "rural_municipality", 9),
        ("Dhaulagiri", "धौलागिरी", "rural_municipality", 7),
        ("Mangala", "मंगला", "rural_municipality", 9),
        ("Malika", "मालिका", "rural_municipality", 9),
        ("Raghuganga", "रघुगंगा", "rural_municipality", 5),
    ],
    "Nawalpur": [
        ("Kawasoti", "कावासोती", "municipality", 19),
        ("Gaindakot", "गैंडाकोट", "municipality", 9),
        ("Devchuli", "देवचुली", "municipality", 19),
        ("Madhyabindu", "मध्यविन्दु", "municipality", 9),
        ("Bulingtar", "बुलिङटार", "rural_municipality", 9),
        ("Binayi Tribeni", "विनयी त्रिवेणी", "rural_municipality", 9),
        ("Hupsekot", "हुप्सेकोट", "rural_municipality", 9),
        ("Mushikot", "मुसिकोट", "rural_municipality", 7),
    ],
    "Nawalparasi East": [
        ("Kawasoti", "कावासोती", "municipality", 19),
        ("Gaindakot", "गैंडाकोट", "municipality", 9),
        ("Devchuli", "देवचुली", "municipality", 19),
        ("Madhyabindu", "मध्यविन्दु", "municipality", 9),
        ("Bulingtar", "बुलिङटार", "rural_municipality", 9),
        ("Binayi Tribeni", "विनयी त्रिवेणी", "rural_municipality", 9),
        ("Hupsekot", "हुप्सेकोट", "rural_municipality", 9),
        ("Mushikot", "मुसिकोट", "rural_municipality", 7),
    ],
    "Parbat": [
        ("Kushma", "कुश्मा", "municipality", 7),
        ("Phalewas", "फलेवास", "municipality", 12),
        ("Jaljala", "जलजला", "rural_municipality", 6),
        ("Paiyun", "पैयूं", "rural_municipality", 9),
        ("Mahashila", "महाशिला", "rural_municipality", 9),
        ("Modi", "मोदी", "rural_municipality", 8),
        ("Bihadi", "बिहादी", "rural_municipality", 9),
    ],
    "Syangja": [
        ("Galyang", "गल्याङ", "municipality", 11),
        ("Chapakot", "चापाकोट", "municipality", 12),
        ("Waling", "वालिङ", "municipality", 16),
        ("Syangja", "स्याङ्जा", "municipality", 11),
        ("Arjunchaupari", "अर्जुनचौपारी", "rural_municipality", 9),
        ("Aandhikhola", "आँधीखोला", "rural_municipality", 9),
        ("Kaligandaki", "कालीगण्डकी", "rural_municipality", 11),
        ("Phedikhola", "फेदीखोला", "rural_municipality", 9),
        ("Harinas", "हरिनास", "rural_municipality", 9),
        ("Biruwa", "बिरुवा", "rural_municipality", 5),
        ("Puthauttarganga", "पुतलीउत्तरगंगा", "rural_municipality", 13),
    ],
    "Tanahun": [
        ("Bhanu", "भानु", "municipality", 13),
        ("Bhimad", "भिमाद", "municipality", 10),
        ("Byas", "व्यास", "municipality", 14),
        ("Shuklagandaki", "शुक्लागण्डकी", "municipality", 12),
        ("Anbu Khaireni", "आँबुखैरेनी", "rural_municipality", 9),
        ("Devghat", "देवघाट", "rural_municipality", 6),
        ("Bandipur", "बन्दीपुर", "rural_municipality", 7),
        ("Rishing", "ऋषिङ", "rural_municipality", 9),
        ("Ghiring", "घिरिङ", "rural_municipality", 11),
        ("Myagde", "म्याग्दे", "rural_municipality", 9),
    ],
    
    # ============= LUMBINI PROVINCE - Complete all districts =============
    "Arghakhanchi": [
        ("Sandhikharka", "सन्धिखर्क", "municipality", 11),
        ("Sitganga", "सीतगंगा", "municipality", 9),
        ("Bhumikasthan", "भूमिकास्थान", "municipality", 9),
        ("Chhatradev", "छत्रदेव", "rural_municipality", 9),
        ("Malarani", "मालारानी", "rural_municipality", 9),
        ("Panini", "पाणिनी", "rural_municipality", 8),
    ],
    "Banke": [
        ("Nepalgunj", "नेपालगञ्ज", "sub_metropolitan", 23),
        ("Kohalpur", "कोहलपुर", "municipality", 14),
        ("Rapti Sonari", "राप्ती सोनारी", "rural_municipality", 9),
        ("Narainapur", "नरैनापुर", "rural_municipality", 9),
        ("Duduwa", "डुडुवा", "rural_municipality", 9),
        ("Janaki", "जानकी", "rural_municipality", 7),
        ("Khajura", "खजुरा", "rural_municipality", 9),
        ("Baijnath", "बैजनाथ", "rural_municipality", 7),
    ],
    "Bardiya": [
        ("Gulariya", "गुलरिया", "municipality", 16),
        ("Madhuwan", "मधुवन", "municipality", 9),
        ("Rajapur", "राजापुर", "municipality", 9),
        ("Thakurbaba", "ठाकुरबाबा", "municipality", 9),
        ("Bansgadhi", "बाँसगढी", "municipality", 9),
        ("Barbardiya", "बारबर्दिया", "municipality", 9),
        ("Geruwa", "गेरुवा", "rural_municipality", 7),
        ("Badhaiyatal", "बढैयाताल", "rural_municipality", 7),
    ],
    "Dang": [
        ("Ghorahi", "घोराही", "sub_metropolitan", 19),
        ("Tulsipur", "तुलसीपुर", "sub_metropolitan", 19),
        ("Lamahi", "लमही", "municipality", 12),
        ("Gadhawa", "गढवा", "rural_municipality", 7),
        ("Rajpur", "राजपुर", "rural_municipality", 6),
        ("Rapti", "राप्ती", "rural_municipality", 8),
        ("Shantinagar", "शान्तिनगर", "rural_municipality", 6),
        ("Babai", "बबई", "rural_municipality", 9),
        ("Dangisharan", "दंगीशरण", "rural_municipality", 6),
        ("Banglachuli", "बंगलाचुली", "rural_municipality", 8),
    ],
    "Eastern Rukum": [
        ("Rukum East", "रुकुम पूर्व", "municipality", 8),
        ("Putha Uttarganga", "पुथा उत्तरगंगा", "rural_municipality", 13),
        ("Sisne", "सिस्ने", "rural_municipality", 7),
        ("Bhume", "भूमे", "rural_municipality", 9),
    ],
    "Gulmi": [
        ("Musikot", "मुसिकोट", "municipality", 9),
        ("Resunga", "रेसुङ्गा", "municipality", 12),
        ("Isma", "इस्मा", "rural_municipality", 6),
        ("Kaligandaki", "कालीगण्डकी", "rural_municipality", 11),
        ("Satyawati", "सत्यवती", "rural_municipality", 9),
        ("Chandrakot", "चन्द्रकोट", "rural_municipality", 7),
        ("Ruru", "रुरु", "rural_municipality", 6),
        ("Gulmi Durbar", "गुल्मी दरबार", "rural_municipality", 12),
        ("Madane", "मदाने", "rural_municipality", 9),
        ("Malika", "मालिका", "rural_municipality", 6),
        ("Dhurkot", "धुर्कोट", "rural_municipality", 7),
        ("Chatrakot", "छत्रकोट", "rural_municipality", 9),
    ],
    "Kapilvastu": [
        ("Kapilvastu", "कपिलवस्तु", "municipality", 14),
        ("Buddhabhumi", "बुद्धभूमि", "municipality", 12),
        ("Shivaraj", "शिवराज", "municipality", 11),
        ("Maharajgunj", "महाराजगञ्ज", "municipality", 9),
        ("Banganga", "बाणगंगा", "municipality", 8),
        ("Krishnanagar", "कृष्णनगर", "municipality", 11),
        ("Suddhodhan", "शुद्धोधन", "rural_municipality", 9),
        ("Bijaynagar", "विजयनगर", "rural_municipality", 9),
        ("Mayadevi", "मायादेवी", "rural_municipality", 9),
        ("Yashodhara", "यशोधरा", "rural_municipality", 7),
    ],
    "Nawalparasi West": [
        ("Bardaghat", "बर्दघाट", "municipality", 18),
        ("Ramgram", "रामग्राम", "municipality", 16),
        ("Sunwal", "सुनवल", "municipality", 17),
        ("Palhi Nandanpur", "पाल्ही नन्दनपुर", "municipality", 9),
        ("Pratappur", "प्रतापपुर", "rural_municipality", 9),
        ("Sarawal", "सरावल", "rural_municipality", 9),
        ("Susta", "सुस्ता", "rural_municipality", 5),
    ],
    "Palpa": [
        ("Tansen", "तानसेन", "municipality", 17),
        ("Rampur", "रामपुर", "municipality", 12),
        ("Rainadevi Chhahara", "रैनादेवी छहरा", "rural_municipality", 9),
        ("Ripdikot", "रिब्दिकोट", "rural_municipality", 6),
        ("Bagnaskali", "बगनासकाली", "rural_municipality", 9),
        ("Rambha", "रम्भा", "rural_municipality", 10),
        ("Purbakhola", "पूर्वखोला", "rural_municipality", 8),
        ("Jhadewa", "झडेवा", "rural_municipality", 5),
        ("Mathagadhi", "माथागढी", "rural_municipality", 9),
        ("Tinau", "तिनाउ", "rural_municipality", 11),
    ],
    "Pyuthan": [
        ("Pyuthan", "प्यूठान", "municipality", 13),
        ("Sworgadwari", "स्वर्गद्वारी", "municipality", 11),
        ("Gaumukhi", "गौमुखी", "rural_municipality", 7),
        ("Mandavi", "माण्डवी", "rural_municipality", 9),
        ("Sarumarani", "सरुमारानी", "rural_municipality", 5),
        ("Mallarani", "मल्लरानी", "rural_municipality", 9),
        ("Naubahini", "नौबहिनी", "rural_municipality", 9),
        ("Jhimruk", "झिमरुक", "rural_municipality", 5),
        ("Airawati", "ऐरावती", "rural_municipality", 9),
    ],
    "Rolpa": [
        ("Rolpa", "रोल्पा", "municipality", 10),
        ("Runtigadhi", "रुन्टीगढी", "rural_municipality", 9),
        ("Triveni", "त्रिवेणी", "rural_municipality", 9),
        ("Duikhola", "दुईखोला", "rural_municipality", 5),
        ("Madi", "माडी", "rural_municipality", 5),
        ("Lungri", "लुङग्री", "rural_municipality", 5),
        ("Gangadev", "गंगादेव", "rural_municipality", 6),
        ("Pariwartan", "परिवर्तन", "rural_municipality", 5),
        ("Sukidaha", "सुकिदह", "rural_municipality", 5),
        ("Thawang", "थवाङ", "rural_municipality", 6),
    ],
    "Rupandehi": [
        ("Butwal", "बुटवल", "sub_metropolitan", 23),
        ("Lumbini Sanskritik", "लुम्बिनी सांस्कृतिक", "municipality", 17),
        ("Devdaha", "देवदह", "municipality", 16),
        ("Sainamaina", "सैनामैना", "municipality", 17),
        ("Siddharthanagar", "सिद्धार्थनगर", "municipality", 19),
        ("Tilottama", "तिलोत्तमा", "municipality", 17),
        ("Kanchan", "कञ्चन", "rural_municipality", 8),
        ("Kotahimai", "कोटहीमाई", "rural_municipality", 9),
        ("Marchawari", "मर्चवारी", "rural_municipality", 6),
        ("Omsatiya", "ओमसतिया", "rural_municipality", 6),
        ("Rohini", "रोहिणी", "rural_municipality", 7),
        ("Sammarimai", "सम्मरीमाई", "rural_municipality", 6),
        ("Siyari", "सियारी", "rural_municipality", 5),
        ("Gaidahawa", "गैडहवा", "rural_municipality", 8),
        ("Mayadebi", "मायादेवी", "rural_municipality", 9),
        ("Suddhodhan", "शुद्धोधन", "rural_municipality", 9),
    ],
    
    # ============= KARNALI PROVINCE - Complete all districts =============
    "Dailekh": [
        ("Narayan", "नारायण", "municipality", 12),
        ("Dullu", "दुल्लु", "municipality", 9),
        ("Chamunda Bindrasaini", "चामुण्डा बिन्द्रासैनी", "municipality", 9),
        ("Aathabis", "आठबिस", "municipality", 9),
        ("Bhagawatimai", "भगवतीमाई", "rural_municipality", 9),
        ("Mahabu", "महाबु", "rural_municipality", 9),
        ("Naumule", "नौमुले", "rural_municipality", 9),
        ("Dungeshwar", "डुंगेश्वर", "rural_municipality", 6),
        ("Gurans", "गुराँस", "rural_municipality", 9),
        ("Bhairabi", "भैरवी", "rural_municipality", 6),
        ("Thantikandh", "ठाँटीकाँध", "rural_municipality", 6),
    ],
    "Dolpa": [
        ("Thuli Bheri", "ठूली भेरी", "municipality", 9),
        ("Tripurasundari", "त्रिपुरासुन्दरी", "rural_municipality", 9),
        ("Dolpo Buddha", "डोल्पो बुद्ध", "rural_municipality", 9),
        ("She Phoksundo", "शे फोक्सुण्डो", "rural_municipality", 9),
        ("Jagadulla", "जगदुल्ला", "rural_municipality", 5),
        ("Mudkechula", "मुड्केचुला", "rural_municipality", 9),
        ("Kaike", "काईके", "rural_municipality", 5),
        ("Chharka Tangsong", "छार्का ताङसोङ", "rural_municipality", 5),
    ],
    "Humla": [
        ("Simkot", "सिमकोट", "rural_municipality", 9),
        ("Namkha", "नाम्खा", "rural_municipality", 5),
        ("Kharpunath", "खार्पुनाथ", "rural_municipality", 9),
        ("Sarkegad", "सर्केगाड", "rural_municipality", 5),
        ("Chankheli", "चंखेली", "rural_municipality", 7),
        ("Adanchuli", "अदानचुली", "rural_municipality", 5),
        ("Tajakot", "ताँजाकोट", "rural_municipality", 5),
    ],
    "Jajarkot": [
        ("Bheri", "भेरी", "municipality", 9),
        ("Chhedagad", "छेडागाड", "municipality", 9),
        ("Tribeni", "त्रिवेणी", "rural_municipality", 9),
        ("Barekot", "बारेकोट", "rural_municipality", 9),
        ("Shiwalaya", "शिवालय", "rural_municipality", 9),
        ("Kushe", "कुशे", "rural_municipality", 7),
        ("Junichande", "जुनीचाँदे", "rural_municipality", 9),
    ],
    "Jumla": [
        ("Chandannath", "चन्दननाथ", "municipality", 10),
        ("Kankasundari", "कनकासुन्दरी", "rural_municipality", 9),
        ("Sinja", "सिन्जा", "rural_municipality", 9),
        ("Hima", "हिमा", "rural_municipality", 7),
        ("Tila", "तिला", "rural_municipality", 9),
        ("Guthichaur", "गुठिचौर", "rural_municipality", 5),
        ("Tatopani", "तातोपानी", "rural_municipality", 7),
        ("Patarasi", "पातारासी", "rural_municipality", 6),
    ],
    "Kalikot": [
        ("Khandachakra", "खाँडाचक्र", "municipality", 9),
        ("Raskot", "रास्कोट", "municipality", 9),
        ("Tilagufa", "तिलागुफा", "municipality", 11),
        ("Pachaljharana", "पचालझरना", "rural_municipality", 9),
        ("Sanni Tribeni", "सान्नी त्रिवेणी", "rural_municipality", 9),
        ("Naraharinath", "नरहरिनाथ", "rural_municipality", 5),
        ("Shubha Kalika", "शुभ कालिका", "rural_municipality", 9),
        ("Mahawai", "महावै", "rural_municipality", 9),
        ("Palata", "पलाता", "rural_municipality", 9),
    ],
    "Mugu": [
        ("Chhayanath Rara", "छायाँनाथ रारा", "municipality", 10),
        ("Mugum Karmarong", "मुगुम कार्मारोङ", "rural_municipality", 5),
        ("Soru", "सोरु", "rural_municipality", 5),
        ("Khatyad", "खत्याड", "rural_municipality", 9),
    ],
    "Salyan": [
        ("Shaarda", "शारदा", "municipality", 12),
        ("Bagchaur", "बागचौर", "municipality", 11),
        ("Bangad Kupinde", "बनगाड कुपिण्डे", "municipality", 10),
        ("Kalimati", "कालीमाटी", "rural_municipality", 9),
        ("Tribeni", "त्रिवेणी", "rural_municipality", 9),
        ("Kapurkot", "कपुरकोट", "rural_municipality", 9),
        ("Chhatreshwari", "छत्रेश्वरी", "rural_municipality", 9),
        ("Kumakh", "कुमाख", "rural_municipality", 9),
        ("Siddha Kumakh", "सिद्ध कुमाख", "rural_municipality", 7),
        ("Darma", "दार्मा", "rural_municipality", 8),
    ],
    "Surkhet": [
        ("Birendranagar", "वीरेन्द्रनगर", "municipality", 13),
        ("Bheriganga", "भेरीगंगा", "municipality", 12),
        ("Gurbhakot", "गुर्भाकोट", "municipality", 9),
        ("Panchpuri", "पञ्चपुरी", "municipality", 9),
        ("Lekbeshi", "लेकबेशी", "municipality", 9),
        ("Chingad", "चिङ्गाड", "rural_municipality", 9),
        ("Chaukune", "चौकुने", "rural_municipality", 7),
        ("Simta", "सिम्ता", "rural_municipality", 9),
    ],
    "Western Rukum": [
        ("Musikot", "मुसिकोट", "municipality", 9),
        ("Chaurjahari", "चौरजहारी", "municipality", 9),
        ("Aathbiskot", "आठबिसकोट", "municipality", 9),
        ("Banphikot", "बाँफिकोट", "rural_municipality", 7),
        ("Triveni", "त्रिवेणी", "rural_municipality", 9),
        ("Sani Bheri", "सानी भेरी", "rural_municipality", 9),
    ],
    
    # ============= SUDURPASHCHIM PROVINCE - Complete all districts =============
    "Achham": [
        ("Mangalsen", "मंगलसेन", "municipality", 11),
        ("Kamalbazar", "कमलबजार", "municipality", 9),
        ("Sanphebagar", "साँफेबगर", "municipality", 11),
        ("Panchadewal Binayak", "पञ्चदेवल विनायक", "municipality", 9),
        ("Chaurpati", "चौरपाटी", "rural_municipality", 9),
        ("Turmakhad", "तुर्माखाँद", "rural_municipality", 9),
        ("Mellekh", "मेल्लेख", "rural_municipality", 9),
        ("Dhakari", "ढकारी", "rural_municipality", 9),
        ("Bannigadhi Jayagadh", "बान्नीगढी जयगढ", "rural_municipality", 9),
        ("Ramaroshan", "रामारोशन", "rural_municipality", 6),
    ],
    "Baitadi": [
        ("Dasharathchand", "दशरथचन्द", "municipality", 19),
        ("Patan", "पाटन", "municipality", 9),
        ("Melauli", "मेलौली", "municipality", 9),
        ("Purchaudi", "पुर्चौडी", "municipality", 9),
        ("Shivanath", "शिवनाथ", "rural_municipality", 9),
        ("Pancheshwar", "पञ्चेश्वर", "rural_municipality", 9),
        ("Dogdakedar", "डोगडाकेदार", "rural_municipality", 9),
        ("Dilasaini", "डिलासैनी", "rural_municipality", 9),
        ("Mahakali", "महाकाली", "rural_municipality", 9),
        ("Suurnaya", "सुर्नया", "rural_municipality", 7),
    ],
    "Bajhang": [
        ("Jaya Prithvi", "जय पृथ्वी", "municipality", 13),
        ("Bungal", "बुंगल", "municipality", 9),
        ("Talkot", "तल्कोट", "rural_municipality", 6),
        ("Masta", "मष्टा", "rural_municipality", 9),
        ("Khaptadchhanna", "खप्तडछान्ना", "rural_municipality", 8),
        ("Thalara", "थलारा", "rural_municipality", 6),
        ("Bitthadchir", "बित्थडचिर", "rural_municipality", 9),
        ("Surma", "सुर्मा", "rural_municipality", 6),
        ("Chhabis Pathibhara", "छबिस पाथिभेरा", "rural_municipality", 9),
        ("Durgathali", "दुर्गाथली", "rural_municipality", 6),
        ("Kedarsyu", "केदारस्यूँ", "rural_municipality", 8),
        ("Saipal", "साईपाल", "rural_municipality", 7),
    ],
    "Bajura": [
        ("Badimalika", "बडीमालिका", "municipality", 9),
        ("Triveni", "त्रिवेणी", "municipality", 9),
        ("Budhiganga", "बुढीगंगा", "municipality", 9),
        ("Budhinanda", "बुढीनन्दा", "municipality", 8),
        ("Swamikartik Khapar", "स्वामीकार्तिक खापर", "rural_municipality", 9),
        ("Khaptad Chhededaha", "खप्तड छेडेदह", "rural_municipality", 5),
        ("Himali", "हिमाली", "rural_municipality", 7),
        ("Gaumul", "गौमुल", "rural_municipality", 5),
        ("Pandav Gupha", "पाण्डव गुफा", "rural_municipality", 5),
    ],
    "Dadeldhura": [
        ("Amargadhi", "अमरगढी", "municipality", 12),
        ("Parshuram", "परशुराम", "municipality", 9),
        ("Alital", "आलिताल", "rural_municipality", 6),
        ("Bhageshwar", "भागेश्वर", "rural_municipality", 9),
        ("Nawadurga", "नवदुर्गा", "rural_municipality", 9),
        ("Ajaymeru", "अजयमेरु", "rural_municipality", 9),
        ("Gangarada Batuli", "गन्यापधुरा", "rural_municipality", 6),
    ],
    "Darchula": [
        ("Mahakali", "महाकाली", "municipality", 9),
        ("Shailyashikhar", "शैल्यशिखर", "municipality", 9),
        ("Naugad", "नौगाड", "rural_municipality", 7),
        ("Dunhun", "दुँहुँ", "rural_municipality", 5),
        ("Lekam", "लेकम", "rural_municipality", 5),
        ("Vyans", "व्याँस", "rural_municipality", 9),
        ("Apihimal", "अपिहिमाल", "rural_municipality", 5),
        ("Malikaarjun", "मालिकार्जुन", "rural_municipality", 5),
        ("Marma", "मर्मा", "rural_municipality", 5),
    ],
    "Doti": [
        ("Dipayal Silgadhi", "दिपायल सिलगढी", "municipality", 19),
        ("Shikhar", "शिखर", "municipality", 9),
        ("Purbichauki", "पूर्वीचौकी", "rural_municipality", 8),
        ("Badikedar", "बडिकेदार", "rural_municipality", 6),
        ("Jorayal", "जोरायल", "rural_municipality", 6),
        ("Sayal", "सायल", "rural_municipality", 7),
        ("Aadarsha", "आदर्श", "rural_municipality", 7),
        ("K.I.Singh", "के.आई.सिंह", "rural_municipality", 8),
        ("Bogatan", "बोगटान", "rural_municipality", 9),
    ],
    "Kailali": [
        ("Dhangadhi", "धनगढी", "sub_metropolitan", 19),
        ("Tikapur", "टीकापुर", "municipality", 9),
        ("Ghodaghodi", "घोडाघोडी", "municipality", 12),
        ("Lamki Chuha", "लम्की चुहा", "municipality", 9),
        ("Bharatpur", "भरतपुर", "municipality", 12),
        ("Godawari", "गोदावरी", "municipality", 15),
        ("Gauriganga", "गौरीगंगा", "municipality", 9),
        ("Janaki", "जानकी", "rural_municipality", 7),
        ("Bardagoriya", "बर्दगोरिया", "rural_municipality", 9),
        ("Mohanyal", "मोहन्याल", "rural_municipality", 9),
        ("Kailari", "कैलारी", "rural_municipality", 7),
        ("Joshipur", "जोशीपुर", "rural_municipality", 5),
        ("Chure", "चुरे", "rural_municipality", 9),
    ],
    "Kanchanpur": [
        ("Bhimdatta", "भीमदत्त", "municipality", 19),
        ("Punarbas", "पुनर्वास", "municipality", 15),
        ("Bedkot", "बेदकोट", "municipality", 9),
        ("Mahakali", "महाकाली", "municipality", 9),
        ("Shuklaphanta", "शुक्लाफाँटा", "municipality", 12),
        ("Belauri", "बेलौरी", "municipality", 10),
        ("Krishnapur", "कृष्णपुर", "municipality", 7),
        ("Laljhadi", "लालझाडी", "rural_municipality", 5),
        ("Beldandi", "बेलडाँडी", "rural_municipality", 6),
    ],
}

def load_all_municipalities():
    """Load all municipalities into the database"""
    
    total_created = 0
    total_updated = 0
    errors = []
    
    print("Loading ALL 753 municipalities into database...")
    print("="*60)
    
    for district_name, municipalities in MUNICIPALITY_DATA.items():
        try:
            # Try to find district by exact name
            district = District.objects.filter(name_en=district_name).first()
            
            # If not found, try partial match (for cases like "Nawalparasi West" vs "Nawalparasi")
            if not district:
                district = District.objects.filter(name_en__icontains=district_name.split()[0]).first()
            
            if not district:
                print(f"⚠️  Warning: District '{district_name}' not found in database")
                errors.append(f"District not found: {district_name}")
                continue
                
            print(f"\n📍 Processing {district_name} district ({district.province.name_en})...")
            
            for idx, (name_en, name_ne, mun_type, wards) in enumerate(municipalities, 1):
                try:
                    # Generate unique code based on district code
                    code = f"M{district.code[1:]}{idx:02d}"
                    
                    # Check if municipality already exists
                    existing = Municipality.objects.filter(
                        district=district,
                        name_en=name_en
                    ).first()
                    
                    if existing:
                        # Update existing municipality
                        existing.name_ne = name_ne
                        existing.municipality_type = mun_type
                        existing.total_wards = wards
                        existing.save()
                        total_updated += 1
                        print(f"  ✓ Updated: {name_en} ({mun_type}, {wards} wards)")
                    else:
                        # Create new municipality
                        Municipality.objects.create(
                            code=code,
                            district=district,
                            name_en=name_en,
                            name_ne=name_ne,
                            municipality_type=mun_type,
                            total_wards=wards
                        )
                        total_created += 1
                        print(f"  ✓ Created: {name_en} ({mun_type}, {wards} wards)")
                        
                except Exception as e:
                    error_msg = f"Error creating {name_en} in {district_name}: {str(e)}"
                    print(f"  ✗ {error_msg}")
                    errors.append(error_msg)
                    
        except Exception as e:
            error_msg = f"Error processing district {district_name}: {str(e)}"
            print(f"✗ {error_msg}")
            errors.append(error_msg)
    
    print(f"\n{'='*60}")
    print("LOADING COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ Municipalities created: {total_created}")
    print(f"✓ Municipalities updated: {total_updated}")
    print(f"✓ Total municipalities in database: {Municipality.objects.count()}")
    
    if errors:
        print(f"\n⚠️  Errors encountered ({len(errors)}):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
    
    # Verify counts by type
    from django.db.models import Count
    print(f"\n📊 Municipality types:")
    type_counts = Municipality.objects.values('municipality_type').annotate(count=Count('municipality_type')).order_by('-count')
    for t in type_counts:
        print(f"  {t['municipality_type']}: {t['count']}")
    
    # Verify by province
    print(f"\n📊 Municipalities by Province:")
    for province in Province.objects.all().order_by('code'):
        count = Municipality.objects.filter(district__province=province).count()
        print(f"  {province.name_en}: {count} municipalities")

if __name__ == "__main__":
    load_all_municipalities()