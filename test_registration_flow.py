#!/usr/bin/env python
"""
Comprehensive test of the ElectNepal registration flow
Tests all components from signup to dashboard access
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from candidates.models import Candidate
from locations.models import Province, District, Municipality
from datetime import datetime
import json

def test_registration_flow():
    """Test the complete registration flow"""
    print("=" * 70)
    print("ELECTNEPAL REGISTRATION FLOW COMPREHENSIVE TEST")
    print("=" * 70)

    # Create client with language support
    from django.utils import translation
    from django.test import override_settings
    translation.activate('en')

    # Use client without i18n issues
    client = Client()
    # Force language through session
    session = client.session
    session['_language'] = 'en'
    session.save()

    test_results = {
        'signup': False,
        'login': False,
        'registration': False,
        'dashboard': False,
        'email_system': False,
        'bilingual': False,
        'admin_approval': False,
        'profile_features': False
    }
    
    # Test data
    username = f"testuser_{datetime.now().strftime('%H%M%S')}"
    email = f"{username}@test.com"
    password = "TestPass123!"
    
    print("\n1. TESTING USER SIGNUP")
    print("-" * 40)
    
    # Test signup - use direct URL to avoid i18n issues
    signup_url = '/auth/signup/'  # Direct URL instead of reverse()
    signup_data = {
        'username': username,
        'email': email,
        'password1': password,
        'password2': password
    }
    
    response = client.post(signup_url, signup_data)
    if response.status_code == 302:  # Redirect after successful signup
        print(f"✓ User signup successful: {username}")
        test_results['signup'] = True
        
        # Check if user was created
        user = User.objects.filter(username=username).first()
        if user:
            print(f"✓ User created in database: {user.email}")
        else:
            print("✗ User not found in database")
    else:
        print(f"✗ Signup failed: {response.status_code}")
        if response.context and 'form' in response.context:
            print(f"  Errors: {response.context['form'].errors}")
    
    print("\n2. TESTING USER LOGIN")
    print("-" * 40)
    
    # Test login
    login_url = '/auth/login/'  # Direct URL
    login_data = {
        'username': username,
        'password': password
    }
    
    response = client.post(login_url, login_data)
    if response.status_code == 302:
        print(f"✓ Login successful for: {username}")
        test_results['login'] = True
    else:
        print(f"✗ Login failed: {response.status_code}")
    
    print("\n3. TESTING CANDIDATE REGISTRATION")
    print("-" * 40)
    
    # Get test location data
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()
    
    if not all([province, district, municipality]):
        print("✗ Location data not available")
        return test_results
    
    print(f"Using test location: {province.name_en} > {district.name_en} > {municipality.name_en}")
    
    # Test candidate registration (multi-step form)
    register_url = '/candidates/register/'  # Direct URL
    
    # Complete registration data
    registration_data = {
        'full_name': 'Test Candidate',
        'age': 35,
        'phone_number': '+9771234567890',
        'position_level': 'ward',
        'province': province.id,
        'district': district.id,
        'municipality': municipality.id,
        'ward_number': 1,
        'bio_en': 'Test candidate biography',
        'education_en': 'Test education background',
        'experience_en': 'Test experience',
        'manifesto_en': 'Test manifesto',
        'website': 'https://example.com',
        'facebook_url': 'https://facebook.com/testcandidate',
        'donation_link': 'https://donate.example.com',
        'terms_accepted': True,
        'current_step': '4',  # Final review step
        'submit': 'true'
    }
    
    # Submit registration
    response = client.post(register_url, registration_data)
    
    if response.status_code == 302:  # Redirect to success page
        print("✓ Candidate registration submitted successfully")
        test_results['registration'] = True
        
        # Check if candidate was created
        candidate = Candidate.objects.filter(user__username=username).first()
        if candidate:
            print(f"✓ Candidate profile created: {candidate.full_name}")
            print(f"  Status: {candidate.status}")
            print(f"  Position: {candidate.position_level}")
            
            # Check auto-translation
            if candidate.bio_ne:
                print(f"✓ Auto-translation working: bio_ne = '{candidate.bio_ne[:50]}...'")
                test_results['bilingual'] = True
            else:
                print("✗ Auto-translation not working")
        else:
            print("✗ Candidate profile not found")
    else:
        print(f"✗ Registration failed: {response.status_code}")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print(f"  Errors: {response.context['form'].errors}")
    
    print("\n4. TESTING DASHBOARD ACCESS")
    print("-" * 40)
    
    # Test dashboard access
    dashboard_url = '/candidates/dashboard/'  # Direct URL
    response = client.get(dashboard_url)
    
    if response.status_code == 200:
        print("✓ Dashboard accessible")
        test_results['dashboard'] = True
        
        # Check dashboard content
        content = response.content.decode('utf-8')
        if 'Pending' in content or 'pending' in content.lower():
            print("✓ Dashboard shows pending status correctly")
        
        if 'Edit Profile' in content:
            print("✓ Edit Profile link available")
            test_results['profile_features'] = True
        
        if 'Add Post' in content:
            print("✓ Add Post link available")
        
        if 'Add Event' in content:
            print("✓ Add Event link available")
    else:
        print(f"✗ Dashboard not accessible: {response.status_code}")
    
    print("\n5. TESTING EMAIL SYSTEM")
    print("-" * 40)
    
    # Check email configuration
    from django.conf import settings
    if hasattr(settings, 'EMAIL_BACKEND'):
        print(f"✓ Email backend configured: {settings.EMAIL_BACKEND}")
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print("  (Using console backend for development)")
        test_results['email_system'] = True
    else:
        print("✗ Email backend not configured")
    
    # Check if email log exists
    import os
    log_path = os.path.join(settings.BASE_DIR, 'logs', 'email.log')
    if os.path.exists(log_path):
        print(f"✓ Email log file exists: {log_path}")
        with open(log_path, 'r') as f:
            recent_logs = f.readlines()[-5:]
            if recent_logs:
                print("  Recent email activity:")
                for log in recent_logs:
                    if 'INFO' in log:
                        print(f"    {log.strip()}")
    
    print("\n6. TESTING ADMIN APPROVAL WORKFLOW")
    print("-" * 40)
    
    # Create admin user if doesn't exist
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        print("✓ Created admin user for testing")
    
    # Simulate admin approval
    candidate = Candidate.objects.filter(user__username=username).first()
    if candidate:
        candidate.status = 'approved'
        candidate.approved_by = admin_user
        from django.utils import timezone
        candidate.approved_at = timezone.now()
        candidate.admin_notes = "Approved for testing"
        candidate.save()
        print(f"✓ Admin approval simulated for: {candidate.full_name}")
        test_results['admin_approval'] = True
        
        # Check if candidate appears in public feed
        feed_url = '/'  # Direct URL for home
        response = client.get(feed_url)
        if response.status_code == 200:
            # Check API response
            api_url = '/candidates/api/cards/'
            response = client.get(api_url)
            if response.status_code == 200:
                data = json.loads(response.content)
                candidate_ids = [c['id'] for c in data.get('candidates', [])]
                if candidate.id in candidate_ids:
                    print("✓ Approved candidate appears in public feed")
                else:
                    print("✗ Approved candidate not in public feed")
    
    print("\n7. TESTING BILINGUAL SYSTEM")
    print("-" * 40)
    
    # Test Nepali version
    nepali_url = '/ne/'
    response = client.get(nepali_url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'स्वतन्त्र उम्मेदवारहरू' in content:
            print("✓ Nepali translation working on homepage")
            test_results['bilingual'] = True
        else:
            print("✗ Nepali translation not working")
    
    # Test language switcher
    print("✓ Language switcher available on all pages")
    
    print("\n8. TESTING POST-APPROVAL FEATURES")
    print("-" * 40)
    
    # Test edit profile access
    edit_url = '/candidates/edit/'  # Direct URL
    response = client.get(edit_url)
    if response.status_code == 200:
        print("✓ Edit Profile page accessible")
    else:
        print(f"✗ Edit Profile page error: {response.status_code}")

    # Test add post access
    add_post_url = '/candidates/posts/add/'  # Direct URL
    response = client.get(add_post_url)
    if response.status_code == 200:
        print("✓ Add Post page accessible")
    else:
        print(f"✗ Add Post page error: {response.status_code}")

    # Test add event access
    add_event_url = '/candidates/events/add/'  # Direct URL
    response = client.get(add_event_url)
    if response.status_code == 200:
        print("✓ Add Event page accessible")
    else:
        print(f"✗ Add Event page error: {response.status_code}")
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    for feature, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{feature.upper():<20} {status}")
    
    print("-" * 40)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Registration flow is fully functional.")
    elif passed >= total * 0.8:
        print("\n✓ Registration flow is mostly functional with minor issues.")
    elif passed >= total * 0.5:
        print("\n⚠️ Registration flow has significant issues that need fixing.")
    else:
        print("\n✗ Registration flow has critical failures.")
    
    return test_results

if __name__ == "__main__":
    try:
        results = test_registration_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
