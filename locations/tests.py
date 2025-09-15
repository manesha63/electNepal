from django.test import TestCase, Client
from django.urls import reverse
from .models import Province, District, Municipality
import json


class LocationModelTest(TestCase):
    def setUp(self):
        self.province = Province.objects.create(
            code='P01',
            name_en='Province 1',
            name_ne='प्रदेश १'
        )
        self.district = District.objects.create(
            code='D01',
            name_en='Test District',
            name_ne='परीक्षण जिल्ला',
            province=self.province
        )

    def test_province_str(self):
        self.assertEqual(str(self.province), 'Province 1')

    def test_district_str(self):
        self.assertEqual(str(self.district), 'Test District, Province 1')

    def test_municipality_creation(self):
        municipality = Municipality.objects.create(
            code='M01',
            name_en='Test Municipality',
            name_ne='परीक्षण नगरपालिका',
            district=self.district,
            municipality_type='municipality',
            total_wards=5
        )
        self.assertEqual(str(municipality), 'Test Municipality Municipality')
        self.assertEqual(municipality.total_wards, 5)

    def test_municipality_types(self):
        types = ['metropolitan', 'sub-metropolitan', 'municipality', 'rural']
        for mtype in types:
            municipality = Municipality.objects.create(
                code=f'M{mtype[:3].upper()}',
                name_en=f'{mtype.title()} Test',
                name_ne='परीक्षण',
                district=self.district,
                municipality_type=mtype,
                total_wards=3
            )
            self.assertEqual(municipality.municipality_type, mtype)


class LocationAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.province = Province.objects.create(
            code='P01',
            name_en='Province 1',
            name_ne='प्रदेश १'
        )
        self.district = District.objects.create(
            code='D01',
            name_en='Test District',
            name_ne='परीक्षण जिल्ला',
            province=self.province
        )
        self.municipality = Municipality.objects.create(
            code='M01',
            name_en='Test Municipality',
            name_ne='परीक्षण नगरपालिका',
            district=self.district,
            municipality_type='municipality',
            total_wards=5
        )

    def test_get_districts_api(self):
        response = self.client.get(reverse('locations_api:districts_by_province'), {'province': self.province.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name_en'], 'Test District')

    def test_get_municipalities_api(self):
        response = self.client.get(reverse('locations_api:municipalities_by_district'), {'district': self.district.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name_en'], 'Test Municipality')

    def test_get_districts_without_province(self):
        response = self.client.get(reverse('locations_api:districts_by_province'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_get_municipalities_without_district(self):
        response = self.client.get(reverse('locations_api:municipalities_by_district'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])
