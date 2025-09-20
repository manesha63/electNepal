"""
Management command to ensure all content is properly translated
"""

from django.core.management.base import BaseCommand
from core.auto_translate import translate_all_existing_content


class Command(BaseCommand):
    help = 'Ensures all content in database is properly translated to Nepali'

    def handle(self, *args, **options):
        self.stdout.write('Starting automatic translation of all content...')
        translate_all_existing_content()
        self.stdout.write(self.style.SUCCESS('Successfully translated all content!'))