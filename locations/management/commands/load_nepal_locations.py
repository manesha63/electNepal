import json
from django.core.management.base import BaseCommand
from django.db import transaction
from locations.models import Province, District, Municipality

class Command(BaseCommand):
    help = 'Load Nepal administrative divisions into database from local JSON'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='data/nepal_locations.json')

    @transaction.atomic
    def handle(self, *args, **opts):
        fp = opts['file']
        data = json.load(open(fp, 'r', encoding='utf-8'))
        pc = dc = mc = 0
        for p in data.get('provinces', []):
            _, created = Province.objects.get_or_create(code=p['code'], defaults={'name_en':p['name_en'],'name_ne':p['name_ne']})
            pc += int(created)
        for d in data.get('districts', []):
            province = Province.objects.get(code=d['province_code'])
            _, created = District.objects.get_or_create(code=d['code'], defaults={'province':province,'name_en':d['name_en'],'name_ne':d['name_ne']})
            dc += int(created)
        for m in data.get('municipalities', []):
            district = District.objects.get(code=m['district_code'])
            _, created = Municipality.objects.get_or_create(code=m['code'], defaults={
                'district':district,'name_en':m['name_en'],'name_ne':m['name_ne'],
                'municipality_type':m['type'],'total_wards':m.get('total_wards',9)})
            mc += int(created)
        self.stdout.write(self.style.SUCCESS(f"Imported: provinces={pc}, districts={dc}, municipalities={mc}"))