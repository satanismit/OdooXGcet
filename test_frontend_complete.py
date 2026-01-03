"""
Complete Frontend-Backend Integration Test
Tests ALL endpoints that frontend expects
"""
import requests
import json

BASE = "http://localhost:8000"

print("\n" + "="*80)
print("🧪 COMPLETE FRONTEND-BACKEND INTEGRATION TEST")
print("="*80)

# STEP 1: Check backend health
print("\n📌 STEP 1: Backend Health")
try:
    r = requests.get(f"{BASE}/")
    print(f"✅ Backend: {r.json()['version']}")
except Exception as e:
    print(f"❌ Backend down: {e}")
    exit(1)

# STEP 2: Create demo users
print("\n📌 STEP 2: Create Demo Users")
users = [
    {"email": "admin@dayflow.com", "password": "admin123", "first_name": "Admin", "last_name": "User", "company_name": "Dayflow"},
    {"email": "employee@dayflow.com", "password": "employee123", "first_name": "Employee", "last_name": "User", "company_name": "Dayflow"}
]

for user in users:
    try:
        r = requests.post(f"{BASE}/auth/signup", json=user)
        if r.status_code == 201:
            print(f"✅ Created: {user['email']}")
        elif "already registered" in r.text:
            print(f"ℹ️  Exists: {user['email']}")
        else:
            print(f"⚠️  {user['email']}: {r.status_code}")
    except Exception as e:
        print(f"❌ {user['email']}: {e}")

# STEP 3: Login as admin
print("\n📌 STEP 3: Admin Login")
try:
    r = requests.post(f"{BASE}/auth/login", json={
        "login_id_or_email": "admin@dayflow.com",
        "password": "admin123"
    })
    if r.status_code == 200:
        token = r.json()["access_token"]
        print(f"✅ Login successful")
    else:
        print(f"❌ Login failed: {r.status_code} - {r.text[:100]}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# STEP 4: Test all frontend endpoints
print("\n📌 STEP 4: Test Frontend Endpoints")
tests = [
    ("GET", "/auth/users/me", None, "Get current user"),
    ("GET", "/attendance/today", None, "Today's attendance"),
    ("POST", "/attendance/check-in", {}, "Check in"),
    ("GET", "/attendance/records/ADMIN0001", None, "Attendance records"),
    ("GET", "/attendance/weekly/ADMIN0001", None, "Weekly attendance"),
    ("GET", "/attendance/stats/ADMIN0001", None, "Attendance stats"),
    ("PUT", "/profile/personal", {"date_of_birth": "1990-01-01", "gender": "Male"}, "Update personal"),
    ("PUT", "/profile/bank", {"account_number": "1234567890", "bank_name": "Test Bank"}, "Update bank"),
    ("GET", "/dashboard/employees", None, "Get employees"),
]

results = {"passed": 0, "failed": 0, "errors": []}

for method, endpoint, body, description in tests:
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{endpoint}", headers=headers)
        elif method == "POST":
            r = requests.post(f"{BASE}{endpoint}", headers=headers, json=body)
        elif method == "PUT":
            r = requests.put(f"{BASE}{endpoint}", headers=headers, json=body)
        
        if r.status_code in [200, 201]:
            print(f"✅ {method:4} {endpoint:40} - {description}")
            results["passed"] += 1
        elif r.status_code == 404:
            print(f"❌ {method:4} {endpoint:40} - 404 NOT FOUND")
            results["failed"] += 1
            results["errors"].append(f"{method} {endpoint} → 404")
        else:
            print(f"⚠️  {method:4} {endpoint:40} - {r.status_code}")
            results["failed"] += 1
            results["errors"].append(f"{method} {endpoint} → {r.status_code}")
    except Exception as e:
        print(f"❌ {method:4} {endpoint:40} - ERROR: {str(e)[:30]}")
        results["failed"] += 1
        results["errors"].append(f"{method} {endpoint} → Error")

# SUMMARY
print("\n" + "="*80)
print(f"📊 RESULTS: {results['passed']}/{len(tests)} passed ({results['passed']*100//len(tests)}%)")
print("="*80)

if results["errors"]:
    print("\n❌ FAILED ENDPOINTS:")
    for error in results["errors"]:
        print(f"   - {error}")
else:
    print("\n🎉 ALL TESTS PASSED!")

print("\n" + "="*80)
