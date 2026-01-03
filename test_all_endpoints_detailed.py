#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing
Tests all API endpoints and shows results
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("COMPREHENSIVE API TEST - ALL ENDPOINTS")
print("="*80)

# ============================================================================
# STEP 1: LOGIN
# ============================================================================
print("\n📝 STEP 1: Login...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "login_id_or_email": "admin@dayflow.com",
        "password": "test123456"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        user_id = data['user']['login_id']
        print(f"✅ Login successful")
        print(f"   User: {user_id}")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ============================================================================
# STEP 2: TEST ALL ENDPOINTS
# ============================================================================
print("\n📊 STEP 2: Testing all endpoints...\n")

endpoints = [
    # Auth
    ("GET", "/auth/users/me", None, "Get Current User"),
    
    # Attendance GET
    ("GET", "/attendance/today", None, "Today Attendance"),
    ("GET", f"/attendance/records/{user_id}", None, "Attendance Records"),
    ("GET", f"/attendance/weekly/{user_id}", None, "Weekly Attendance"),
    ("GET", f"/attendance/stats/{user_id}", None, "Attendance Stats"),
    
    # Attendance POST
    ("POST", "/attendance/check-in", None, "Check In"),
    ("POST", "/attendance/check-out", None, "Check Out"),
    
    # Profile
    ("PUT", "/profile/personal", {"date_of_birth": "1990-01-01", "gender": "Male"}, "Update Personal"),
    ("PUT", "/profile/bank", {"bank_name": "Test Bank", "account_number": "12345678", "ifsc_code": "TESTIF"}, "Update Bank"),
    
    # Dashboard
    ("GET", "/dashboard/employees", None, "Dashboard Employees"),
]

results = {"pass": 0, "fail": 0, "errors": []}

for method, path, body, name in endpoints:
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=body or {}, timeout=5)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=body or {}, timeout=5)
        
        if resp.status_code in [200, 201]:
            print(f"✅ {method:6} {path:50} - {name}")
            results["pass"] += 1
        else:
            print(f"❌ {method:6} {path:50} - {name} (HTTP {resp.status_code})")
            results["fail"] += 1
            results["errors"].append({
                "endpoint": f"{method} {path}",
                "status": resp.status_code,
                "name": name
            })
    except Exception as e:
        print(f"❌ {method:6} {path:50} - {name} (Error: {str(e)[:40]})")
        results["fail"] += 1
        results["errors"].append({
            "endpoint": f"{method} {path}",
            "error": str(e),
            "name": name
        })

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\n✅ Passed: {results['pass']}/{results['pass']+results['fail']}")
print(f"❌ Failed: {results['fail']}/{results['pass']+results['fail']}")

if results['errors']:
    print("\nFailed Endpoints:")
    for error in results['errors']:
        print(f"  - {error['name']} ({error['endpoint']})")
        if 'status' in error:
            print(f"    Status: {error['status']}")
        if 'error' in error:
            print(f"    Error: {error['error']}")

print("\n" + "="*80 + "\n")
