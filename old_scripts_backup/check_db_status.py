from django import setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
setup()

from locations.models import Province, District, Municipality

print('CURRENT DATABASE STATUS:')
print('='*50)
print(f'Total Provinces: {Province.objects.count()}')
print(f'Total Districts: {District.objects.count()}')
print(f'Total Municipalities: {Municipality.objects.count()}')
print('='*50)

print('\nPROVINCE BREAKDOWN:')
for p in Province.objects.all().order_by('code'):
    d_count = p.districts.count()
    m_count = Municipality.objects.filter(district__province=p).count()
    print(f'{p.name_en}: {d_count} districts, {m_count} municipalities')

print('\nMUNICIPALITY TYPES:')
from django.db.models import Count
types = Municipality.objects.values('municipality_type').annotate(count=Count('municipality_type'))
for t in types:
    print(f"  {t['municipality_type']}: {t['count']}")

print('\nSAMPLE DISTRICTS (first 5):')
for d in District.objects.all()[:5]:
    m_count = d.municipalities.count()
    print(f'  {d.name_en} ({d.province.name_en}): {m_count} municipalities')