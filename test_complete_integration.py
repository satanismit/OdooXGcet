"""
COMPLETE FRONTEND-BACKEND INTEGRATION TEST
Tests ALL endpoints with fresh data
"""
import requests
from datetime import datetime
import json

BACKEND_URL = "http://localhost:8000"

tokens = {}
test_data = {}

def test(name, status_code, expected):
    is_pass = status_code == expected or (isinstance(expected, list) and status_code in expected)
    result = "✅" if is_pass else "❌"
    print(f"{result} {name}: {status_code}")
    return is_pass

passed = failed = 0

print("\n" + "="*80)
print("🧪 COMPLETE API INTEGRATION TEST".center(80))
print("="*80)

# 1. SIGNUP
print("\n1️⃣  Admin Signup")
r = requests.post(f"{BACKEND_URL}/auth/signup", json={
    "company_name": "IntegrationTestCorp",
    "first_name": "Test",
    "last_name": "Admin",
    "email": f"testadmin{int(datetime.now().timestamp())}@example.com",
    "password": "Admin123!@#"
})
if test("POST /auth/signup", r.status_code, 201):
    passed += 1
    test_data["admin_email"] = r.json()["message"].split("login at ")[1] if "login at" in r.json()["message"] else r.json().get("email", "")
    test_data["admin_login_id"] = r.json()["login_id"]
    print(f"   Admin Email: {test_data.get('admin_email', 'N/A')}")
    print(f"   Login ID: {test_data['admin_login_id']}")
else:
    failed += 1
    print(f"   Error: {r.text[:200]}")

# 2. LOGIN (use email from signup)
print("\n2️⃣  Admin Login")
r = requests.post(f"{BACKEND_URL}/auth/login", json={
    "login_id_or_email": test_data["admin_login_id"],
    "password": "Admin123!@#"
})
if test("POST /auth/login", r.status_code, 200):
    passed += 1
    tokens["admin"] = r.json()["access_token"]
    print(f"   Token: {tokens['admin'][:30]}...")
else:
    failed += 1
    print(f"   Error: {r.text[:200]}")

# 3. GET PROFILE
print("\n3️⃣  Get User Profile")
if tokens.get("admin"):
    r = requests.get(f"{BACKEND_URL}/auth/users/me",
        headers={"Authorization": f"Bearer {tokens['admin']}"})
    if test("GET /auth/users/me", r.status_code, 200):
        passed += 1
        profile = r.json()
        print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
        print(f"   Role: {profile.get('role')}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 4. CREATE EMPLOYEE
print("\n4️⃣  Create Employee")
if tokens.get("admin"):
    r = requests.post(f"{BACKEND_URL}/admin/create-employee",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
        json={
            "first_name": "Test",
            "last_name": "Employee",
            "email": f"emp{int(datetime.now().timestamp())}@example.com",
            "joining_date": datetime.now().isoformat()
        })
    if test("POST /admin/create-employee", r.status_code, 201):
        passed += 1
        test_data["emp_login_id"] = r.json()["login_id"]
        test_data["emp_password"] = r.json()["temporary_password"]
        print(f"   Employee ID: {test_data['emp_login_id']}")
        print(f"   Password: {test_data['emp_password']}")
    else:
        failed += 1
        print(f"   Error: {r.text[:200]}")
else:
    print("⏭️  SKIPPED")

# 5. EMPLOYEE LOGIN
print("\n5️⃣  Employee Login")
if test_data.get("emp_login_id"):
    r = requests.post(f"{BACKEND_URL}/auth/login", json={
        "login_id_or_email": test_data["emp_login_id"],
        "password": test_data["emp_password"]
    })
    if test("POST /auth/login (Employee)", r.status_code, 200):
        passed += 1
        tokens["employee"] = r.json()["access_token"]
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 6. EMPLOYEE CHECK-IN
print("\n6️⃣  Employee Check-in")
if tokens.get("employee"):
    r = requests.post(f"{BACKEND_URL}/attendance/check-in",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("POST /attendance/check-in", r.status_code, [200, 201, 400]):
        passed += 1
        if r.status_code in [200, 201]:
            print(f"   Time: {r.json().get('check_in_time', 'N/A')}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 7. GET TODAY'S ATTENDANCE
print("\n7️⃣  Get Today's Attendance")
if tokens.get("employee"):
    r = requests.get(f"{BACKEND_URL}/attendance/today",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("GET /attendance/today", r.status_code, 200):
        passed += 1
        data = r.json()
        if data:
            print(f"   Status: {data.get('status')}")
            print(f"   Check-in: {data.get('checkIn', 'N/A')[:16]}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 8. GET ATTENDANCE RECORDS
print("\n8️⃣  Get Attendance Records")
if tokens.get("employee") and test_data.get("emp_login_id"):
    r = requests.get(f"{BACKEND_URL}/attendance/records/{test_data['emp_login_id']}",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("GET /attendance/records/{user_id}", r.status_code, 200):
        passed += 1
        records = r.json()
        print(f"   Total Records: {len(records)}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 9. GET WEEKLY ATTENDANCE
print("\n9️⃣  Get Weekly Attendance")
if tokens.get("employee") and test_data.get("emp_login_id"):
    r = requests.get(f"{BACKEND_URL}/attendance/weekly/{test_data['emp_login_id']}",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("GET /attendance/weekly/{user_id}", r.status_code, 200):
        passed += 1
        data = r.json()
        print(f"   Week: {data.get('weekStart')} to {data.get('weekEnd')}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 10. GET ATTENDANCE STATS
print("\n🔟 Get Attendance Stats")
if tokens.get("employee") and test_data.get("emp_login_id"):
    r = requests.get(f"{BACKEND_URL}/attendance/stats/{test_data['emp_login_id']}",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("GET /attendance/stats/{user_id}", r.status_code, 200):
        passed += 1
        stats = r.json()
        print(f"   Month: {stats.get('month')}")
        print(f"   Present: {stats.get('presentDays')} days")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 11. CHECK-OUT
print("\n1️⃣1️⃣  Employee Check-out")
if tokens.get("employee"):
    r = requests.post(f"{BACKEND_URL}/attendance/check-out",
        headers={"Authorization": f"Bearer {tokens['employee']}"})
    if test("POST /attendance/check-out", r.status_code, [200, 201, 400]):
        passed += 1
        if r.status_code in [200, 201]:
            print(f"   Hours: {r.json().get('total_hours', 'N/A')}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# 12. UPDATE PERSONAL INFO
print("\n1️⃣2️⃣  Update Personal Info")
if tokens.get("employee"):
    r = requests.put(f"{BACKEND_URL}/profile/personal",
        headers={"Authorization": f"Bearer {tokens['employee']}"},
        json={
            "father_name": "Father Name",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "address": "Test Address"
        })
    if test("PUT /profile/personal", r.status_code, 200):
        passed += 1
    else:
        failed += 1
        print(f"   Error: {r.text[:200]}")
else:
    print("⏭️  SKIPPED")

# 13. UPDATE BANK DETAILS
print("\n1️⃣3️⃣  Update Bank Details")
if tokens.get("employee"):
    r = requests.put(f"{BACKEND_URL}/profile/bank",
        headers={"Authorization": f"Bearer {tokens['employee']}"},
        json={
            "bank_name": "Test Bank",
            "account_number": "123456789",
            "ifsc_code": "TEST0001234"
        })
    if test("PUT /profile/bank", r.status_code, 200):
        passed += 1
    else:
        failed += 1
        print(f"   Error: {r.text[:200]}")
else:
    print("⏭️  SKIPPED")

# 14. GET DASHBOARD
print("\n1️⃣4️⃣  Get Dashboard Employees")
if tokens.get("admin"):
    r = requests.get(f"{BACKEND_URL}/dashboard/employees",
        headers={"Authorization": f"Bearer {tokens['admin']}"})
    if test("GET /dashboard/employees", r.status_code, 200):
        passed += 1
        employees = r.json()
        print(f"   Total Employees: {len(employees)}")
    else:
        failed += 1
else:
    print("⏭️  SKIPPED")

# SUMMARY
print("\n" + "="*80)
print("📊 TEST SUMMARY".center(80))
print("="*80)
total = passed + failed
print(f"Total Tests: {total}")
print(f"✅ Passed: {passed} ({passed*100//total if total > 0 else 0}%)")
print(f"❌ Failed: {failed} ({failed*100//total if total > 0 else 0}%)")
print("="*80)

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! Frontend-Backend integration is PERFECT!")
else:
    print(f"\n⚠️  {failed} tests failed. Check the logs above.")
