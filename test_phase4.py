"""
Phase 4 Test Suite: Profile Management (Private Info & Security)
Tests for personal details, bank details, password change, and privacy controls
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime
from main import app
from models import User, PersonalDetails, BankDetails
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import settings


@pytest.fixture(scope="function")
async def async_client():
    """Create async test client with database setup."""
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[f"{settings.DATABASE_NAME}_test_phase4"]
    
    # Initialize Beanie with all models
    await init_beanie(
        database=database,
        document_models=[User]
    )
    
    # Clear all collections before each test
    await User.delete_all()
    
    # Create test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Cleanup after test
    await User.delete_all()
    client.close()


async def create_admin_and_login(client: AsyncClient):
    """Helper: Create admin user and return token."""
    signup_response = await client.post("/auth/signup", json={
        "company_name": "Test Corp",
        "email": "admin@test.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "User"
    })
    assert signup_response.status_code == 201
    
    login_response = await client.post("/auth/login", json={
        "login_id_or_email": "admin@test.com",
        "password": "Admin@123"
    })
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


async def create_employee_and_login(client: AsyncClient, admin_token: str, email: str, first: str, last: str):
    """Helper: Create employee and return (login_id, token)."""
    create_response = await client.post("/admin/create-employee",
        json={
            "email": email,
            "first_name": first,
            "last_name": last,
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_response.status_code == 201
    employee_data = create_response.json()
    
    login_response = await client.post("/auth/login", json={
        "login_id_or_email": email,
        "password": employee_data["temporary_password"]
    })
    assert login_response.status_code == 200
    
    return employee_data["login_id"], login_response.json()["access_token"]


# ==================== PRIVATE INFO TESTS ====================

@pytest.mark.asyncio
async def test_update_personal_details_success(async_client):
    """Test successful update of personal details."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp1@test.com", "John", "Doe"
    )
    
    # Update personal details
    response = await async_client.patch("/users/me/private-info",
        json={
            "personal_details": {
                "date_of_birth": "1990-05-15",
                "gender": "Male",
                "marital_status": "Single",
                "current_address": "123 Main St, Mumbai",
                "personal_email": "john.personal@gmail.com"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Private information updated successfully"
    assert data["personal_details"]["gender"] == "Male"
    assert data["personal_details"]["date_of_birth"] == "1990-05-15"
    print("✓ Personal details updated successfully")


@pytest.mark.asyncio
async def test_update_bank_details_success(async_client):
    """Test successful update of bank details."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp2@test.com", "Jane", "Smith"
    )
    
    # Update bank details
    response = await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "bank_name": "HDFC Bank",
                "account_number": "12345678901234",
                "ifsc_code": "HDFC0001234",
                "pan_number": "ABCDE1234F",
                "uan_number": "123456789012"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["bank_details"]["bank_name"] == "HDFC Bank"
    assert data["bank_details"]["pan_number"] == "ABCDE1234F"
    print("✓ Bank details updated successfully")


@pytest.mark.asyncio
async def test_data_persistence_bank_details(async_client):
    """Test that bank details persist correctly (GET after UPDATE)."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp3@test.com", "Bob", "Johnson"
    )
    
    # Update bank details
    update_response = await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "bank_name": "ICICI Bank",
                "account_number": "98765432109876",
                "ifsc_code": "ICIC0009876",
                "pan_number": "PQRST5678U",
                "uan_number": "987654321098"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert update_response.status_code == 200
    
    # Retrieve full profile
    get_response = await async_client.get(f"/users/{login_id}/full-profile",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert get_response.status_code == 200
    
    profile_data = get_response.json()
    assert profile_data["bank_details"]["bank_name"] == "ICICI Bank"
    assert profile_data["bank_details"]["account_number"] == "98765432109876"
    assert profile_data["bank_details"]["ifsc_code"] == "ICIC0009876"
    assert profile_data["bank_details"]["pan_number"] == "PQRST5678U"
    print("✓ Data persistence verified: Bank details saved and retrieved correctly")


@pytest.mark.asyncio
async def test_update_both_personal_and_bank_details(async_client):
    """Test updating both personal and bank details simultaneously."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp4@test.com", "Alice", "Brown"
    )
    
    response = await async_client.patch("/users/me/private-info",
        json={
            "personal_details": {
                "date_of_birth": "1985-12-01",
                "gender": "Female",
                "marital_status": "Married",
                "current_address": "456 Park Ave, Delhi",
                "personal_email": "alice.brown@gmail.com"
            },
            "bank_details": {
                "bank_name": "SBI",
                "account_number": "11223344556677",
                "ifsc_code": "SBIN0001122",
                "pan_number": "XYZAB9876C",
                "uan_number": "111222333444"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["personal_details"]["gender"] == "Female"
    assert data["bank_details"]["bank_name"] == "SBI"
    print("✓ Both personal and bank details updated successfully")


@pytest.mark.asyncio
async def test_invalid_pan_number_validation(async_client):
    """Test that invalid PAN number is rejected."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp5@test.com", "Invalid", "PAN"
    )
    
    response = await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "pan_number": "INVALID123"  # Invalid format
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 422  # Validation error
    print("✓ Invalid PAN number rejected")


@pytest.mark.asyncio
async def test_invalid_ifsc_code_validation(async_client):
    """Test that invalid IFSC code is rejected."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp6@test.com", "Invalid", "IFSC"
    )
    
    response = await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "ifsc_code": "HDFC1234567"  # Invalid format (should have 0 in 5th position)
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 422  # Validation error
    print("✓ Invalid IFSC code rejected")


# ==================== PASSWORD CHANGE TESTS ====================

@pytest.mark.asyncio
async def test_change_password_wrong_current_password(async_client):
    """Test password change fails with wrong current password."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp7@test.com", "Password", "Test"
    )
    
    response = await async_client.post("/users/me/change-password",
        json={
            "current_password": "WrongPassword123",  # Incorrect
            "new_password": "NewSecurePass456",
            "confirm_new_password": "NewSecurePass456"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()
    print("✓ Password change rejected with wrong current password")


@pytest.mark.asyncio
async def test_change_password_mismatch_confirmation(async_client):
    """Test password change fails when new password doesn't match confirmation."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "emp8@test.com", "Mismatch", "Test"
    )
    
    # Get the temporary password from employee creation
    create_response = await async_client.post("/admin/create-employee",
        json={
            "email": "temp@test.com",
            "first_name": "Temp",
            "last_name": "User",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    temp_password = create_response.json()["temporary_password"]
    temp_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "temp@test.com",
        "password": temp_password
    })).json()["access_token"]
    
    response = await async_client.post("/users/me/change-password",
        json={
            "current_password": temp_password,
            "new_password": "NewSecurePass456",
            "confirm_new_password": "DifferentPass789"  # Mismatch
        },
        headers={"Authorization": f"Bearer {temp_token}"}
    )
    
    assert response.status_code == 400
    assert "do not match" in response.json()["detail"].lower()
    print("✓ Password change rejected when confirmation doesn't match")


@pytest.mark.asyncio
async def test_change_password_success_and_old_password_fails(async_client):
    """Test successful password change, then verify old password no longer works."""
    admin_token = await create_admin_and_login(async_client)
    
    # Create employee
    create_response = await async_client.post("/admin/create-employee",
        json={
            "email": "pwchange@test.com",
            "first_name": "Password",
            "last_name": "Changer",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    old_password = create_response.json()["temporary_password"]
    login_id = create_response.json()["login_id"]
    
    # Login with old password
    login_response = await async_client.post("/auth/login", json={
        "login_id_or_email": "pwchange@test.com",
        "password": old_password
    })
    assert login_response.status_code == 200
    employee_token = login_response.json()["access_token"]
    
    # Change password
    change_response = await async_client.post("/users/me/change-password",
        json={
            "current_password": old_password,
            "new_password": "NewSecurePassword789",
            "confirm_new_password": "NewSecurePassword789"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert change_response.status_code == 200
    assert "successfully" in change_response.json()["message"].lower()
    print("✓ Password changed successfully")
    
    # Try to login with old password (should fail)
    old_login_response = await async_client.post("/auth/login", json={
        "login_id_or_email": "pwchange@test.com",
        "password": old_password
    })
    assert old_login_response.status_code == 401
    print("✓ Old password no longer works")
    
    # Login with new password (should succeed)
    new_login_response = await async_client.post("/auth/login", json={
        "login_id_or_email": "pwchange@test.com",
        "password": "NewSecurePassword789"
    })
    assert new_login_response.status_code == 200
    assert "access_token" in new_login_response.json()
    print("✓ New password works correctly")


@pytest.mark.asyncio
async def test_change_password_same_as_current(async_client):
    """Test that new password cannot be the same as current password."""
    admin_token = await create_admin_and_login(async_client)
    
    create_response = await async_client.post("/admin/create-employee",
        json={
            "email": "samepass@test.com",
            "first_name": "Same",
            "last_name": "Password",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    temp_password = create_response.json()["temporary_password"]
    
    employee_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "samepass@test.com",
        "password": temp_password
    })).json()["access_token"]
    
    response = await async_client.post("/users/me/change-password",
        json={
            "current_password": temp_password,
            "new_password": temp_password,  # Same as current
            "confirm_new_password": temp_password
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()
    print("✓ Cannot change to same password")


# ==================== PRIVACY & RBAC TESTS ====================

@pytest.mark.asyncio
async def test_employee_cannot_view_other_employee_profile(async_client):
    """Test that Employee A cannot view Employee B's full profile."""
    admin_token = await create_admin_and_login(async_client)
    
    # Create Employee A
    login_id_a, token_a = await create_employee_and_login(
        async_client, admin_token, "empA@test.com", "Employee", "A"
    )
    
    # Create Employee B and add private info
    login_id_b, token_b = await create_employee_and_login(
        async_client, admin_token, "empB@test.com", "Employee", "B"
    )
    
    await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "bank_name": "Secret Bank",
                "account_number": "99999999999999",
                "pan_number": "SECRT9999S"
            }
        },
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # Employee A tries to view Employee B's profile
    response = await async_client.get(f"/users/{login_id_b}/full-profile",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()
    print("✓ Employee A cannot view Employee B's profile (403 Forbidden)")


@pytest.mark.asyncio
async def test_employee_can_view_own_profile(async_client):
    """Test that employee can view their own full profile."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "ownprofile@test.com", "Own", "Profile"
    )
    
    # Add private info
    await async_client.patch("/users/me/private-info",
        json={
            "personal_details": {
                "gender": "Male",
                "marital_status": "Single"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # View own profile
    response = await async_client.get(f"/users/{login_id}/full-profile",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["login_id"] == login_id
    assert data["personal_details"]["gender"] == "Male"
    print("✓ Employee can view their own profile")


@pytest.mark.asyncio
async def test_admin_can_view_any_employee_profile(async_client):
    """Test that admin can view any employee's full profile."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "adminview@test.com", "Admin", "View"
    )
    
    # Employee adds private info
    await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "bank_name": "Employee Bank",
                "account_number": "11111111111111"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # Admin views employee profile
    response = await async_client.get(f"/users/{login_id}/full-profile",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["login_id"] == login_id
    assert data["bank_details"]["bank_name"] == "Employee Bank"
    print("✓ Admin can view any employee's profile")


@pytest.mark.asyncio
async def test_get_profile_nonexistent_user(async_client):
    """Test that getting profile for non-existent user returns 404."""
    admin_token = await create_admin_and_login(async_client)
    
    response = await async_client.get("/users/NONEXISTENT123/full-profile",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("✓ Non-existent user returns 404")


# ==================== COMPLETE WORKFLOW TEST ====================

@pytest.mark.asyncio
async def test_complete_profile_workflow(async_client):
    """Test complete workflow: create user, update profile, change password, verify access."""
    admin_token = await create_admin_and_login(async_client)
    
    # Step 1: Create employee
    create_response = await async_client.post("/admin/create-employee",
        json={
            "email": "workflow@test.com",
            "first_name": "Workflow",
            "last_name": "Test",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    temp_password = create_response.json()["temporary_password"]
    login_id = create_response.json()["login_id"]
    print(f"✓ Step 1: Employee created ({login_id})")
    
    # Step 2: Employee login
    employee_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "workflow@test.com",
        "password": temp_password
    })).json()["access_token"]
    print("✓ Step 2: Employee logged in")
    
    # Step 3: Update personal details
    await async_client.patch("/users/me/private-info",
        json={
            "personal_details": {
                "date_of_birth": "1995-03-20",
                "gender": "Other",
                "current_address": "789 Workflow St"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    print("✓ Step 3: Personal details updated")
    
    # Step 4: Update bank details
    await async_client.patch("/users/me/private-info",
        json={
            "bank_details": {
                "bank_name": "Workflow Bank",
                "account_number": "12341234123412",
                "ifsc_code": "WORK0001234",
                "pan_number": "WRKFL1234W"
            }
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    print("✓ Step 4: Bank details updated")
    
    # Step 5: Change password
    await async_client.post("/users/me/change-password",
        json={
            "current_password": temp_password,
            "new_password": "WorkflowNewPass123",
            "confirm_new_password": "WorkflowNewPass123"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    print("✓ Step 5: Password changed")
    
    # Step 6: Login with new password
    new_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "workflow@test.com",
        "password": "WorkflowNewPass123"
    })).json()["access_token"]
    print("✓ Step 6: Logged in with new password")
    
    # Step 7: Verify all data persisted
    profile = await async_client.get(f"/users/{login_id}/full-profile",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert profile.status_code == 200
    data = profile.json()
    assert data["personal_details"]["gender"] == "Other"
    assert data["bank_details"]["bank_name"] == "Workflow Bank"
    print("✓ Step 7: All data persisted correctly")
    
    # Step 8: Admin can also view the profile
    admin_view = await async_client.get(f"/users/{login_id}/full-profile",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_view.status_code == 200
    print("✓ Step 8: Admin verified profile access")
    
    print("\n✅ Complete workflow test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
