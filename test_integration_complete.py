#!/usr/bin/env python3
"""
Complete Frontend-Backend Integration Test
Tests all critical endpoints and response formats
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🔗 COMPLETE FRONTEND-BACKEND INTEGRATION TEST")
print("="*80)

# ============================================================================
# 1. SIGNUP (Create demo users if needed)
# ============================================================================
print("\n📝 STEP 1: Creating demo users...")

users_to_create = [
    {"email": "admin@dayflow.com", "first_name": "Admin", "last_name": "User", "company_name": "Dayflow"},
    {"email": "employee@dayflow.com", "first_name": "Employee", "last_name": "User", "company_name": "Dayflow"}
]

for user in users_to_create:
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            **user,
            "password": "test123456"  # At least 8 characters
        })
        if response.status_code == 201:
            print(f"   ✅ Created: {user['email']}")
        elif "already registered" in response.text:
            print(f"   ℹ️  Already exists: {user['email']}")
        else:
            print(f"   ⚠️  Signup response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# ============================================================================
# 2. LOGIN - CRITICAL TEST (Must match frontend expectations)
# ============================================================================
print("\n🔐 STEP 2: Testing LOGIN endpoint...")

login_payload = {
    "login_id_or_email": "admin@dayflow.com",
    "password": "test123456"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check response structure
        print(f"   ✅ Login returned 200 OK")
        print(f"   ✅ Has access_token: {'access_token' in data}")
        print(f"   ✅ Has user object: {'user' in data}")
        
        if 'user' in data:
            user = data['user']
            print(f"\n   User object fields:")
            print(f"      - login_id: {user.get('login_id')}")
            print(f"      - email: {user.get('email')}")
            print(f"      - name: {user.get('name')}")
            print(f"      - role: {user.get('role')}")
            print(f"      - joining_date: {user.get('joining_date')}")
        
        token = data.get('access_token')
        if token:
            print(f"\n   ✅ Got access token: {token[:50]}...")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.json()}")
        token = None
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    token = None

# ============================================================================
# 3. GET CURRENT USER
# ============================================================================
if token:
    print("\n👤 STEP 3: Testing GET /auth/users/me...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/users/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ Got current user: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Fields: {list(user.keys())}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ============================================================================
    # 4. ATTENDANCE ENDPOINTS
    # ============================================================================
    print("\n📅 STEP 4: Testing ATTENDANCE endpoints...")
    
    endpoints = [
        ("GET", "/attendance/today"),
        ("GET", "/attendance/records/admin@dayflow.com"),
        ("GET", "/attendance/weekly/admin@dayflow.com"),
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print(f"   ✅ {method} {endpoint} - OK")
            elif response.status_code == 404:
                print(f"   ❌ {method} {endpoint} - NOT FOUND (404)")
            else:
                print(f"   ⚠️  {method} {endpoint} - Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - Error: {e}")

    # ============================================================================
    # 5. PROFILE ENDPOINTS
    # ============================================================================
    print("\n👥 STEP 5: Testing PROFILE endpoints...")
    
    profile_endpoints = [
        ("PUT", "/profile/personal", {"date_of_birth": "1990-01-01", "gender": "Male", "address": "Test Address"}),
        ("PUT", "/profile/bank", {"bank_name": "Test Bank", "account_number": "12345678", "ifsc_code": "TESTIF"})
    ]
    
    for method, endpoint, payload in profile_endpoints:
        try:
            if method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"   ✅ {method} {endpoint} - OK")
            elif response.status_code == 404:
                print(f"   ❌ {method} {endpoint} - NOT FOUND (404)")
            else:
                print(f"   ⚠️  {method} {endpoint} - Status {response.status_code}")
                print(f"      Response: {response.json()}")
                
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - Error: {e}")

    # ============================================================================
    # 6. CHECK-IN/CHECK-OUT
    # ============================================================================
    print("\n⏰ STEP 6: Testing CHECK-IN/CHECK-OUT...")
    
    try:
        # Check-in
        response = requests.post(f"{BASE_URL}/attendance/check-in", headers=headers)
        if response.status_code == 200:
            print(f"   ✅ POST /attendance/check-in - OK")
        else:
            print(f"   ⚠️  POST /attendance/check-in - Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ POST /attendance/check-in - Error: {e}")
    
    try:
        # Check-out
        response = requests.post(f"{BASE_URL}/attendance/check-out", headers=headers)
        if response.status_code == 200:
            print(f"   ✅ POST /attendance/check-out - OK")
        else:
            print(f"   ⚠️  POST /attendance/check-out - Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ POST /attendance/check-out - Error: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ INTEGRATION TEST COMPLETE")
print("="*80)
print("\nNext steps:")
print("1. Open frontend: http://localhost:3000")
print("2. Login with: admin@dayflow.com / test123")
print("3. Test all features in the UI")
print("="*80 + "\n")
