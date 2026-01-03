"""
Quick API Validation - Focus on 403 Forbidden Issues
"""
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

print("\n" + "="*70)
print("🔍 API AUTHORIZATION VALIDATION")
print("="*70)

# Test 1: Create employee WITHOUT authentication
print("\n▶️  Test 1: POST /admin/create-employee (NO TOKEN)")
response = requests.post(
    f"{BACKEND_URL}/admin/create-employee",
    json={
        "first_name": "Test",
        "last_name": "User",
        "email": f"test.{datetime.now().timestamp()}@test.com",
        "joining_date": datetime.now().isoformat()
    }
)
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 Unauthorized")
print(f"   Result: {'✅ PASS' if response.status_code == 401 else '❌ FAIL'}")

# Test 2: Get admin token
print("\n▶️  Test 2: Login as Admin")
login_response = requests.post(
    f"{BACKEND_URL}/auth/login",
    json={
        "login_id_or_email": "admin@testcorp.com",
        "password": "Admin123!@#"
    }
)
print(f"   Status: {login_response.status_code}")

if login_response.status_code == 200:
    admin_token = login_response.json()["access_token"]
    print(f"   Token: {admin_token[:30]}...")
    
    # Test 3: Create employee WITH admin token
    print("\n▶️  Test 3: POST /admin/create-employee (WITH ADMIN TOKEN)")
    response = requests.post(
        f"{BACKEND_URL}/admin/create-employee",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Valid",
            "last_name": "Employee",
            "email": f"valid.emp.{datetime.now().timestamp()}@test.com",
            "joining_date": datetime.now().isoformat()
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 201 Created")
    print(f"   Result: {'✅ PASS' if response.status_code == 201 else '❌ FAIL'}")
    
    if response.status_code == 201:
        emp_data = response.json()
        print(f"   Employee Login ID: {emp_data.get('login_id')}")
        print(f"   Temp Password: {emp_data.get('temporary_password')}")
        
        # Test 4: Login as employee
        print("\n▶️  Test 4: Login as Employee")
        emp_login = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": emp_data.get('login_id'),
                "password": emp_data.get('temporary_password')
            }
        )
        print(f"   Status: {emp_login.status_code}")
        
        if emp_login.status_code == 200:
            emp_token = emp_login.json()["access_token"]
            print(f"   Employee Token: {emp_token[:30]}...")
            
            # Test 5: Try to create employee with EMPLOYEE token (should fail 403)
            print("\n▶️  Test 5: POST /admin/create-employee (WITH EMPLOYEE TOKEN)")
            response = requests.post(
                f"{BACKEND_URL}/admin/create-employee",
                headers={"Authorization": f"Bearer {emp_token}"},
                json={
                    "first_name": "Unauthorized",
                    "last_name": "Attempt",
                    "email": f"unauth.{datetime.now().timestamp()}@test.com",
                    "joining_date": datetime.now().isoformat()
                }
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            print(f"   Expected: 403 Forbidden")
            print(f"   Result: {'✅ PASS' if response.status_code == 403 else '❌ FAIL'}")
    else:
        print(f"   ❌ Failed to create employee: {response.text[:200]}")
else:
    print(f"   ❌ Admin login failed: {login_response.text}")

# Test 6: Check-in without auth
print("\n▶️  Test 6: POST /attendance/check-in (NO TOKEN)")
response = requests.post(
    f"{BACKEND_URL}/attendance/check-in",
    json={}
)
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 Unauthorized")
print(f"   Result: {'✅ PASS' if response.status_code == 401 else '❌ FAIL'}")

print("\n" + "="*70)
print("✅ AUTHORIZATION TESTS COMPLETE")
print("="*70)
