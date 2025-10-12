#!/usr/bin/env python
"""
Test script for health check endpoint
Verifies the endpoint works correctly and returns expected data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import Client
import json

print("=" * 80)
print("HEALTH ENDPOINT TEST")
print("=" * 80)

client = Client()

# Test 1: Health endpoint
print("\n1. Testing /api/health/:")
print("-" * 40)

try:
    response = client.get('/api/health/')

    if response.status_code == 200:
        print("✓ PASS: Returns 200 OK")

        data = response.json()

        # Check required fields
        required_fields = ['status', 'version', 'timestamp', 'database', 'api_endpoints']
        missing = [f for f in required_fields if f not in data]

        if missing:
            print(f"✗ FAIL: Missing fields: {missing}")
        else:
            print("✓ PASS: All required fields present")

        # Check field values
        if data['status'] in ['healthy', 'degraded', 'error']:
            print(f"✓ PASS: Status is valid: '{data['status']}'")
        else:
            print(f"✗ FAIL: Invalid status: '{data['status']}'")

        if data['database'] in ['connected', 'error']:
            print(f"✓ PASS: Database status is valid: '{data['database']}'")

        if 'api_endpoints' in data:
            locations = data['api_endpoints'].get('locations', 0)
            candidates = data['api_endpoints'].get('candidates', 0)
            print(f"✓ PASS: API endpoints data present")
            print(f"  - Locations: {locations}")
            print(f"  - Candidates: {candidates}")

        print(f"\nFull Response:")
        print(json.dumps(data, indent=2))

    else:
        print(f"✗ FAIL: Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"✗ FAIL: Exception occurred: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Version endpoint (alias)
print("\n2. Testing /api/version/ (alias):")
print("-" * 40)

try:
    response = client.get('/api/version/')

    if response.status_code == 200:
        print("✓ PASS: Returns 200 OK")
        data = response.json()

        if 'version' in data:
            print(f"✓ PASS: Version field present: {data['version']}")
        else:
            print("✗ FAIL: Version field missing")

    else:
        print(f"✗ FAIL: Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"✗ FAIL: Exception occurred: {e}")

# Test 3: Check endpoint is public (no auth required)
print("\n3. Testing public access (no authentication):")
print("-" * 40)

try:
    # Create a new client without session
    anon_client = Client()
    response = anon_client.get('/api/health/')

    if response.status_code == 200:
        print("✓ PASS: Endpoint is public (no auth required)")
    else:
        print(f"✗ FAIL: Requires authentication (status: {response.status_code})")

except Exception as e:
    print(f"✗ FAIL: Exception occurred: {e}")

# Test 4: Check other endpoints still work
print("\n4. Verifying existing endpoints still work:")
print("-" * 40)

endpoints_to_test = [
    ('/api/districts/', 'Districts API'),
    ('/api/statistics/', 'Statistics API'),
    ('/candidates/api/cards/', 'Candidate Cards API'),
]

for endpoint, name in endpoints_to_test:
    try:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✓ PASS: {name} ({endpoint})")
        else:
            print(f"✗ FAIL: {name} returned {response.status_code}")
    except Exception as e:
        print(f"✗ FAIL: {name} - {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
