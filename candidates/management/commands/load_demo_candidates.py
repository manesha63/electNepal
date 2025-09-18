import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from candidates.models import Candidate, CandidatePost, CandidateEvent
from locations.models import Province, District, Municipality
import random


class Command(BaseCommand):
    help = 'Load demo candidate data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/demo_candidates.json',
            help='Path to the JSON file containing candidate data'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        candidates_created = 0
        candidates_updated = 0

        for candidate_data in data.get('candidates', []):
            try:
                # Create or get user
                user, user_created = User.objects.get_or_create(
                    username=candidate_data['username'],
                    defaults={
                        'email': candidate_data['email'],
                        'first_name': candidate_data['full_name'].split()[0],
                        'last_name': ' '.join(candidate_data['full_name'].split()[1:])
                    }
                )
                
                if user_created:
                    user.set_password(candidate_data['password'])
                    user.save()

                # Get location objects
                province = Province.objects.filter(name_en=candidate_data['province']).first()
                district = District.objects.filter(name_en=candidate_data['district']).first()
                municipality = Municipality.objects.filter(name_en=candidate_data['municipality']).first() if candidate_data.get('municipality') else None

                if not province or not district:
                    self.stdout.write(self.style.WARNING(f'Location not found for {candidate_data["full_name"]}'))
                    continue

                # Create or update candidate
                candidate, created = Candidate.objects.update_or_create(
                    user=user,
                    defaults={
                        'full_name': candidate_data['full_name'],
                        'date_of_birth': candidate_data.get('date_of_birth'),
                        'phone_number': candidate_data.get('phone_number', ''),
                        'bio_en': candidate_data.get('bio_en', ''),
                        'bio_ne': candidate_data.get('bio_ne', ''),
                        'education_en': candidate_data.get('education_en', ''),
                        'education_ne': candidate_data.get('education_ne', ''),
                        'experience_en': candidate_data.get('experience_en', ''),
                        'experience_ne': candidate_data.get('experience_ne', ''),
                        'manifesto_en': candidate_data.get('manifesto_en', ''),
                        'manifesto_ne': candidate_data.get('manifesto_ne', ''),
                        'position_level': candidate_data['position_level'],
                        'province': province,
                        'district': district,
                        'municipality': municipality,
                        'ward_number': candidate_data.get('ward_number'),
                        'website': candidate_data.get('website', ''),
                        'facebook_url': candidate_data.get('facebook_url', ''),
                        'donation_link': candidate_data.get('donation_link', ''),
                    }
                )

                if created:
                    candidates_created += 1
                    
                    # Add some demo posts for all candidates
                    CandidatePost.objects.create(
                        candidate=candidate,
                        title="My Vision for Our Community",
                        content=f"As your candidate, I am committed to bringing positive change to our community. {candidate.manifesto_en}",
                        is_published=True
                    )

                    CandidatePost.objects.create(
                        candidate=candidate,
                        title="Campaign Launch Event Success",
                        content="Thank you to everyone who joined our campaign launch. Your support means everything. Together, we will build a better future!",
                        is_published=True
                    )

                    # Add demo events
                    from datetime import timedelta
                    future_date = timezone.now() + timedelta(days=random.randint(5, 30))

                    CandidateEvent.objects.create(
                        candidate=candidate,
                        title="Community Town Hall Meeting",
                        description="Join us for an open discussion about local issues and solutions. Everyone is welcome!",
                        event_date=future_date,
                        location=f"{municipality.name_en if municipality else district.name_en} Community Center",
                        is_published=True
                    )

                    future_date2 = timezone.now() + timedelta(days=random.randint(35, 60))
                    CandidateEvent.objects.create(
                        candidate=candidate,
                        title="Youth Engagement Program",
                        description="Special session focused on youth employment and education opportunities.",
                        event_date=future_date2,
                        location=f"{district.name_en} Youth Center",
                        is_published=True
                    )
                else:
                    candidates_updated += 1

                self.stdout.write(self.style.SUCCESS(f'Processed: {candidate.full_name}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {candidate_data.get("full_name", "unknown")}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {candidates_created} candidates created, {candidates_updated} candidates updated'
        ))