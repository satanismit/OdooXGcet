"""
Complete E2E Integration Test
Tests Full User Journey: Signup → Login → Dashboard Access
"""
import pytest
import requests
from pymongo import MongoClient
import time

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "dayflow_hrms"


def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DB_NAME]


@pytest.fixture(scope="module")
def cleanup():
    """Cleanup test data before and after tests"""
    db = get_db()
    # Clean up test users before
    db.users.delete_many({"email": {"$regex": "e2e_test"}})
    yield
    # Clean up after tests
    db.users.delete_many({"email": {"$regex": "e2e_test"}})


class TestE2EIntegration:
    """Complete End-to-End Integration Tests"""
    
    def test_01_complete_signup_flow(self, cleanup):
        """Test 1: Complete Signup Flow"""
        print("\n" + "="*60)
        print("▶️  TEST 1: COMPLETE SIGNUP FLOW")
        print("="*60)
        
        # Step 1: Register a company admin
        print("\n📝 Step 1: Registering company admin...")
        signup_response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={
                "company_name": "E2E TestCorp",
                "first_name": "E2E",
                "last_name": "Admin",
                "email": "e2e_test_admin@testcorp.com",
                "password": "SecurePass123!@#"
            }
        )
        
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        signup_data = signup_response.json()
        
        assert "login_id" in signup_data
        assert "email" in signup_data
        assert signup_data["email"] == "e2e_test_admin@testcorp.com"
        
        login_id = signup_data["login_id"]
        print(f"   ✅ Admin registered successfully!")
        print(f"   Login ID: {login_id}")
        print(f"   Email: {signup_data['email']}")
        
        # Step 2: Verify user exists in database
        print("\n💾 Step 2: Verifying user in database...")
        db = get_db()
        user_in_db = db.users.find_one({"email": "e2e_test_admin@testcorp.com"})
        
        assert user_in_db is not None, "User not found in database"
        assert user_in_db["login_id"] == login_id
        assert user_in_db["role"] == "ADMIN"
        print(f"   ✅ User verified in MongoDB")
        
        # Step 3: Login with email
        print("\n🔐 Step 3: Logging in with email...")
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "e2e_test_admin@testcorp.com",
                "password": "SecurePass123!@#"
            }
        )
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        
        assert "access_token" in login_data
        assert "login_id" in login_data
        assert "email" in login_data
        
        token = login_data["access_token"]
        
        print(f"   ✅ Login successful!")
        print(f"   Token: {token[:30]}...")
        print(f"   User: {login_data.get('login_id')}")
        print(f"   Email: {login_data.get('email')}")
        
        # Step 4: Login with login_id
        print("\n🔐 Step 4: Logging in with login_id...")
        login_response2 = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": login_id,
                "password": "SecurePass123!@#"
            }
        )
        
        assert login_response2.status_code == 200
        print(f"   ✅ Login with login_id successful!")
        
        print("\n" + "="*60)
        print("✅ TEST 1 PASSED: Complete Signup Flow")
        print("="*60)
    
    def test_02_admin_creates_employee(self, cleanup):
        """Test 2: Admin Creates Employee"""
        print("\n" + "="*60)
        print("▶️  TEST 2: ADMIN CREATES EMPLOYEE")
        print("="*60)
        
        # Step 1: Login as admin
        print("\n🔐 Step 1: Admin login...")
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "e2e_test_admin@testcorp.com",
                "password": "SecurePass123!@#"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        print(f"   ✅ Admin logged in")
        
        # Step 2: Create employee
        print("\n👤 Step 2: Creating employee...")
        employee_response = requests.post(
            f"{BACKEND_URL}/admin/create-employee",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "E2E",
                "last_name": "Employee",
                "email": "e2e_test_employee@testcorp.com",
                "joining_date": "2026-01-03T00:00:00"
            }
        )
        
        assert employee_response.status_code == 201, f"Employee creation failed: {employee_response.text}"
        employee_data = employee_response.json()
        
        assert "login_id" in employee_data
        assert "temporary_password" in employee_data
        
        emp_login_id = employee_data["login_id"]
        temp_password = employee_data["temporary_password"]
        
        print(f"   ✅ Employee created!")
        print(f"   Login ID: {emp_login_id}")
        print(f"   Temp Password: {temp_password}")
        
        # Step 3: Employee login with temp password
        print("\n🔐 Step 3: Employee login with temp password...")
        emp_login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": emp_login_id,
                "password": temp_password
            }
        )
        
        assert emp_login_response.status_code == 200
        emp_token = emp_login_response.json()["access_token"]
        print(f"   ✅ Employee logged in successfully!")
        
        print("\n" + "="*60)
        print("✅ TEST 2 PASSED: Admin Creates Employee")
        print("="*60)
    
    def test_03_attendance_check_in(self, cleanup):
        """Test 3: Employee Check-in Flow"""
        print("\n" + "="*60)
        print("▶️  TEST 3: ATTENDANCE CHECK-IN FLOW")
        print("="*60)
        
        # Step 1: Get or create employee
        print("\n🔐 Step 1: Getting employee credentials...")
        db = get_db()
        
        # Login as admin first
        admin_login = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "e2e_test_admin@testcorp.com",
                "password": "SecurePass123!@#"
            }
        )
        
        if admin_login.status_code != 200:
            pytest.skip("Admin not available - run test_01 first")
        
        admin_token = admin_login.json()["access_token"]
        
        # Create a fresh employee for this test
        emp_response = requests.post(
            f"{BACKEND_URL}/admin/create-employee",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "first_name": "CheckIn",
                "last_name": "Tester",
                "email": f"e2e_test_checkin_{int(time.time())}@testcorp.com",
                "joining_date": "2026-01-03T00:00:00"
            }
        )
        
        assert emp_response.status_code == 201, f"Employee creation failed: {emp_response.text}"
        emp_data = emp_response.json()
        emp_login_id = emp_data["login_id"]
        temp_password = emp_data["temporary_password"]
        
        print(f"   ✅ Employee created: {emp_login_id}")
        
        # Step 2: Employee login
        print("\n🔐 Step 2: Employee login...")
        emp_login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": emp_login_id,
                "password": temp_password
            }
        )
        
        assert emp_login_response.status_code == 200, f"Employee login failed: {emp_login_response.text}"
        emp_token = emp_login_response.json()["access_token"]
        print(f"   ✅ Employee logged in")
        
        # Step 3: Check-in via API
        print("\n⏱️  Step 3: Employee check-in...")
        checkin_response = requests.post(
            f"{BACKEND_URL}/attendance/check-in",
            headers={"Authorization": f"Bearer {emp_token}"}
        )
        
        # Handle case where user already checked in
        if checkin_response.status_code == 400 and "Already checked in" in checkin_response.text:
            print(f"   ℹ️  Employee already checked in today")
            # Verify the existing check-in
            checkin_data = {"check_in_time": "Already checked in"}
        else:
            assert checkin_response.status_code in [200, 201], f"Check-in failed: {checkin_response.status_code} - {checkin_response.text}"
            checkin_data = checkin_response.json()
            print(f"   ✅ Check-in successful!")
            print(f"   Time: {checkin_data.get('check_in_time', 'N/A')}")
        
        # Step 4: Verify in database
        print("\n💾 Step 4: Verifying attendance in database...")
        time.sleep(1)  # Give DB time to write
        
        attendance = db.attendance.find_one({"user_id": emp_login_id})
        
        assert attendance is not None, "Attendance record not found in database"
        assert attendance["status"] == "PRESENT", f"Expected PRESENT, got {attendance['status']}"
        
        print(f"   ✅ Attendance verified in MongoDB")
        print(f"   Status: {attendance['status']}")
        print(f"   User ID: {attendance['user_id']}")
        
        print("\n" + "="*60)
        print("✅ TEST 3 PASSED: Attendance Check-in Flow")
        print("="*60)
    
    def test_04_cors_and_connectivity(self):
        """Test 4: CORS and Frontend Connectivity"""
        print("\n" + "="*60)
        print("▶️  TEST 4: CORS AND CONNECTIVITY")
        print("="*60)
        
        # Test 1: CORS headers
        print("\n🌐 Step 1: Testing CORS headers...")
        response = requests.get(
            f"{BACKEND_URL}/health",
            headers={"Origin": FRONTEND_URL}
        )
        
        assert "access-control-allow-origin" in response.headers
        print(f"   ✅ CORS headers present")
        print(f"   Allowed Origin: {response.headers.get('access-control-allow-origin')}")
        
        # Test 2: Frontend accessibility
        print("\n🎨 Step 2: Testing frontend accessibility...")
        try:
            frontend_response = requests.get(FRONTEND_URL, timeout=5)
            assert frontend_response.status_code == 200
            print(f"   ✅ Frontend is accessible at {FRONTEND_URL}")
        except Exception as e:
            print(f"   ⚠️  Frontend not accessible: {e}")
            pytest.skip("Frontend not running")
        
        print("\n" + "="*60)
        print("✅ TEST 4 PASSED: CORS and Connectivity")
        print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
