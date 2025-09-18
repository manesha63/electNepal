from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from candidates.models import Candidate, CandidateEvent
from locations.models import Province, District, Municipality
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Create test candidate profiles with complete information'

    def handle(self, *args, **options):
        # Sample candidate data
        candidates_data = [
            {
                'username': 'sunita_poudel',
                'full_name': 'Sunita Poudel',
                'position_level': 'federal',
                'bio': """Sunita Poudel is a renowned women's rights activist and social entrepreneur with 20 years of experience in advocacy and policy reform. She has championed causes related to gender equality, education, and economic empowerment.

Her vision is to create a Nepal where women have equal opportunities in all spheres of life, where quality education is accessible to all, and where sustainable development drives our nation's progress.""",
                'education': """• PhD in Gender Studies - Kathmandu University (2015)
• Masters in Social Work - Delhi University, India (2005)
• Bachelor in Sociology - Tribhuvan University (2001)
• Certificate in Women's Leadership - Oxford University (2019)""",
                'experience': """• Founder & CEO - Women Empowerment Foundation (2010-Present)
• Senior Advisor - UN Women Nepal (2015-2020)
• Director - National Women's Commission (2008-2010)
• Research Fellow - Centre for Women's Studies (2005-2008)

Achievements:
- Drafted legislation for 33% women's reservation
- Established 200+ women's cooperatives
- Trained 5000+ women in entrepreneurship
- Published 10+ research papers on gender equality""",
                'manifesto': """BUILDING AN INCLUSIVE NEPAL:

1. WOMEN'S EMPOWERMENT
- 50% women representation in all government bodies
- Equal pay legislation and enforcement
- Safe spaces and support systems for women
- Zero tolerance for gender-based violence

2. QUALITY EDUCATION
- Free education including university level
- STEM programs for girls
- Adult literacy campaigns
- Digital education infrastructure

3. SUSTAINABLE DEVELOPMENT
- Green energy initiatives
- Climate change adaptation programs
- Sustainable agriculture practices
- Eco-tourism development

4. SOCIAL JUSTICE
- Equal rights for all marginalized communities
- Disability-inclusive infrastructure
- Senior citizen support programs
- Mental health awareness and support""",
                'phone': '+977-9851234567',
                'website': 'https://sunitapoudel.org.np',
                'facebook': 'https://facebook.com/sunitapoudel',
                'donation': 'https://support.sunitapoudel.org.np'
            },
            {
                'username': 'ram_thapa',
                'full_name': 'Ram Bahadur Thapa',
                'position_level': 'local_executive',
                'bio': """Ram Bahadur Thapa is a grassroots leader with deep roots in rural development and agriculture. Having grown up in a farming family, he understands the challenges faced by rural communities and is committed to agricultural modernization and rural prosperity.

His vision is to transform rural municipalities into self-sufficient, prosperous communities through modern agriculture, local entrepreneurship, and sustainable development practices.""",
                'education': """• Masters in Agricultural Economics - Agriculture and Forestry University (2012)
• Bachelor in Agriculture - Institute of Agriculture and Animal Science (2008)
• Diploma in Cooperative Management - Nepal Cooperative Training Centre (2015)
• Certificate in Organic Farming - Israel (2018)""",
                'experience': """• Chairman - District Agriculture Cooperative (2018-Present)
• Agriculture Officer - Ministry of Agriculture (2012-2018)
• Project Coordinator - Rural Development Fund (2008-2012)
• Youth Coordinator - Young Farmers Association (2005-2008)

Key Initiatives:
- Introduced modern farming techniques to 100+ villages
- Established 50+ agriculture cooperatives
- Created market linkages for 2000+ farmers
- Implemented irrigation projects in 30 communities""",
                'manifesto': """PROSPERITY THROUGH AGRICULTURE:

1. AGRICULTURAL MODERNIZATION
- Subsidized modern farming equipment
- Free seeds and fertilizers for small farmers
- Agriculture insurance programs
- Cold storage facilities in every ward

2. RURAL INFRASTRUCTURE
- All-weather roads to all villages
- Irrigation systems for all farmland
- Rural electrification programs
- Internet connectivity for digital services

3. LOCAL ECONOMY
- Farmer's markets in every municipality
- Agro-processing industries
- Cooperative strengthening programs
- Youth entrepreneurship funds

4. ENVIRONMENTAL CONSERVATION
- Forest conservation programs
- Watershed management
- Organic farming promotion
- Renewable energy projects""",
                'phone': '+977-9861234567',
                'website': 'https://ramthapa.com.np',
                'facebook': 'https://facebook.com/rambahadurthapa',
                'donation': 'https://donate.ramthapa.com.np'
            },
            {
                'username': 'priya_sharma',
                'full_name': 'Priya Sharma',
                'position_level': 'ward',
                'bio': """Priya Sharma is a young dynamic leader passionate about community development and youth engagement. As a social worker and community organizer, she has worked tirelessly to improve living conditions in urban settlements.

Her vision is to create model wards with excellent public services, green spaces, and opportunities for all residents, especially youth and marginalized communities.""",
                'education': """• Masters in Urban Planning - IOE, Tribhuvan University (2018)
• Bachelor in Civil Engineering - Pulchowk Campus (2015)
• Certificate in Community Development - AIT, Thailand (2020)
• Training in Disaster Management - Japan (2019)""",
                'experience': """• Ward Secretary - Ward 10, Kathmandu (2020-Present)
• Urban Planner - Kathmandu Metropolitan City (2018-2020)
• Junior Engineer - Department of Roads (2015-2018)
• Volunteer - Nepal Red Cross Society (2013-2015)

Notable Projects:
- Implemented waste segregation in 500+ households
- Created 5 community parks and green spaces
- Established youth skill development center
- Organized 20+ community health camps""",
                'manifesto': """TRANSFORMING OUR WARD:

1. URBAN SERVICES
- 24/7 water supply to all households
- Door-to-door waste collection
- Street lighting in all areas
- Public WiFi zones

2. COMMUNITY SPACES
- Parks and playgrounds in every tole
- Community centers for events
- Sports facilities for youth
- Senior citizen recreation areas

3. HEALTH & SAFETY
- Ward health clinic with emergency services
- CCTV surveillance for security
- Disaster preparedness programs
- COVID-19 recovery support

4. YOUTH DEVELOPMENT
- Skill training programs
- Sports tournaments and cultural events
- Startup incubation center
- Scholarship programs for students""",
                'phone': '+977-9841567890',
                'website': 'https://priyasharma.org',
                'facebook': 'https://facebook.com/priyasharmaward10',
                'donation': 'https://support.priyasharma.org'
            }
        ]

        for data in candidates_data:
            # Create user if doesn't exist
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': f"{data['username']}@example.com",
                    'first_name': data['full_name'].split()[0],
                    'last_name': ' '.join(data['full_name'].split()[1:])
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()

            # Get random location
            province = Province.objects.order_by('?').first()
            district = District.objects.filter(province=province).order_by('?').first()
            municipality = Municipality.objects.filter(district=district).order_by('?').first()

            # Ward number for ward-level candidates
            ward_number = random.randint(1, 10) if data['position_level'] == 'ward' else None

            # Create or update candidate
            candidate, created = Candidate.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': data['full_name'],
                    'position_level': data['position_level'],
                    'bio_en': data['bio'],
                    'education_en': data['education'],
                    'experience_en': data['experience'],
                    'manifesto_en': data['manifesto'],
                    'phone_number': data['phone'],
                    'website': data['website'],
                    'facebook_url': data['facebook'],
                    'donation_link': data['donation'],
                    'province': province,
                    'district': district,
                    'municipality': municipality if data['position_level'] in ['ward', 'local_executive'] else None,
                    'ward_number': ward_number
                }
            )

            # Create some events for each candidate
            events = [
                {
                    'title': f"Meet {data['full_name'].split()[0]} - Community Dialogue",
                    'description': "Open forum to discuss local issues and solutions",
                    'days': 7,
                    'location': f"Community Center, {district.name_en}"
                },
                {
                    'title': "Campaign Rally",
                    'description': "Join us for our main campaign event",
                    'days': 14,
                    'location': f"City Hall, {municipality.name_en if municipality else district.name_en}"
                },
                {
                    'title': "Q&A Session with Voters",
                    'description': "Direct interaction with voters - ask your questions",
                    'days': 21,
                    'location': "Online via Zoom"
                }
            ]

            for event_data in events:
                CandidateEvent.objects.create(
                    candidate=candidate,
                    title_en=event_data['title'],
                    description_en=event_data['description'],
                    event_date=timezone.now() + timedelta(days=event_data['days']),
                    location_en=event_data['location']
                )

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} candidate: {candidate.full_name} ({candidate.get_position_level_display()})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Successfully created/updated test candidates with complete profiles"))