"""
Management command to verify and fix translation flag inconsistencies.

Translation Flag Rules:
1. is_mt_*_ne should be True ONLY when:
   - The Nepali field exists
   - The English field exists
   - The Nepali content is DIFFERENT from English (actual translation occurred)

2. is_mt_*_ne should be False when:
   - No Nepali translation exists
   - Nepali equals English (copy, not translation)
   - Nepali is manually translated (user-provided)

Usage:
    # Dry run (show inconsistencies without fixing)
    python manage.py verify_translation_flags

    # Fix all inconsistencies
    python manage.py verify_translation_flags --fix

    # Check specific model
    python manage.py verify_translation_flags --model candidate
    python manage.py verify_translation_flags --model event
"""

from django.core.management.base import BaseCommand
from candidates.models import Candidate, CandidateEvent


class Command(BaseCommand):
    help = 'Verify and fix translation flag (is_mt_*) inconsistencies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually fix inconsistencies (default is dry-run mode)',
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['candidate', 'event', 'both'],
            default='both',
            help='Which model to check (default: both)',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        model_choice = options['model']

        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('TRANSLATION FLAG VERIFICATION'))
        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write('')

        total_checked = 0
        total_inconsistencies = 0
        total_fixed = 0

        # Check Candidates
        if model_choice in ['candidate', 'both']:
            checked, inconsistencies, fixed = self.verify_candidates(fix_mode)
            total_checked += checked
            total_inconsistencies += inconsistencies
            total_fixed += fixed

        # Check CandidateEvents
        if model_choice in ['event', 'both']:
            checked, inconsistencies, fixed = self.verify_events(fix_mode)
            total_checked += checked
            total_inconsistencies += inconsistencies
            total_fixed += fixed

        # Summary
        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('SUMMARY'))
        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(f'Total Records Checked: {total_checked}')
        self.stdout.write(f'Total Inconsistencies Found: {total_inconsistencies}')

        if fix_mode:
            self.stdout.write(self.style.SUCCESS(f'Total Inconsistencies Fixed: {total_fixed}'))
        else:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes made'))
            self.stdout.write(self.style.NOTICE('\nTo fix these inconsistencies, run:'))
            self.stdout.write(self.style.NOTICE('  python manage.py verify_translation_flags --fix'))

        self.stdout.write('')

    def verify_candidates(self, fix_mode):
        """Verify Candidate translation flags"""
        self.stdout.write(self.style.WARNING('\nChecking Candidates...'))

        candidates = Candidate.objects.all()
        checked = 0
        inconsistencies = 0
        fixed = 0

        fields = ['bio', 'education', 'experience', 'achievements', 'manifesto']

        for candidate in candidates:
            checked += 1
            for field in fields:
                en_val = (getattr(candidate, f'{field}_en', '') or '').strip()
                ne_val = (getattr(candidate, f'{field}_ne', '') or '').strip()
                is_mt = getattr(candidate, f'is_mt_{field}_ne', False)
                mt_flag_field = f'is_mt_{field}_ne'

                # Rule 1: Empty Nepali but MT flag is True
                if not ne_val and is_mt:
                    inconsistencies += 1
                    self.stdout.write(
                        f'  ✗ Candidate {candidate.id} ({candidate.full_name}): '
                        f'{field} - Empty Nepali but is_mt=True'
                    )
                    if fix_mode:
                        setattr(candidate, mt_flag_field, False)
                        fixed += 1

                # Rule 2: Nepali equals English but MT flag is True
                # (This means translation failed and English was copied as fallback)
                elif ne_val and en_val and ne_val == en_val and is_mt:
                    inconsistencies += 1
                    self.stdout.write(
                        f'  ✗ Candidate {candidate.id} ({candidate.full_name}): '
                        f'{field} - Nepali equals English but is_mt=True (copy, not translation)'
                    )
                    if fix_mode:
                        setattr(candidate, mt_flag_field, False)
                        fixed += 1

            # Save if we made changes
            if fix_mode and inconsistencies > 0:
                candidate.save(skip_validation=True)  # Skip validation to avoid unnecessary checks

        self.stdout.write(f'  Checked: {checked} candidates')
        return checked, inconsistencies, fixed

    def verify_events(self, fix_mode):
        """Verify CandidateEvent translation flags"""
        self.stdout.write(self.style.WARNING('\nChecking CandidateEvents...'))

        events = CandidateEvent.objects.all()
        checked = 0
        inconsistencies = 0
        fixed = 0

        fields = ['title', 'description', 'location']

        for event in events:
            checked += 1
            for field in fields:
                en_val = (getattr(event, f'{field}_en', '') or '').strip()
                ne_val = (getattr(event, f'{field}_ne', '') or '').strip()
                is_mt = getattr(event, f'is_mt_{field}_ne', False)
                mt_flag_field = f'is_mt_{field}_ne'

                # Rule 1: Empty Nepali but MT flag is True
                if not ne_val and is_mt:
                    inconsistencies += 1
                    self.stdout.write(
                        f'  ✗ Event {event.id} ({event.candidate.full_name}): '
                        f'{field} - Empty Nepali but is_mt=True'
                    )
                    if fix_mode:
                        setattr(event, mt_flag_field, False)
                        fixed += 1

                # Rule 2: Nepali equals English but MT flag is True
                elif ne_val and en_val and ne_val == en_val and is_mt:
                    inconsistencies += 1
                    self.stdout.write(
                        f'  ✗ Event {event.id} ({event.candidate.full_name}): '
                        f'{field} - Nepali equals English but is_mt=True (copy, not translation)'
                    )
                    if fix_mode:
                        setattr(event, mt_flag_field, False)
                        fixed += 1

            # Save if we made changes
            if fix_mode and inconsistencies > 0:
                # Use Model.save() to skip AutoTranslationMixin
                from django.db import models
                models.Model.save(event)

        self.stdout.write(f'  Checked: {checked} events')
        return checked, inconsistencies, fixed
