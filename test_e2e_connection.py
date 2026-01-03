"""
End-to-End Integration Test
Tests the complete Frontend <-> Backend connection using Playwright
"""

import pytest
from playwright.sync_api import sync_playwright, expect
from pymongo import MongoClient
import time
import os

# ========================================
# CONFIGURATION
# ========================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "dayflow_hrms"

# Test credentials
ADMIN_EMAIL = "test_admin@dayflow.com"
ADMIN_PASSWORD = "TestAdmin123"
EMPLOYEE_EMAIL = "test_employee@dayflow.com"


# ========================================
# DATABASE UTILITIES
# ========================================

def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DB_NAME]


def reset_test_data():
    """Clean up test data from database"""
    db = get_db()
    # Remove test users
    db.users.delete_many({"login_id": {"$regex": "test_"}})
    db.attendance.delete_many({"user_id": {"$regex": "test_"}})
    db.salary_details.delete_many({"user_id": {"$regex": "test_"}})
    db.leaves.delete_many({"user_id": {"$regex": "test_"}})
    db.leave_balances.delete_many({"user_id": {"$regex": "test_"}})
    print("✅ Test data cleaned from database")


# ========================================
# TEST SUITE
# ========================================

@pytest.fixture(scope="function")
def cleanup():
    """Cleanup before and after each test"""
    reset_test_data()
    yield
    reset_test_data()


def test_backend_health(cleanup):
    """Test 1: Verify backend is running"""
    print("\n▶️  TEST 1: Backend Health Check")
    
    import requests
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Backend is healthy")
    except Exception as e:
        pytest.fail(f"❌ Backend health check failed: {e}")


def test_end_to_end_login_flow(cleanup):
    """Test 2: Complete user flow - Registration, Login, and Dashboard"""
    print("\n▶️  TEST 2: End-to-End Login Flow")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set to True for CI/CD
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # ========================================
            # STEP 1: Check Frontend is Running
            # ========================================
            print("  Step 1: Navigating to frontend...")
            page.goto(FRONTEND_URL, wait_until="networkidle")
            expect(page).to_have_url(f"{FRONTEND_URL}/", timeout=10000)
            print("  ✅ Frontend loaded successfully")
            
            # ========================================
            # STEP 2: Navigate to Login Page
            # ========================================
            print("  Step 2: Going to login page...")
            page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
            page.wait_for_timeout(1000)
            print("  ✅ Login page loaded")
            
            # ========================================
            # STEP 3: First, Create Admin User via Backend API
            # ========================================
            print("  Step 3: Creating admin user via backend...")
            import requests
            
            # Register admin user directly via API
            try:
                register_response = requests.post(
                    f"{BACKEND_URL}/auth/register",
                    json={
                        "login_id": ADMIN_EMAIL,
                        "password": ADMIN_PASSWORD,
                        "name": "Test Admin",
                        "role": "ADMIN",
                        "joining_date": "2026-01-03T00:00:00"
                    }
                )
                if register_response.status_code in [200, 201]:
                    print("  ✅ Admin user created")
                else:
                    print(f"  ⚠️  Admin creation returned {register_response.status_code}")
            except Exception as e:
                print(f"  ⚠️  Admin creation: {e}")
            
            # ========================================
            # STEP 4: Login via Frontend
            # ========================================
            print("  Step 4: Logging in via frontend...")
            
            # Find and fill login form
            try:
                email_input = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first
                password_input = page.locator('input[type="password"], input[name="password"]').first
                submit_button = page.locator('button[type="submit"]').first
                
                email_input.fill(ADMIN_EMAIL)
                password_input.fill(ADMIN_PASSWORD)
                
                # Click login and wait for navigation
                submit_button.click()
                page.wait_for_timeout(3000)  # Wait for backend API call
                
                # Check if we're redirected (either to dashboard or another authenticated page)
                current_url = page.url
                print(f"  Current URL after login: {current_url}")
                
                # Verify we're not on login page anymore
                if "/login" not in current_url:
                    print("  ✅ Login successful - redirected from login page")
                else:
                    # Check for error messages
                    error_msg = page.locator('text=/error|invalid|failed/i').first
                    if error_msg.is_visible():
                        error_text = error_msg.text_content()
                        pytest.fail(f"  ❌ Login failed with error: {error_text}")
                    else:
                        pytest.fail("  ❌ Still on login page - login may have failed")
                        
            except Exception as e:
                pytest.fail(f"  ❌ Login interaction failed: {e}")
            
            # ========================================
            # STEP 5: Verify Token in LocalStorage
            # ========================================
            print("  Step 5: Checking authentication token...")
            token = page.evaluate("() => localStorage.getItem('access_token')")
            
            if token:
                print(f"  ✅ Token found in localStorage: {token[:20]}...")
            else:
                pytest.fail("  ❌ No authentication token found in localStorage")
            
            # ========================================
            # STEP 6: Verify Database Entry
            # ========================================
            print("  Step 6: Verifying database entry...")
            db = get_db()
            user = db.users.find_one({"login_id": ADMIN_EMAIL})
            
            if user:
                print(f"  ✅ User found in database: {user['name']}")
                assert user['role'] == 'ADMIN', "User role mismatch"
            else:
                pytest.fail("  ❌ User not found in database")
            
            # ========================================
            # STEP 7: Test API Call from Frontend
            # ========================================
            print("  Step 7: Testing API call from frontend...")
            page.wait_for_timeout(2000)
            
            # Check console for API logs
            console_messages = []
            page.on("console", lambda msg: console_messages.append(msg.text()))
            
            # Try to navigate to a page that makes API calls
            page.goto(f"{FRONTEND_URL}/dashboard", wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # Check if any API calls were made
            api_logs = [msg for msg in console_messages if 'API' in msg or 'api' in msg]
            if api_logs:
                print(f"  ✅ API calls detected: {len(api_logs)} logs")
            else:
                print("  ⚠️  No API call logs found (might be normal)")
            
            print("\n✅ ALL TESTS PASSED!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            # Take screenshot on failure
            page.screenshot(path="test_failure.png")
            raise
        
        finally:
            browser.close()


def test_attendance_flow(cleanup):
    """Test 3: Attendance Check-in/Check-out Flow"""
    print("\n▶️  TEST 3: Attendance Flow")
    
    import requests
    
    try:
        # Create employee via API
        print("  Creating test employee...")
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "login_id": EMPLOYEE_EMAIL,
                "password": "Employee123",
                "name": "Test Employee",
                "role": "EMPLOYEE",
                "joining_date": "2026-01-03T00:00:00"
            }
        )
        assert register_response.status_code in [200, 201], "Employee creation failed"
        
        # Login
        print("  Logging in...")
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id": EMPLOYEE_EMAIL,
                "password": "Employee123"
            }
        )
        assert login_response.status_code == 200, "Login failed"
        token = login_response.json()["access_token"]
        
        # Check-in
        print("  Checking in...")
        checkin_response = requests.post(
            f"{BACKEND_URL}/attendance/check-in",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert checkin_response.status_code in [200, 201], "Check-in failed"
        print("  ✅ Check-in successful")
        
        # Verify in database
        db = get_db()
        attendance = db.attendance.find_one({"user_id": EMPLOYEE_EMAIL})
        assert attendance is not None, "Attendance record not found"
        assert attendance["status"] == "PRESENT", "Attendance status incorrect"
        
        print("✅ Attendance flow test passed!")
        
    except Exception as e:
        pytest.fail(f"❌ Attendance flow test failed: {e}")


def test_leave_balance_integration(cleanup):
    """Test 4: Leave Balance System"""
    print("\n▶️  TEST 4: Leave Balance Integration")
    
    import requests
    
    try:
        # Create employee
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "login_id": "test_leave@dayflow.com",
                "password": "Employee123",
                "name": "Leave Test",
                "role": "EMPLOYEE",
                "joining_date": "2026-01-03T00:00:00"
            }
        )
        
        # Login
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id": "test_leave@dayflow.com",
                "password": "Employee123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Check leave balance
        print("  Checking leave balance...")
        balance_response = requests.get(
            f"{BACKEND_URL}/leaves/me/balance",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert balance_response.status_code == 200, "Balance check failed"
        
        balance = balance_response.json()
        assert balance["paid_leave_balance"] == 24.0, "Paid leave balance incorrect"
        assert balance["sick_leave_balance"] == 7.0, "Sick leave balance incorrect"
        
        print(f"  ✅ Leave balances: {balance['paid_leave_balance']} paid, {balance['sick_leave_balance']} sick")
        print("✅ Leave balance test passed!")
        
    except Exception as e:
        pytest.fail(f"❌ Leave balance test failed: {e}")


# ========================================
# RUN TESTS
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("END-TO-END INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"MongoDB URL: {MONGODB_URL}")
    print("="*60)
    
    pytest.main([__file__, "-v", "-s"])
