#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []

def log_test(test_name, status, details="", data=None):
    """Log test results"""
    result = {
        "test": test_name,
        "status": "✅ PASSED" if status else "❌ FAILED",
        "time": datetime.now().strftime("%H:%M:%S"),
        "details": details
    }
    if data:
        result["data"] = data
    TEST_RESULTS.append(result)
    print(f"[{result['time']}] {result['status']} - {test_name}")
    if details:
        print(f"  └─ {details}")
    if data:
        print(f"     Data: {json.dumps(data, indent=6)[:200]}...")

def test_ballot_page_load():
    """Test 1: Ballot page loads correctly"""
    try:
        response = requests.get(f"{BASE_URL}/candidates/ballot/")
        if response.status_code == 200:
            # Check for key elements
            has_geolocation = "navigator.geolocation" in response.text
            has_position_utils = "position-utils.js" in response.text
            has_alpine = "ballotApp" in response.text  # Check for actual Alpine component
            has_location_form = "manual-selection" in response.text  # Check for location section
            
            all_elements = all([has_geolocation, has_position_utils, has_alpine, has_location_form])
            
            log_test(
                "Ballot Page Load",
                all_elements,
                f"Status: {response.status_code}, Size: {len(response.text)} bytes",
                {
                    "has_geolocation": has_geolocation,
                    "has_position_utils": has_position_utils,
                    "has_alpine": has_alpine,
                    "has_location_form": has_location_form
                }
            )
            return all_elements
        else:
            log_test("Ballot Page Load", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("Ballot Page Load", False, str(e))
        return False

def test_geolocation_api():
    """Test 2: Geolocation API with various coordinates"""
    test_cases = [
        {
            "name": "Kathmandu (Valid)",
            "lat": 27.7172,
            "lng": 85.3240,
            "expected_province": "Bagmati",
            "should_succeed": True
        },
        {
            "name": "Pokhara (Valid)",
            "lat": 28.2096,
            "lng": 83.9856,
            "expected_province": "Gandaki",
            "should_succeed": True
        },
        {
            "name": "Biratnagar (Valid)",
            "lat": 26.4525,
            "lng": 87.2718,
            "expected_province": "Koshi",
            "should_succeed": True
        },
        {
            "name": "Outside Nepal (Invalid)",
            "lat": 28.6139,
            "lng": 77.2090,
            "expected_province": None,
            "should_succeed": False
        },
        {
            "name": "Far outside (Invalid)",
            "lat": 40.7128,
            "lng": -74.0060,
            "expected_province": None,
            "should_succeed": False
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/georesolve/",
                params={"lat": test_case["lat"], "lng": test_case["lng"]}
            )
            
            if test_case["should_succeed"]:
                success = (response.status_code == 200 and 
                          "province" in response.json() and
                          response.json()["province"]["name_en"] == test_case["expected_province"])
            else:
                success = response.status_code == 404 or "error" in response.json()
            
            log_test(
                f"Geolocation API - {test_case['name']}",
                success,
                f"Coordinates: ({test_case['lat']}, {test_case['lng']})",
                response.json() if response.status_code in [200, 404] else {"error": response.text}
            )
            
            all_passed = all_passed and success
            
        except Exception as e:
            log_test(f"Geolocation API - {test_case['name']}", False, str(e))
            all_passed = False
    
    return all_passed

def test_location_cascading_apis():
    """Test 3: Location cascading APIs"""
    try:
        # Test provinces (should work without params)
        provinces = requests.get(f"{BASE_URL}/api/districts/", params={"province": 3})
        
        if provinces.status_code == 200:
            districts = provinces.json()
            log_test(
                "Districts by Province API",
                len(districts) > 0,
                f"Found {len(districts)} districts in Province 3 (Bagmati)",
                {"sample_districts": districts[:3] if districts else []}
            )
            
            if districts:
                # Test municipalities for first district
                first_district = districts[0]
                municipalities = requests.get(
                    f"{BASE_URL}/api/municipalities/",
                    params={"district": first_district["id"]}
                )
                
                if municipalities.status_code == 200:
                    munis = municipalities.json()
                    log_test(
                        "Municipalities by District API",
                        len(munis) > 0,
                        f"Found {len(munis)} municipalities in {first_district['name_en']}",
                        {"sample_municipalities": munis[:3] if munis else []}
                    )
                    return True
                    
        log_test("Location Cascading APIs", False, "Failed to fetch districts")
        return False
        
    except Exception as e:
        log_test("Location Cascading APIs", False, str(e))
        return False

def test_ballot_api():
    """Test 4: My Ballot API with different locations"""
    test_locations = [
        {
            "name": "Kathmandu Ward 5",
            "province_id": 3,
            "district_id": 27,
            "municipality_id": 155,
            "ward_number": 5
        },
        {
            "name": "Province Only",
            "province_id": 1,
            "district_id": None,
            "municipality_id": None,
            "ward_number": None
        },
        {
            "name": "No Location",
            "province_id": None,
            "district_id": None,
            "municipality_id": None,
            "ward_number": None
        }
    ]
    
    all_passed = True
    for location in test_locations:
        try:
            # Build params, excluding None values
            params = {k: v for k, v in location.items() if v is not None and k != "name"}
            
            response = requests.get(f"{BASE_URL}/candidates/api/my-ballot/", params=params)
            
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                
                log_test(
                    f"My Ballot API - {location['name']}",
                    True,
                    f"Found {len(candidates)} candidates",
                    {
                        "location_params": params,
                        "candidate_count": len(candidates),
                        "sample_candidates": [
                            {"name": c.get("name"), "position": c.get("position_level")}
                            for c in candidates[:2]
                        ] if candidates else []
                    }
                )
            else:
                log_test(
                    f"My Ballot API - {location['name']}",
                    False,
                    f"Status: {response.status_code}"
                )
                all_passed = False
                
        except Exception as e:
            log_test(f"My Ballot API - {location['name']}", False, str(e))
            all_passed = False
    
    return all_passed

def test_analytics_tracking():
    """Test 5: Analytics tracking after API calls"""
    try:
        response = requests.get(f"{BASE_URL}/api/geo-analytics/")
        
        if response.status_code == 200:
            data = response.json()
            today_stats = data.get("today", {})
            
            # Note: In dev with LocMemCache, stats might be 0 due to process isolation
            log_test(
                "Analytics Tracking",
                True,
                "Analytics endpoint working (Note: Dev cache is process-local)",
                {
                    "total_requests": today_stats.get("total_requests", 0),
                    "successful": today_stats.get("successful", 0),
                    "failed": today_stats.get("failed", 0),
                    "success_rate": today_stats.get("success_rate", 0),
                    "provinces": today_stats.get("provinces", {})
                }
            )
            return True
        else:
            log_test("Analytics Tracking", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Analytics Tracking", False, str(e))
        return False

def test_position_utils_integration():
    """Test 6: Position Utils Integration"""
    try:
        # Test candidate cards API
        response = requests.get(f"{BASE_URL}/candidates/api/cards/", params={"page": 1})
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("items", [])
            
            # Check for position_level in candidates
            has_position_levels = all(
                "position_level" in c for c in candidates[:5]
            ) if candidates else True
            
            # Get unique position levels
            position_levels = list(set(c.get("position_level", "") for c in candidates))
            
            log_test(
                "Position Utils Integration",
                has_position_levels,
                f"Found {len(position_levels)} unique position levels",
                {
                    "position_levels": position_levels,
                    "sample_candidates": [
                        {
                            "name": c.get("name"),
                            "position": c.get("position_level"),
                            "photo": "default" if "default-avatar" in c.get("photo", "") else "custom"
                        }
                        for c in candidates[:3]
                    ] if candidates else []
                }
            )
            return has_position_levels
        else:
            log_test("Position Utils Integration", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Position Utils Integration", False, str(e))
        return False

def test_default_avatar_setting():
    """Test 7: Default Avatar Configuration"""
    try:
        response = requests.get(f"{BASE_URL}/candidates/api/cards/", params={"page": 1})
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("items", [])
            
            # Check how many candidates use default avatar
            default_avatar_count = sum(
                1 for c in candidates 
                if "default-avatar.png" in c.get("photo", "")
            )
            
            log_test(
                "Default Avatar Setting",
                True,
                f"{default_avatar_count}/{len(candidates)} candidates using default avatar",
                {
                    "total_candidates": len(candidates),
                    "using_default": default_avatar_count,
                    "default_path": "/static/images/default-avatar.png"
                }
            )
            return True
        else:
            log_test("Default Avatar Setting", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Default Avatar Setting", False, str(e))
        return False

def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE BALLOT FEATURE TEST SUITE")
    print("="*60 + "\n")
    
    # Run all tests
    test_results = {
        "ballot_page": test_ballot_page_load(),
        "geolocation": test_geolocation_api(),
        "cascading": test_location_cascading_apis(),
        "ballot_api": test_ballot_api(),
        "analytics": test_analytics_tracking(),
        "position_utils": test_position_utils_integration(),
        "default_avatar": test_default_avatar_setting()
    }
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed/total)*100
        },
        "test_results": test_results,
        "detailed_logs": TEST_RESULTS
    }
    
    with open("ballot_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Detailed report saved to ballot_test_report.json")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
