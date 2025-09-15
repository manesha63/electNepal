"""
Management command to translate candidate content fields
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from candidates.models import Candidate
from core.translation import translation_service


class Command(BaseCommand):
    help = 'Translate missing Nepali fields for all candidates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-translation even if target fields are not empty',
        )
        parser.add_argument(
            '--candidate-id',
            type=int,
            help='Translate only a specific candidate by ID',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of candidates to process in each batch (default: 10)',
        )

    def handle(self, *args, **options):
        force = options['force']
        candidate_id = options.get('candidate_id')
        batch_size = options['batch_size']

        # Get candidates to translate
        if candidate_id:
            candidates = Candidate.objects.filter(id=candidate_id)
            if not candidates.exists():
                self.stdout.write(
                    self.style.ERROR(f'Candidate with ID {candidate_id} not found')
                )
                return
        else:
            candidates = Candidate.objects.all()

        total_count = candidates.count()
        translated_count = 0
        error_count = 0

        self.stdout.write(
            self.style.SUCCESS(f'Starting translation for {total_count} candidates...')
        )

        # Process in batches for better performance
        for i in range(0, total_count, batch_size):
            batch = candidates[i:i+batch_size]

            with transaction.atomic():
                for candidate in batch:
                    try:
                        # Check if translation is needed
                        needs_translation = False

                        # Check each field pair
                        field_pairs = [
                            ('bio_en', 'bio_ne', 'is_mt_bio_ne'),
                            ('education_en', 'education_ne', 'is_mt_education_ne'),
                            ('experience_en', 'experience_ne', 'is_mt_experience_ne'),
                            ('manifesto_en', 'manifesto_ne', 'is_mt_manifesto_ne'),
                        ]

                        for source_field, target_field, mt_flag_field in field_pairs:
                            source_text = getattr(candidate, source_field, '')
                            target_text = getattr(candidate, target_field, '')

                            if source_text and (not target_text or force):
                                needs_translation = True
                                break

                        if needs_translation:
                            # Perform translation
                            updated = translation_service.translate_candidate_fields(
                                candidate, force=force
                            )

                            if updated:
                                candidate.save()
                                translated_count += 1
                                self.stdout.write(
                                    f'✓ Translated: {candidate.full_name} (ID: {candidate.id})'
                                )
                            else:
                                self.stdout.write(
                                    f'- Skipped: {candidate.full_name} (ID: {candidate.id}) - No fields to translate'
                                )
                        else:
                            self.stdout.write(
                                f'- Skipped: {candidate.full_name} (ID: {candidate.id}) - Already has translations'
                            )

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error translating {candidate.full_name} (ID: {candidate.id}): {str(e)}'
                            )
                        )

            # Progress update
            processed = min(i + batch_size, total_count)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Progress: {processed}/{total_count} candidates processed'
                )
            )

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTranslation Complete!'
                f'\n  Total candidates: {total_count}'
                f'\n  Translated: {translated_count}'
                f'\n  Errors: {error_count}'
                f'\n  Skipped: {total_count - translated_count - error_count}'
            )
        )

        # Provide guidance on next steps
        if translated_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    '\nNote: Machine translations have been marked with is_mt_* flags.'
                    '\nConsider having native speakers review and improve these translations.'
                )
            )