from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District, Municipality


class LoginRedirectTests(TestCase):
    """Test that different user types are redirected to the correct dashboard after login"""

    def setUp(self):
        self.client = Client()

        # Create location data for candidate profile
        self.province = Province.objects.create(
            code='P1',
            name_en='Test Province',
            name_ne='टेस्ट प्रदेश'
        )
        self.district = District.objects.create(
            province=self.province,
            code='D1',
            name_en='Test District',
            name_ne='टेस्ट जिल्ला'
        )
        self.municipality = Municipality.objects.create(
            district=self.district,
            code='M1',
            name_en='Test Municipality',
            name_ne='टेस्ट नगरपालिका',
            municipality_type='municipality',
            total_wards=10
        )

    def test_admin_with_candidate_profile_redirects_to_admin(self):
        """Test that admin users are redirected to /admin/ even if they have a candidate profile"""
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='adminpass123'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # Create candidate profile for admin
        Candidate.objects.create(
            user=admin_user,
            full_name='Admin User',
            position_level='ward',
            province=self.province,
            district=self.district,
            municipality=self.municipality,
            ward_number=1
        )

        # Login and check redirect
        response = self.client.post(reverse('authentication:login'), {
            'username': 'admin_test',
            'password': 'adminpass123'
        })

        # Should redirect to admin dashboard
        self.assertRedirects(response, '/admin/', fetch_redirect_response=False)

    def test_staff_without_candidate_redirects_to_admin(self):
        """Test that staff users without candidate profile go to admin"""
        staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='staffpass123'
        )
        staff_user.is_staff = True
        staff_user.save()

        response = self.client.post(reverse('authentication:login'), {
            'username': 'staff_test',
            'password': 'staffpass123'
        })

        self.assertRedirects(response, '/admin/', fetch_redirect_response=False)

    def test_candidate_redirects_to_candidate_dashboard(self):
        """Test that regular candidates are redirected to candidate dashboard"""
        candidate_user = User.objects.create_user(
            username='candidate_test',
            email='candidate@test.com',
            password='candidatepass123'
        )

        # Create candidate profile
        Candidate.objects.create(
            user=candidate_user,
            full_name='Test Candidate',
            position_level='ward',
            province=self.province,
            district=self.district,
            municipality=self.municipality,
            ward_number=1
        )

        response = self.client.post(reverse('authentication:login'), {
            'username': 'candidate_test',
            'password': 'candidatepass123'
        })

        self.assertRedirects(response, reverse('candidates:dashboard'), fetch_redirect_response=False)

    def test_new_user_redirects_to_registration(self):
        """Test that users without candidate profile are redirected to registration"""
        new_user = User.objects.create_user(
            username='new_test',
            email='new@test.com',
            password='newpass123'
        )

        response = self.client.post(reverse('authentication:login'), {
            'username': 'new_test',
            'password': 'newpass123'
        })

        self.assertRedirects(response, reverse('candidates:register'), fetch_redirect_response=False)

    def test_next_parameter_overrides_default_redirect(self):
        """Test that 'next' parameter in URL overrides default redirect behavior"""
        admin_user = User.objects.create_user(
            username='admin_next',
            email='admin_next@test.com',
            password='adminpass123'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # Login with next parameter
        next_url = '/some/other/page/'
        response = self.client.post(
            f"{reverse('authentication:login')}?next={next_url}",
            {
                'username': 'admin_next',
                'password': 'adminpass123'
            }
        )

        # Should redirect to the 'next' URL, not admin dashboard
        self.assertRedirects(response, next_url, fetch_redirect_response=False)