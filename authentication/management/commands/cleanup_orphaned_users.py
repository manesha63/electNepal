"""
Management command to identify and clean up orphaned User accounts.

Orphaned users are accounts that:
- Have no associated Candidate profile
- Are not staff/superuser accounts
- Optionally, have been inactive for a specified period

Usage:
    # Dry run (list orphaned users without deleting)
    python manage.py cleanup_orphaned_users

    # Delete orphaned users
    python manage.py cleanup_orphaned_users --delete

    # Only delete users inactive for 30+ days
    python manage.py cleanup_orphaned_users --delete --days-inactive 30

    # Delete users created more than 7 days ago
    python manage.py cleanup_orphaned_users --delete --days-old 7
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Identify and clean up orphaned User accounts (users without Candidate profiles)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphaned users (default is dry-run mode)',
        )
        parser.add_argument(
            '--days-inactive',
            type=int,
            default=None,
            help='Only consider users who have not logged in for N days',
        )
        parser.add_argument(
            '--days-old',
            type=int,
            default=None,
            help='Only consider users created more than N days ago',
        )

    def handle(self, *args, **options):
        delete_mode = options['delete']
        days_inactive = options['days_inactive']
        days_old = options['days_old']

        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('ORPHANED USER ACCOUNT CLEANUP'))
        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write('')

        # Base query: users without Candidate profiles, excluding staff/superusers
        orphaned_users = User.objects.filter(
            candidate__isnull=True
        ).exclude(
            is_staff=True
        ).exclude(
            is_superuser=True
        )

        # Apply date filters if specified
        if days_inactive is not None:
            cutoff_date = timezone.now() - timedelta(days=days_inactive)
            orphaned_users = orphaned_users.filter(last_login__lt=cutoff_date) | orphaned_users.filter(last_login__isnull=True)
            self.stdout.write(f'Filter: Only users inactive for {days_inactive}+ days')

        if days_old is not None:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            orphaned_users = orphaned_users.filter(date_joined__lt=cutoff_date)
            self.stdout.write(f'Filter: Only users created {days_old}+ days ago')

        orphaned_count = orphaned_users.count()

        if orphaned_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ No orphaned user accounts found!'))
            return

        # Display statistics
        self.stdout.write(self.style.WARNING(f'\nFound {orphaned_count} orphaned user account(s):'))
        self.stdout.write('')

        # Display details for each orphaned user
        for i, user in enumerate(orphaned_users.order_by('date_joined'), 1):
            self.stdout.write(f'{i}. {user.username} (ID: {user.id})')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   Joined: {user.date_joined.strftime("%Y-%m-%d %H:%M")}')
            if user.last_login:
                self.stdout.write(f'   Last Login: {user.last_login.strftime("%Y-%m-%d %H:%M")}')
            else:
                self.stdout.write(f'   Last Login: Never')
            self.stdout.write(f'   Active: {user.is_active}')
            self.stdout.write('')

        # Perform deletion or show dry-run message
        if delete_mode:
            self.stdout.write(self.style.WARNING('=' * 80))
            self.stdout.write(self.style.WARNING('DELETING ORPHANED USERS...'))
            self.stdout.write(self.style.WARNING('=' * 80))

            # Get usernames before deletion for confirmation message
            deleted_usernames = list(orphaned_users.values_list('username', flat=True))

            # Perform deletion
            deleted_count, deleted_objects = orphaned_users.delete()

            self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully deleted {deleted_count} user account(s):'))
            for username in deleted_usernames:
                self.stdout.write(f'  - {username}')

            # Show breakdown of deleted objects
            if deleted_objects:
                self.stdout.write('\nDeleted objects breakdown:')
                for model, count in deleted_objects.items():
                    if count > 0:
                        self.stdout.write(f'  - {model}: {count}')

        else:
            self.stdout.write(self.style.WARNING('=' * 80))
            self.stdout.write(self.style.WARNING('DRY RUN MODE (no changes made)'))
            self.stdout.write(self.style.WARNING('=' * 80))
            self.stdout.write(self.style.NOTICE(f'\nTo delete these {orphaned_count} orphaned user(s), run:'))
            self.stdout.write(self.style.NOTICE('  python manage.py cleanup_orphaned_users --delete'))
            if days_inactive:
                self.stdout.write(self.style.NOTICE(f'  python manage.py cleanup_orphaned_users --delete --days-inactive {days_inactive}'))
            if days_old:
                self.stdout.write(self.style.NOTICE(f'  python manage.py cleanup_orphaned_users --delete --days-old {days_old}'))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=' * 80))
