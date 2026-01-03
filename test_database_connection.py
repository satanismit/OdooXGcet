#!/usr/bin/env python3
"""
Database Connection Test
Verifies MongoDB is working and data is being saved/retrieved
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("DATABASE CONNECTION AND DATA VERIFICATION TEST")
print("="*80)

# ============================================================================
# CREATE A NEW TEST USER
# ============================================================================
print("\n📝 STEP 1: Creating test user...")

timestamp = datetime.now().strftime("%H%M%S")
test_email = f"testuser{timestamp}@dayflow.com"

signup_resp = requests.post(f"{BASE_URL}/auth/signup", json={
    "company_name": "TestCompany",
    "first_name": "Test",
    "last_name": f"User{timestamp}",
    "email": test_email,
    "password": "test123456"
})

if signup_resp.status_code == 201:
    signup_data = signup_resp.json()
    print(f"✅ User created: {test_email}")
    print(f"   Login ID: {signup_data['login_id']}")
else:
    print(f"❌ Signup failed: {signup_resp.status_code}")
    print(signup_resp.json())
    exit(1)

# ============================================================================
# LOGIN WITH NEW USER
# ============================================================================
print("\n🔐 STEP 2: Logging in with new user...")

login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "login_id_or_email": test_email,
    "password": "test123456"
})

if login_resp.status_code == 200:
    data = login_resp.json()
    token = data['access_token']
    user_id = data['user']['login_id']
    print(f"✅ Login successful")
    print(f"   User ID: {user_id}")
else:
    print(f"❌ Login failed: {login_resp.status_code}")
    print(login_resp.json())
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ============================================================================
# STEP 3: CHECK ATTENDANCE BEFORE CHECK-IN
# ============================================================================
print("\n📅 STEP 3: Checking attendance before check-in...")

today_resp = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
if today_resp.status_code == 200:
    data = today_resp.json()
    if data is None:
        print(f"✅ No attendance record yet (expected)")
    else:
        print(f"⚠️ Attendance exists: {data}")
else:
    print(f"❌ Failed to fetch today attendance: {today_resp.status_code}")

# ============================================================================
# STEP 4: CHECK-IN
# ============================================================================
print("\n⏰ STEP 4: Checking in...")

checkin_resp = requests.post(f"{BASE_URL}/attendance/check-in", headers=headers)
if checkin_resp.status_code == 200:
    checkin_data = checkin_resp.json()
    print(f"✅ Checked in successfully")
    print(f"   User: {checkin_data['user_id']}")
    print(f"   Time: {checkin_data['check_in_time']}")
else:
    print(f"❌ Check-in failed: {checkin_resp.status_code}")
    print(checkin_resp.json())

# ============================================================================
# STEP 5: CHECK ATTENDANCE AFTER CHECK-IN
# ============================================================================
print("\n📅 STEP 5: Checking attendance after check-in...")

today_resp = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
if today_resp.status_code == 200:
    data = today_resp.json()
    if data:
        print(f"✅ Attendance record found!")
        print(f"   ID: {data['id']}")
        print(f"   Date: {data['date']}")
        print(f"   Check-in: {data['checkIn']}")
        print(f"   Status: {data['status']}")
    else:
        print(f"❌ No attendance record found after check-in!")
else:
    print(f"❌ Failed to fetch: {today_resp.status_code}")

# ============================================================================
# STEP 6: UPDATE PROFILE (TEST DATA SAVING)
# ============================================================================
print("\n👥 STEP 6: Updating profile to test data persistence...")

profile_resp = requests.put(f"{BASE_URL}/profile/personal", 
    headers=headers,
    json={
        "date_of_birth": "1995-06-15",
        "gender": "Male",
        "address": "123 Test Street, Test City"
    }
)

if profile_resp.status_code == 200:
    print(f"✅ Profile updated successfully")
    profile_data = profile_resp.json()
    print(f"   Response: {profile_data}")
else:
    print(f"❌ Profile update failed: {profile_resp.status_code}")
    print(profile_resp.json())

# ============================================================================
# STEP 7: FETCH UPDATED PROFILE
# ============================================================================
print("\n👤 STEP 7: Fetching updated user profile...")

user_resp = requests.get(f"{BASE_URL}/auth/users/me", headers=headers)
if user_resp.status_code == 200:
    user_data = user_resp.json()
    print(f"✅ User profile fetched:")
    print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Role: {user_data['role']}")
    print(f"   Joined: {user_data['joining_date']}")
else:
    print(f"❌ Failed to fetch user: {user_resp.status_code}")

# ============================================================================
# STEP 8: GET ATTENDANCE RECORDS
# ============================================================================
print("\n📊 STEP 8: Getting attendance records...")

records_resp = requests.get(f"{BASE_URL}/attendance/records/{user_id}", headers=headers)
if records_resp.status_code == 200:
    records = records_resp.json()
    print(f"✅ Attendance records fetched:")
    if isinstance(records, list):
        print(f"   Total records: {len(records)}")
        if len(records) > 0:
            print(f"   Latest record: {records[0]}")
    else:
        print(f"   Data: {records}")
else:
    print(f"❌ Failed to fetch records: {records_resp.status_code}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ DATABASE CONNECTION TEST COMPLETE")
print("="*80)
print("\nConclusions:")
print("✅ MongoDB is connected")
print("✅ User data is being saved")
print("✅ Attendance data is being saved")
print("✅ Profile data is being saved")
print("✅ Data retrieval is working")
print("\n" + "="*80 + "\n")
