"""
Comprehensive API Testing Suite
Tests ALL backend endpoints with proper authentication and authorization
"""
import pytest
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient

# Configuration
BACKEND_URL = "http://localhost:8000"
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "dayflow_hrms"

# Test data storage
test_data = {
    "admin_token": None,
    "admin_login_id": None,
    "employee_token": None,
    "employee_login_id": None,
    "employee_email": None,
}


def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DB_NAME]


class TestAuthenticationAPIs:
    """Test all authentication endpoints"""
    
    def test_01_signup_new_admin(self):
        """POST /auth/signup - Create new company admin"""
        print("\n" + "="*70)
        print("🔐 AUTH API TESTS")
        print("="*70)
        print("\n▶️  Test 1: POST /auth/signup (New Admin)")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={
                "company_name": "API Test Corp",
                "first_name": "API",
                "last_name": "Admin",
                "email": f"api.admin.{datetime.now().timestamp()}@testcorp.com",
                "password": "Admin123!@#"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 201, f"Signup failed: {response.text}"
        
        data = response.json()
        assert "login_id" in data
        assert "message" in data
        
        test_data["admin_login_id"] = data["login_id"]
        
        print(f"✅ Admin created successfully")
        print(f"   Login ID: {data['login_id']}")
        print(f"   Message: {data['message']}")
    
    def test_02_signup_duplicate_email(self):
        """POST /auth/signup - Duplicate email should fail"""
        print("\n▶️  Test 2: POST /auth/signup (Duplicate Email)")
        
        # Try to signup with same email
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={
                "company_name": "API Test Corp",
                "first_name": "Duplicate",
                "last_name": "User",
                "email": "admin@testcorp.com",  # Existing email
                "password": "Admin123!@#"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 400, "Should reject duplicate email"
        assert "already registered" in response.text.lower()
        print("✅ Duplicate email properly rejected")
    
    def test_03_login_with_email(self):
        """POST /auth/login - Login with email"""
        print("\n▶️  Test 3: POST /auth/login (Email)")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "admin@testcorp.com",
                "password": "Admin123!@#"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        test_data["admin_token"] = data["access_token"]
        
        print(f"✅ Login successful with email")
        print(f"   Token: {data['access_token'][:30]}...")
    
    def test_04_login_with_login_id(self):
        """POST /auth/login - Login with login_id"""
        print("\n▶️  Test 4: POST /auth/login (Login ID)")
        
        if not test_data["admin_login_id"]:
            pytest.skip("No login_id available from signup")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": test_data["admin_login_id"],
                "password": "Admin123!@#"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        
        print(f"✅ Login successful with login_id")
    
    def test_05_login_wrong_password(self):
        """POST /auth/login - Wrong password should fail"""
        print("\n▶️  Test 5: POST /auth/login (Wrong Password)")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "admin@testcorp.com",
                "password": "WrongPassword123"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 401, "Should reject wrong password"
        print("✅ Wrong password properly rejected")
    
    def test_06_get_profile_authenticated(self):
        """GET /auth/users/me - Get current user profile"""
        print("\n▶️  Test 6: GET /auth/users/me (Authenticated)")
        
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        response = requests.get(
            f"{BACKEND_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {test_data['admin_token']}"}
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200, f"Profile fetch failed: {response.text}"
        
        profile = response.json()
        assert "email" in profile
        assert "login_id" in profile
        assert "role" in profile
        assert profile["role"] == "ADMIN"
        
        print(f"✅ Profile retrieved successfully")
        print(f"   Email: {profile['email']}")
        print(f"   Login ID: {profile['login_id']}")
        print(f"   Role: {profile['role']}")
    
    def test_07_get_profile_unauthenticated(self):
        """GET /auth/users/me - Without token should fail"""
        print("\n▶️  Test 7: GET /auth/users/me (No Token)")
        
        response = requests.get(f"{BACKEND_URL}/auth/users/me")
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 401, "Should reject unauthenticated request"
        print("✅ Unauthenticated request properly rejected")


class TestAdminAPIs:
    """Test all admin endpoints"""
    
    def test_08_create_employee_success(self):
        """POST /admin/create-employee - Admin creates employee"""
        print("\n" + "="*70)
        print("👤 ADMIN API TESTS")
        print("="*70)
        print("\n▶️  Test 8: POST /admin/create-employee (Authorized Admin)")
        
        if not test_data["admin_token"]:
            pytest.skip("No admin token available")
        
        timestamp = int(datetime.now().timestamp())
        employee_email = f"employee.{timestamp}@testcorp.com"
        
        response = requests.post(
            f"{BACKEND_URL}/admin/create-employee",
            headers={"Authorization": f"Bearer {test_data['admin_token']}"},
            json={
                "first_name": "Test",
                "last_name": "Employee",
                "email": employee_email,
                "joining_date": datetime.now().isoformat()
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 201, f"Employee creation failed: {response.text}"
        
        data = response.json()
        assert "login_id" in data
        assert "temporary_password" in data
        
        test_data["employee_login_id"] = data["login_id"]
        test_data["employee_temp_password"] = data["temporary_password"]
        test_data["employee_email"] = employee_email
        
        print(f"✅ Employee created successfully")
        print(f"   Login ID: {data['login_id']}")
        print(f"   Temp Password: {data['temporary_password']}")
    
    def test_09_create_employee_no_auth(self):
        """POST /admin/create-employee - Without token should fail"""
        print("\n▶️  Test 9: POST /admin/create-employee (No Token)")
        
        response = requests.post(
            f"{BACKEND_URL}/admin/create-employee",
            json={
                "first_name": "Test",
                "last_name": "Employee",
                "email": "unauthorized@testcorp.com",
                "joining_date": datetime.now().isoformat()
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 401, "Should reject unauthenticated request"
        print("✅ Unauthenticated request properly rejected (401)")
    
    def test_10_create_employee_non_admin(self):
        """POST /admin/create-employee - Employee role should get 403"""
        print("\n▶️  Test 10: POST /admin/create-employee (Non-Admin User)")
        
        if not test_data["employee_login_id"] or not test_data.get("employee_temp_password"):
            pytest.skip("No employee credentials available")
        
        # Login as employee first
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": test_data["employee_login_id"],
                "password": test_data["employee_temp_password"]
            }
        )
        
        if login_response.status_code != 200:
            pytest.skip("Cannot login as employee")
        
        employee_token = login_response.json()["access_token"]
        test_data["employee_token"] = employee_token
        
        # Try to create employee with employee token
        response = requests.post(
            f"{BACKEND_URL}/admin/create-employee",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "first_name": "Unauthorized",
                "last_name": "Employee",
                "email": f"unauth.{datetime.now().timestamp()}@testcorp.com",
                "joining_date": datetime.now().isoformat()
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 403, "Should reject non-admin user"
        assert "permission" in response.text.lower() or "forbidden" in response.text.lower()
        print("✅ Non-admin user properly rejected (403 Forbidden)")


class TestAttendanceAPIs:
    """Test all attendance endpoints"""
    
    def test_11_checkin_employee(self):
        """POST /attendance/check-in - Employee check-in"""
        print("\n" + "="*70)
        print("📋 ATTENDANCE API TESTS")
        print("="*70)
        print("\n▶️  Test 11: POST /attendance/check-in (Employee)")
        
        if not test_data.get("employee_token"):
            pytest.skip("No employee token available")
        
        response = requests.post(
            f"{BACKEND_URL}/attendance/check-in",
            headers={"Authorization": f"Bearer {test_data['employee_token']}"},
            json={}
        )
        
        print(f"  Status: {response.status_code}")
        
        # Accept both 200/201 for success, and 400 for "already checked in"
        if response.status_code == 400 and "already checked in" in response.text.lower():
            print("✅ Employee already checked in (idempotent)")
            return
        
        assert response.status_code in [200, 201], f"Check-in failed: {response.text}"
        
        data = response.json()
        print(f"✅ Check-in successful")
        print(f"   Time: {data.get('check_in_time', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
    
    def test_12_checkin_no_auth(self):
        """POST /attendance/check-in - Without token should fail"""
        print("\n▶️  Test 12: POST /attendance/check-in (No Token)")
        
        response = requests.post(
            f"{BACKEND_URL}/attendance/check-in",
            json={}
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 401, "Should reject unauthenticated request"
        print("✅ Unauthenticated request properly rejected")


class TestHealthAPIs:
    """Test health and utility endpoints"""
    
    def test_13_health_check(self):
        """GET /health - Health check endpoint"""
        print("\n" + "="*70)
        print("🏥 HEALTH & UTILITY API TESTS")
        print("="*70)
        print("\n▶️  Test 13: GET /health")
        
        response = requests.get(f"{BACKEND_URL}/health")
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        
        print(f"✅ Health check passed")
    
    def test_14_cors_headers(self):
        """OPTIONS /* - CORS preflight"""
        print("\n▶️  Test 14: CORS Headers")
        
        response = requests.options(
            f"{BACKEND_URL}/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200
        
        headers = response.headers
        assert "access-control-allow-origin" in headers
        print(f"✅ CORS configured correctly")
        print(f"   Allow-Origin: {headers.get('access-control-allow-origin')}")


class TestDatabaseIntegration:
    """Test database operations"""
    
    def test_15_database_connection(self):
        """Test MongoDB connection and collections"""
        print("\n" + "="*70)
        print("🗄️  DATABASE INTEGRATION TESTS")
        print("="*70)
        print("\n▶️  Test 15: MongoDB Connection")
        
        try:
            db = get_db()
            collections = db.list_collection_names()
            
            print(f"  Connected to: {DB_NAME}")
            print(f"  Collections: {collections}")
            
            assert len(collections) > 0, "No collections found"
            print(f"✅ MongoDB connection successful ({len(collections)} collections)")
        except Exception as e:
            pytest.fail(f"❌ MongoDB connection failed: {e}")
    
    def test_16_verify_admin_in_db(self):
        """Verify admin user was stored in database"""
        print("\n▶️  Test 16: Verify Admin in Database")
        
        if not test_data["admin_login_id"]:
            pytest.skip("No admin login_id available")
        
        try:
            db = get_db()
            user = db.User.find_one({"login_id": test_data["admin_login_id"]})
            
            if user:
                print(f"✅ Admin found in database")
                print(f"   Login ID: {user['login_id']}")
                print(f"   Email: {user['email']}")
                print(f"   Role: {user['role']}")
            else:
                pytest.fail("Admin not found in database")
        except Exception as e:
            pytest.fail(f"Database query failed: {e}")
    
    def test_17_verify_employee_in_db(self):
        """Verify employee was stored in database"""
        print("\n▶️  Test 17: Verify Employee in Database")
        
        if not test_data.get("employee_login_id"):
            pytest.skip("No employee login_id available")
        
        try:
            db = get_db()
            user = db.User.find_one({"login_id": test_data["employee_login_id"]})
            
            if user:
                print(f"✅ Employee found in database")
                print(f"   Login ID: {user['login_id']}")
                print(f"   Email: {user['email']}")
                print(f"   Role: {user['role']}")
                assert user["role"] == "EMPLOYEE"
            else:
                pytest.fail("Employee not found in database")
        except Exception as e:
            pytest.fail(f"Database query failed: {e}")


def print_test_summary():
    """Print summary of test data"""
    print("\n" + "="*70)
    print("📊 TEST DATA SUMMARY")
    print("="*70)
    for key, value in test_data.items():
        if value and "token" in key:
            print(f"{key}: {str(value)[:30]}...")
        else:
            print(f"{key}: {value}")
    print("="*70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
    print_test_summary()
