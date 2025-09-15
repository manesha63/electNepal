from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Candidate
from locations.models import Province, District, Municipality


class CandidateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcandidate',
            email='test@example.com',
            password='testpass123'
        )
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

    def test_candidate_creation(self):
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Test Candidate',
            position_level='municipality',
            province=self.province,
            district=self.district,
            municipality=self.municipality
        )
        self.assertEqual(candidate.full_name, 'Test Candidate')
        self.assertEqual(candidate.verification_status, 'pending')
        self.assertIsNotNone(candidate.created_at)

    def test_candidate_str_method(self):
        candidate = Candidate.objects.create(
            user=self.user,
            full_name='Test Candidate',
            position_level='municipality',
            province=self.province,
            district=self.district,
            municipality=self.municipality
        )
        self.assertEqual(str(candidate), 'Test Candidate (municipality)')

    def test_unique_user_constraint(self):
        Candidate.objects.create(
            user=self.user,
            full_name='First Candidate',
            position_level='municipality',
            province=self.province,
            district=self.district,
            municipality=self.municipality
        )
        
        with self.assertRaises(Exception):
            Candidate.objects.create(
                user=self.user,
                full_name='Second Candidate',
                position_level='municipality',
                province=self.province,
                district=self.district,
                municipality=self.municipality
            )


class CandidateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
        self.candidate = Candidate.objects.create(
            user=self.user,
            full_name='Test Candidate',
            position_level='municipality',
            province=self.province,
            district=self.district,
            municipality=self.municipality,
            bio_en='Test bio in English',
            bio_ne='नेपालीमा परीक्षण बायो',
            verification_status='verified'
        )

    def test_candidate_list_view(self):
        response = self.client.get(reverse('candidates:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Candidate')

    def test_candidate_detail_view(self):
        response = self.client.get(reverse('candidates:detail', kwargs={'pk': self.candidate.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Candidate')

    def test_candidate_list_filtering(self):
        # Test without filter - should show the candidate
        response = self.client.get(reverse('candidates:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Candidate')
