#!/usr/bin/env python
"""
API Endpoint Testing Script for ElectNepal
Tests all documented API endpoints to ensure they're working properly
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET", data=None):
    """Test an API endpoint and return the result"""
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ SUCCESS")
            # Print first 200 chars of response
            content = response.text[:200]
            print(f"Response preview: {content}...")
            return True
        else:
            print(f"✗ FAILED: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("ElectNepal API Endpoint Testing")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = []

    # Test Location APIs
    print("\n" + "=" * 80)
    print("LOCATION APIs")
    print("=" * 80)

    results.append(test_endpoint(
        "Get All Districts",
        f"{BASE_URL}/api/districts/"
    ))

    results.append(test_endpoint(
        "Get Districts by Province",
        f"{BASE_URL}/api/districts/?province=1"
    ))

    results.append(test_endpoint(
        "Get All Municipalities",
        f"{BASE_URL}/api/municipalities/"
    ))

    results.append(test_endpoint(
        "Get Municipalities by District",
        f"{BASE_URL}/api/municipalities/?district=1"
    ))

    results.append(test_endpoint(
        "Get Municipality Wards",
        f"{BASE_URL}/api/municipalities/1/wards/"
    ))

    results.append(test_endpoint(
        "Get Location Statistics",
        f"{BASE_URL}/api/statistics/"
    ))

    # Test Candidate APIs
    print("\n" + "=" * 80)
    print("CANDIDATE APIs")
    print("=" * 80)

    results.append(test_endpoint(
        "Get Candidate Cards (paginated)",
        f"{BASE_URL}/candidates/api/cards/?page=1&page_size=5"
    ))

    results.append(test_endpoint(
        "Search Candidates",
        f"{BASE_URL}/candidates/api/cards/?q=test&page=1"
    ))

    results.append(test_endpoint(
        "Filter Candidates by Province",
        f"{BASE_URL}/candidates/api/cards/?province=1&page=1"
    ))

    results.append(test_endpoint(
        "Filter Candidates by Position",
        f"{BASE_URL}/candidates/api/cards/?position=ward&page=1"
    ))

    results.append(test_endpoint(
        "Get My Ballot",
        f"{BASE_URL}/candidates/api/my-ballot/?province_id=1&district_id=1&municipality_id=1&ward_number=1"
    ))

    # Test Documentation APIs
    print("\n" + "=" * 80)
    print("DOCUMENTATION APIs")
    print("=" * 80)

    results.append(test_endpoint(
        "OpenAPI Schema",
        f"{BASE_URL}/api/schema/"
    ))

    results.append(test_endpoint(
        "Swagger UI",
        f"{BASE_URL}/api/docs/"
    ))

    results.append(test_endpoint(
        "ReDoc",
        f"{BASE_URL}/api/redoc/"
    ))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")

if __name__ == "__main__":
    main()
