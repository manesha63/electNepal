import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from locations.analytics import GeolocationAnalytics

# Get current stats
stats = GeolocationAnalytics.get_stats()
print("Today's Geolocation Analytics:")
print(f"Total Requests: {stats['total_requests']}")
print(f"Successful: {stats['successful']}")
print(f"Failed: {stats['failed']}")
print(f"Success Rate: {stats['success_rate']:.1f}%")
print(f"Provinces Hit: {stats['provinces']}")

# Get summary
summary = GeolocationAnalytics.get_summary()
print(f"\n30-Day Summary:")
print(f"Total All Time: {summary['total_all_time']}")
print(f"Success Rate All Time: {summary['success_rate_all_time']:.1f}%")
