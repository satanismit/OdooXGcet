import pytest
import pytest_asyncio
from datetime import datetime
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from main import app
from models import User
from config import settings
from utils import extract_code, generate_login_id


# Test database configuration
TEST_DATABASE_NAME = "dayflow_hrms_test"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Set up a clean test database for each test."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[TEST_DATABASE_NAME]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[User])
    
    yield database
    
    # Clean up: Drop all collections after each test
    await database.users.delete_many({})
    client.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """Create an async HTTP client for testing."""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ========================
# Test Login ID Generation Logic
# ========================

class TestLoginIDGeneration:
    """Test the login ID generation utility functions."""
    
    def test_extract_code_normal(self):
        """Test extract_code with normal input."""
        assert extract_code("Ode", 2) == "OD"
        assert extract_code("John", 2) == "JO"
        assert extract_code("Doe", 2) == "DO"
    
    def test_extract_code_lowercase(self):
        """Test extract_code converts to uppercase."""
        assert extract_code("ode", 2) == "OD"
        assert extract_code("john", 2) == "JO"
    
    def test_extract_code_with_spaces(self):
        """Test extract_code handles spaces."""
        assert extract_code("O de", 2) == "OD"
        assert extract_code("J o hn", 2) == "JO"
    
    def test_extract_code_short_input(self):
        """Test extract_code pads short input with 'X'."""
        assert extract_code("A", 2) == "AX"
        assert extract_code("", 2) == "XX"
    
    def test_extract_code_with_numbers(self):
        """Test extract_code ignores numbers."""
        assert extract_code("A1B2C3", 2) == "AB"
        assert extract_code("123ABC", 2) == "AB"
    
    def test_extract_code_with_special_chars(self):
        """Test extract_code ignores special characters."""
        assert extract_code("A@B#C", 2) == "AB"
        assert extract_code("!@#$AB", 2) == "AB"
    
    @pytest.mark.asyncio
    async def test_generate_login_id_format(self, test_db):
        """Test that generated login ID follows the correct format."""
        login_id = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2022, 1, 15)
        )
        
        # Expected: ODJODO20220001
        assert login_id == "ODJODO20220001"
        assert len(login_id) == 14  # 2+2+2+4+4
    
    @pytest.mark.asyncio
    async def test_generate_login_id_incremental_serial(self, test_db):
        """Test that serial numbers increment correctly."""
        # Create first user
        login_id_1 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2026, 1, 15)
        )
        assert login_id_1 == "ODJODO20260001"
        
        # Save first user
        user1 = User(
            login_id=login_id_1,
            email="john.doe@ode.com",
            hashed_password="hashed",
            first_name="John",
            last_name="Doe",
            company_name="Ode",
            role="ADMIN",
            joining_date=datetime(2026, 1, 15)
        )
        await user1.insert()
        
        # Create second user with same prefix
        login_id_2 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2026, 2, 20)
        )
        assert login_id_2 == "ODJODO20260002"
        
        # Save second user
        user2 = User(
            login_id=login_id_2,
            email="john.doe2@ode.com",
            hashed_password="hashed",
            first_name="John",
            last_name="Doe",
            company_name="Ode",
            role="EMPLOYEE",
            joining_date=datetime(2026, 2, 20)
        )
        await user2.insert()
        
        # Create third user
        login_id_3 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2026, 3, 10)
        )
        assert login_id_3 == "ODJODO20260003"
    
    @pytest.mark.asyncio
    async def test_generate_login_id_different_years(self, test_db):
        """Test that serial numbers restart for different years."""
        # Create user for 2025
        login_id_2025 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2025, 1, 15)
        )
        assert login_id_2025 == "ODJODO20250001"
        
        user_2025 = User(
            login_id=login_id_2025,
            email="john.2025@ode.com",
            hashed_password="hashed",
            first_name="John",
            last_name="Doe",
            company_name="Ode",
            role="ADMIN",
            joining_date=datetime(2025, 1, 15)
        )
        await user_2025.insert()
        
        # Create user for 2026
        login_id_2026 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2026, 1, 15)
        )
        assert login_id_2026 == "ODJODO20260001"  # Serial resets for new year
    
    @pytest.mark.asyncio
    async def test_generate_login_id_different_names(self, test_db):
        """Test login IDs for different names in same year."""
        # User 1: John Doe
        login_id_1 = await generate_login_id(
            company_name="Ode",
            first_name="John",
            last_name="Doe",
            joining_date=datetime(2026, 1, 15)
        )
        assert login_id_1 == "ODJODO20260001"
        
        # User 2: Jane Smith (different name code)
        login_id_2 = await generate_login_id(
            company_name="Ode",
            first_name="Jane",
            last_name="Smith",
            joining_date=datetime(2026, 1, 15)
        )
        assert login_id_2 == "ODJASM20260001"  # Different prefix, serial starts at 1


# ========================
# Test Authentication Flow
# ========================

class TestAuthenticationFlow:
    """Test the complete authentication workflow."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client, test_db):
        """Test successful company admin signup."""
        response = await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["login_id"] == "ODJODO20260001"  # Assuming test runs in 2026
        assert data["email"] == "admin@ode.com"
        assert data["role"] == "ADMIN"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client, test_db):
        """Test signup with duplicate email fails."""
        # First signup
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Second signup with same email
        response = await client.post("/auth/signup", json={
            "company_name": "Another Company",
            "email": "admin@ode.com",
            "password": "DifferentPass456",
            "first_name": "Jane",
            "last_name": "Smith"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_with_login_id(self, client, test_db):
        """Test login using login_id."""
        # First, signup a user
        signup_response = await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        login_id = signup_response.json()["login_id"]
        
        # Login with login_id
        login_response = await client.post("/auth/login", json={
            "login_id_or_email": login_id,
            "password": "SecurePass123"
        })
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["login_id"] == login_id
        assert data["email"] == "admin@ode.com"
        assert data["role"] == "ADMIN"
    
    @pytest.mark.asyncio
    async def test_login_with_email(self, client, test_db):
        """Test login using email."""
        # Signup
        signup_response = await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        login_id = signup_response.json()["login_id"]
        
        # Login with email
        login_response = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["login_id"] == login_id
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_db):
        """Test login with wrong password fails."""
        # Signup
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login with wrong password
        response = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client, test_db):
        """Test login with nonexistent user fails."""
        response = await client.post("/auth/login", json={
            "login_id_or_email": "nonexistent@test.com",
            "password": "SomePassword"
        })
        
        assert response.status_code == 401


# ========================
# Test Employee Creation
# ========================

class TestEmployeeCreation:
    """Test employee onboarding by admin."""
    
    @pytest.mark.asyncio
    async def test_create_employee_success(self, client, test_db):
        """Test successful employee creation by admin."""
        # First, create admin
        signup_response = await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        token = login_response.json()["access_token"]
        
        # Create employee
        employee_response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert employee_response.status_code == 201
        data = employee_response.json()
        assert data["login_id"] == "ODJASM20260001"
        assert data["email"] == "jane.smith@ode.com"
        assert data["role"] == "EMPLOYEE"
        assert "temporary_password" in data
        assert len(data["temporary_password"]) > 0
    
    @pytest.mark.asyncio
    async def test_create_employee_serial_increment(self, client, test_db):
        """Test that employee serial numbers increment correctly."""
        # Create admin
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login as admin
        login_response = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        token = login_response.json()["access_token"]
        
        # Create first employee
        emp1_response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert emp1_response.json()["login_id"] == "ODJASM20260001"
        
        # Create second employee with same name
        emp2_response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith2@ode.com",
                "joining_date": "2026-02-20T00:00:00"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert emp2_response.json()["login_id"] == "ODJASM20260002"
    
    @pytest.mark.asyncio
    async def test_create_employee_without_auth(self, client, test_db):
        """Test that employee creation requires authentication."""
        response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            }
        )
        
        assert response.status_code == 401  # Unauthorized (no auth header)
    
    @pytest.mark.asyncio
    async def test_create_employee_as_employee_fails(self, client, test_db):
        """Test that only admins can create employees."""
        # Create admin
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login as admin
        admin_login = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        admin_token = admin_login.json()["access_token"]
        
        # Create an employee
        emp_response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        temp_password = emp_response.json()["temporary_password"]
        
        # Login as employee
        emp_login = await client.post("/auth/login", json={
            "login_id_or_email": "jane.smith@ode.com",
            "password": temp_password
        })
        emp_token = emp_login.json()["access_token"]
        
        # Try to create another employee as employee (should fail)
        response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Bob",
                "last_name": "Jones",
                "email": "bob.jones@ode.com",
                "joining_date": "2026-01-20T00:00:00"
            },
            headers={"Authorization": f"Bearer {emp_token}"}
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_employee_can_login_with_generated_credentials(self, client, test_db):
        """Test that generated employee can login with auto-generated credentials."""
        # Create admin
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login as admin
        admin_login = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        admin_token = admin_login.json()["access_token"]
        
        # Create employee
        emp_response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        emp_data = emp_response.json()
        login_id = emp_data["login_id"]
        temp_password = emp_data["temporary_password"]
        
        # Employee logs in with generated login_id
        emp_login = await client.post("/auth/login", json={
            "login_id_or_email": login_id,
            "password": temp_password
        })
        
        assert emp_login.status_code == 200
        emp_login_data = emp_login.json()
        assert emp_login_data["login_id"] == login_id
        assert emp_login_data["role"] == "EMPLOYEE"


# ========================
# Test Edge Cases
# ========================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_short_names(self, test_db):
        """Test handling of names with fewer than 2 letters."""
        login_id = await generate_login_id(
            company_name="O",  # 1 letter
            first_name="A",    # 1 letter
            last_name="B",     # 1 letter
            joining_date=datetime(2026, 1, 15)
        )
        
        # Should pad with 'X'
        assert login_id[:6] == "OXAXBX"
    
    @pytest.mark.asyncio
    async def test_names_with_spaces(self, test_db):
        """Test handling of names with spaces."""
        login_id = await generate_login_id(
            company_name="O de",
            first_name="Jo hn",
            last_name="Do e",
            joining_date=datetime(2026, 1, 15)
        )
        
        # Spaces should be removed
        assert login_id[:6] == "ODJODO"
    
    @pytest.mark.asyncio
    async def test_names_with_numbers(self, test_db):
        """Test handling of names with numbers."""
        login_id = await generate_login_id(
            company_name="Ode123",
            first_name="John456",
            last_name="Doe789",
            joining_date=datetime(2026, 1, 15)
        )
        
        # Numbers should be removed
        assert login_id[:6] == "ODJODO"
    
    @pytest.mark.asyncio
    async def test_duplicate_email_error(self, client, test_db):
        """Test proper error when creating employee with duplicate email."""
        # Create admin
        await client.post("/auth/signup", json={
            "company_name": "Ode",
            "email": "admin@ode.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        # Login
        login_response = await client.post("/auth/login", json={
            "login_id_or_email": "admin@ode.com",
            "password": "SecurePass123"
        })
        token = login_response.json()["access_token"]
        
        # Create first employee
        await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@ode.com",
                "joining_date": "2026-01-15T00:00:00"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to create another employee with same email
        response = await client.post(
            "/admin/create-employee",
            json={
                "first_name": "Bob",
                "last_name": "Jones",
                "email": "jane@ode.com",  # Same email
                "joining_date": "2026-01-20T00:00:00"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
