import requests
import json

print("\n" + "="*80)
print("🔍 DEBUGGING FRONTEND-BACKEND CONNECTION")
print("="*80)

BASE_URL = "http://localhost:8000"

# Test 1: Health
print("\n1️⃣  Testing Backend Health...")
try:
    r = requests.get(f"{BASE_URL}/health")
    print(f"   ✅ Backend alive: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"   ❌ Backend dead: {e}")
    exit(1)

# Test 2: Create demo admin
print("\n2️⃣  Creating demo admin (admin@dayflow.com)...")
signup_data = {
    "company_name": "Dayflow",
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@dayflow.com",
    "password": "admin123"
}
try:
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if r.status_code == 201:
        print(f"   ✅ Admin created: {r.json()['login_id']}")
    elif r.status_code == 400 and "already registered" in r.text:
        print(f"   ℹ️  Admin already exists")
    else:
        print(f"   ❌ Unexpected: {r.status_code} - {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Login
print("\n3️⃣  Testing Login...")
login_data = {
    "login_id_or_email": "admin@dayflow.com",
    "password": "admin123"
}
try:
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print(f"   ✅ Login SUCCESS")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"   ❌ Login FAILED: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 4: Check /attendance/today
print("\n4️⃣  Testing GET /attendance/today...")
try:
    r = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    if r.status_code == 200:
        print(f"   ✅ Endpoint works! Response: {r.json()}")
    elif r.status_code == 404:
        print(f"   ❌ 404 NOT FOUND - Endpoint missing!")
    else:
        print(f"   ⚠️  Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Check /profile/personal
print("\n5️⃣  Testing PUT /profile/personal...")
try:
    r = requests.put(f"{BASE_URL}/profile/personal", headers=headers, json={
        "father_name": "Test",
        "date_of_birth": "1990-01-01"
    })
    if r.status_code == 200:
        print(f"   ✅ Endpoint works!")
    elif r.status_code == 404:
        print(f"   ❌ 404 NOT FOUND - Endpoint missing!")
    else:
        print(f"   ⚠️  Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("✅ DEBUGGING COMPLETE")
print("="*80)
