"""
Management command to backfill missing bilingual fields
Fills empty Nepali fields from English using machine translation
Never overwrites existing human translations
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from candidates.models import Candidate, CandidatePost, CandidateEvent


class Command(BaseCommand):
    help = "Fill missing Nepali fields from English using machine translation"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without saving',
        )
        parser.add_argument(
            '--model',
            type=str,
            default='all',
            choices=['all', 'candidate', 'post', 'event'],
            help='Which model to backfill (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        model_choice = options['model']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be saved"))

        # Process each model type
        if model_choice in ['all', 'candidate']:
            self.backfill_candidates(dry_run)

        if model_choice in ['all', 'post']:
            self.backfill_posts(dry_run)

        if model_choice in ['all', 'event']:
            self.backfill_events(dry_run)

    def backfill_candidates(self, dry_run):
        """Backfill Candidate model"""
        self.stdout.write("Processing Candidates...")
        updated = 0
        skipped = 0

        with transaction.atomic():
            for candidate in Candidate.objects.all().iterator():
                # Track original values
                original_values = {
                    'bio_ne': candidate.bio_ne,
                    'education_ne': candidate.education_ne,
                    'experience_ne': candidate.experience_ne,
                    'manifesto_ne': candidate.manifesto_ne,
                }

                # Auto-translate missing fields
                candidate.autotranslate_missing()

                # Check if anything changed
                changed_fields = []
                for field, original in original_values.items():
                    if getattr(candidate, field) != original:
                        changed_fields.append(field)

                if changed_fields:
                    updated += 1
                    if dry_run:
                        self.stdout.write(
                            f"  Would update {candidate.full_name}: {', '.join(changed_fields)}"
                        )
                    else:
                        candidate.save(update_fields=changed_fields + [
                            f'is_mt_{field}' for field in ['bio_ne', 'education_ne', 'experience_ne', 'manifesto_ne']
                        ])
                        self.stdout.write(
                            f"  ✓ Updated {candidate.full_name}: {', '.join(changed_fields)}"
                        )
                else:
                    skipped += 1

            if dry_run:
                # Rollback transaction in dry-run mode
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Candidates: {'Would update' if dry_run else 'Updated'} {updated}, Skipped {skipped}"
            )
        )

    def backfill_posts(self, dry_run):
        """Backfill CandidatePost model"""
        self.stdout.write("Processing Candidate Posts...")
        updated = 0
        skipped = 0

        # First, check if CandidatePost has bilingual fields
        post_sample = CandidatePost.objects.first()
        if not post_sample or not hasattr(post_sample, 'title_ne'):
            self.stdout.write(
                self.style.WARNING(
                    "CandidatePost model doesn't have bilingual fields yet. Skipping."
                )
            )
            return

        with transaction.atomic():
            for post in CandidatePost.objects.all().iterator():
                original_title_ne = post.title_ne
                original_content_ne = post.content_ne

                # Auto-translate if empty
                if post.title and not post.title_ne:
                    from core.mt import mt
                    post.title_ne = mt.translate(post.title, "en", "ne")

                if post.content and not post.content_ne:
                    from core.mt import mt
                    post.content_ne = mt.translate(post.content, "en", "ne")

                if post.title_ne != original_title_ne or post.content_ne != original_content_ne:
                    updated += 1
                    if not dry_run:
                        post.save()
                else:
                    skipped += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Posts: {'Would update' if dry_run else 'Updated'} {updated}, Skipped {skipped}"
            )
        )

    def backfill_events(self, dry_run):
        """Backfill CandidateEvent model"""
        self.stdout.write("Processing Candidate Events...")
        updated = 0
        skipped = 0

        # First, check if CandidateEvent has bilingual fields
        event_sample = CandidateEvent.objects.first()
        if not event_sample or not hasattr(event_sample, 'title_ne'):
            self.stdout.write(
                self.style.WARNING(
                    "CandidateEvent model doesn't have bilingual fields yet. Skipping."
                )
            )
            return

        with transaction.atomic():
            for event in CandidateEvent.objects.all().iterator():
                original_title_ne = event.title_ne
                original_description_ne = event.description_ne
                original_location_ne = event.location_ne

                # Auto-translate if empty
                if event.title and not event.title_ne:
                    from core.mt import mt
                    event.title_ne = mt.translate(event.title, "en", "ne")

                if event.description and not event.description_ne:
                    from core.mt import mt
                    event.description_ne = mt.translate(event.description, "en", "ne")

                if event.location and not event.location_ne:
                    from core.mt import mt
                    event.location_ne = mt.translate(event.location, "en", "ne")

                if (event.title_ne != original_title_ne or
                    event.description_ne != original_description_ne or
                    event.location_ne != original_location_ne):
                    updated += 1
                    if not dry_run:
                        event.save()
                else:
                    skipped += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Events: {'Would update' if dry_run else 'Updated'} {updated}, Skipped {skipped}"
            )
        )