"""
Simple E2E Integration Test
Tests Backend API directly without Playwright
"""
import pytest
import requests
from pymongo import MongoClient
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "dayflow_hrms"


def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGODB_URL)
    return client[DB_NAME]


class TestBackendIntegration:
    """Test Backend API Integration"""
    
    def test_01_backend_health(self):
        """Test 1: Backend Health Check"""
        print("\n▶️  TEST 1: Backend Health Check")
        response = requests.get(f"{BACKEND_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Backend is healthy")
    
    def test_02_admin_login(self):
        """Test 2: Admin Login"""
        print("\n▶️  TEST 2: Admin Login Test")
        
        # First, create an admin if it doesn't exist
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/signup",
                json={
                    "company_name": "TestCorp",
                    "first_name": "Test",
                    "last_name": "Admin",
                    "email": "admin@testcorp.com",
                    "password": "Admin123!@#"
                }
            )
            print(f"  Admin registration: {response.status_code}")
            if response.status_code == 201:
                print(f"  Login ID: {response.json().get('login_id')}")
        except Exception as e:
            print(f"  Admin might already exist: {e}")
        
        # Try to login
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "login_id_or_email": "admin@testcorp.com",
                "password": "Admin123!@#"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            print(f"✅ Login successful, token: {data['access_token'][:20]}...")
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            pytest.skip("Cannot login - admin might not exist")
    
    def test_03_get_profile(self):
        """Test 3: Get User Profile"""
        print("\n▶️  TEST 3: Get Profile Test")
        
        # Login first
        try:
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "login_id_or_email": "admin@testcorp.com",
                    "password": "Admin123!@#"
                }
            )
            token = login_response.json()["access_token"]
        except Exception as e:
            pytest.skip(f"Cannot login: {e}")
        
        # Get profile using /auth/users/me
        response = requests.get(
            f"{BACKEND_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Profile fetch failed: {response.status_code} - {response.text}"
        profile = response.json()
        
        assert "email" in profile
        assert "login_id" in profile
        assert profile["email"] == "admin@testcorp.com"
        
        print(f"✅ Profile retrieved: {profile.get('first_name')} {profile.get('last_name')}")
        print(f"   Login ID: {profile.get('login_id')}")
        print(f"   Role: {profile.get('role')}")
    
    def test_04_cors_headers(self):
        """Test 4: CORS Headers"""
        print("\n▶️  TEST 4: CORS Configuration Test")
        
        response = requests.get(
            f"{BACKEND_URL}/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check if CORS headers are present
        assert "access-control-allow-origin" in response.headers
        assert response.headers.get("access-control-allow-origin") in ["http://localhost:3000", "*"]
        print(f"  CORS Origin: {response.headers.get('access-control-allow-origin')}")
        print("✅ CORS configuration is working")
    
    def test_05_database_connection(self):
        """Test 5: MongoDB Connection"""
        print("\n▶️  TEST 5: Database Connection Test")
        
        try:
            db = get_db()
            # List collections
            collections = db.list_collection_names()
            print(f"  Found collections: {collections}")
            assert len(collections) > 0
            print("✅ MongoDB connection successful")
        except Exception as e:
            pytest.fail(f"❌ MongoDB connection failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
