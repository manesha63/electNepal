"""
Management command to optimize existing candidate photos in the database
Usage: python manage.py optimize_existing_images
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from candidates.models import Candidate
from candidates.image_utils import optimize_image, should_optimize_image, get_image_dimensions
import os


class Command(BaseCommand):
    help = 'Optimize all existing candidate photos to improve performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be optimized without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force optimization even for already optimized images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('Starting image optimization...'))

        candidates_with_photos = Candidate.objects.exclude(photo='').exclude(photo=None)
        total_candidates = candidates_with_photos.count()

        if total_candidates == 0:
            self.stdout.write(self.style.WARNING('No candidates with photos found.'))
            return

        self.stdout.write(f'Found {total_candidates} candidates with photos')

        optimized_count = 0
        skipped_count = 0
        error_count = 0
        total_size_before = 0
        total_size_after = 0

        for candidate in candidates_with_photos:
            try:
                if not candidate.photo:
                    continue

                # Get current image info
                try:
                    current_size = candidate.photo.size
                    width, height = get_image_dimensions(candidate.photo)
                except (IOError, OSError, AttributeError, ValueError) as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Could not read photo for {candidate.full_name} (ID: {candidate.pk}): '
                            f'{type(e).__name__}: {str(e)}'
                        )
                    )
                    error_count += 1
                    continue

                total_size_before += current_size

                # Check if optimization is needed
                if not force and not should_optimize_image(candidate.photo):
                    self.stdout.write(
                        f'  Skipping {candidate.full_name}: '
                        f'Already optimized ({current_size / 1024:.1f}KB, {width}x{height})'
                    )
                    skipped_count += 1
                    total_size_after += current_size
                    continue

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Would optimize {candidate.full_name}: '
                            f'{current_size / 1024:.1f}KB, {width}x{height}'
                        )
                    )
                    optimized_count += 1
                else:
                    # Optimize the image
                    candidate.photo.open()
                    optimized = optimize_image(candidate.photo)

                    if optimized:
                        # Save the optimized image
                        old_name = candidate.photo.name
                        candidate.photo.save(
                            os.path.basename(old_name),
                            optimized,
                            save=False
                        )
                        candidate.save(update_fields=['photo'])

                        # Get new size
                        new_size = candidate.photo.size
                        total_size_after += new_size

                        reduction = ((current_size - new_size) / current_size) * 100

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Optimized {candidate.full_name}: '
                                f'{current_size / 1024:.1f}KB -> {new_size / 1024:.1f}KB '
                                f'({reduction:.1f}% reduction)'
                            )
                        )
                        optimized_count += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Failed to optimize {candidate.full_name}'
                            )
                        )
                        error_count += 1
                        total_size_after += current_size

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error processing {candidate.full_name}: {str(e)}'
                    )
                )
                error_count += 1

        # Print summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('OPTIMIZATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

        if dry_run:
            self.stdout.write(f'DRY RUN MODE - No changes were made')

        self.stdout.write(f'Total candidates with photos: {total_candidates}')
        self.stdout.write(f'Optimized: {optimized_count}')
        self.stdout.write(f'Skipped (already optimized): {skipped_count}')
        self.stdout.write(f'Errors: {error_count}')

        if not dry_run and optimized_count > 0:
            total_reduction = total_size_before - total_size_after
            total_reduction_percent = (total_reduction / total_size_before) * 100 if total_size_before > 0 else 0

            self.stdout.write('')
            self.stdout.write(f'Total size before: {total_size_before / (1024 * 1024):.2f}MB')
            self.stdout.write(f'Total size after: {total_size_after / (1024 * 1024):.2f}MB')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Total saved: {total_reduction / (1024 * 1024):.2f}MB '
                    f'({total_reduction_percent:.1f}% reduction)'
                )
            )