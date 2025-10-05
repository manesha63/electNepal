"""
Management command to create API keys
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api_auth.models import APIKey


class Command(BaseCommand):
    help = 'Create a new API key for a developer or organization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name to identify this API key'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Contact email for the API key holder'
        )
        parser.add_argument(
            '--organization',
            type=str,
            default='',
            help='Organization name (optional)'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username to associate with this API key (optional)'
        )
        parser.add_argument(
            '--read-only',
            action='store_true',
            help='Create a read-only API key (default allows read)'
        )
        parser.add_argument(
            '--can-write',
            action='store_true',
            help='Allow write permissions'
        )
        parser.add_argument(
            '--rate-limit',
            type=int,
            default=1000,
            help='Requests per hour limit (default: 1000)'
        )

    def handle(self, *args, **options):
        # Get or create user if username provided
        user = None
        if options['username']:
            try:
                user = User.objects.get(username=options['username'])
                self.stdout.write(
                    self.style.SUCCESS(f'Found user: {user.username}')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {options["username"]} not found')
                )
                return

        # Create API key
        api_key = APIKey.objects.create(
            key=APIKey.generate_key(),
            name=options['name'],
            contact_email=options['email'],
            organization=options['organization'],
            user=user,
            can_read=True,  # Always allow read
            can_write=options['can_write'],
            rate_limit=options['rate_limit']
        )

        # Display success message
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('API Key Created Successfully!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\nName:         {api_key.name}')
        self.stdout.write(f'Organization: {api_key.organization or "N/A"}')
        self.stdout.write(f'Email:        {api_key.contact_email}')
        self.stdout.write(f'User:         {api_key.user.username if api_key.user else "N/A"}')
        self.stdout.write(f'Permissions:  Read: ✓ | Write: {"✓" if api_key.can_write else "✗"}')
        self.stdout.write(f'Rate Limit:   {api_key.rate_limit} requests/hour')
        self.stdout.write(f'\n{self.style.WARNING("API Key (save this - it won\'t be shown again):")}')
        self.stdout.write(self.style.SUCCESS(f'{api_key.key}'))
        self.stdout.write('\n' + '='*70)
        self.stdout.write('\nUsage:')
        self.stdout.write('  curl -H "X-API-Key: ' + api_key.key + '" http://localhost:8000/api/districts/')
        self.stdout.write('='*70 + '\n')