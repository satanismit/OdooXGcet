"""
Comprehensive Test Suite for All 3 Phases of Dayflow HRMS
Tests Phase 1 (Auth), Phase 2 (Attendance), Phase 3 (Salary) together
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import date, datetime, timedelta
from main import app
from models import User, Attendance, Leave, SalaryStructure
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import settings


@pytest.fixture(scope="function")
async def async_client():
    """Create async test client with database setup."""
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[f"{settings.DATABASE_NAME}_test_full_system"]
    
    # Initialize Beanie with all models
    await init_beanie(
        database=database,
        document_models=[User, Attendance, Leave, SalaryStructure]
    )
    
    # Clear all collections before each test
    await User.delete_all()
    await Attendance.delete_all()
    await Leave.delete_all()
    await SalaryStructure.delete_all()
    
    # Create test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Cleanup after test
    await User.delete_all()
    await Attendance.delete_all()
    await Leave.delete_all()
    await SalaryStructure.delete_all()
    client.close()


# ==================== FULL SYSTEM INTEGRATION TEST ====================

@pytest.mark.asyncio
async def test_full_system_flow(async_client):
    """
    Complete integration test covering all 3 phases:
    Phase 1: Authentication
    Phase 2: Attendance
    Phase 3: Salary Configuration
    """
    # ========== PHASE 1: AUTHENTICATION ==========
    print("\n=== Phase 1: Authentication ===")
    
    # Step 1: Create Admin
    admin_signup = await async_client.post("/auth/signup", json={
        "company_name": "Dayflow Inc",
        "email": "admin@dayflow.com",
        "password": "Admin@123",
        "first_name": "System",
        "last_name": "Administrator"
    })
    assert admin_signup.status_code == 201
    admin_data = admin_signup.json()
    admin_login_id = admin_data["login_id"]
    print(f"✓ Admin created: {admin_login_id}")
    
    # Step 2: Admin Login
    admin_login = await async_client.post("/auth/login", json={
        "login_id_or_email": "admin@dayflow.com",
        "password": "Admin@123"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    print(f"✓ Admin logged in successfully")
    
    # Step 3: Create Employee
    employee_create = await async_client.post("/admin/create-employee", 
        json={
            "email": "john.doe@dayflow.com",
            "first_name": "John",
            "last_name": "Doe",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert employee_create.status_code == 201
    employee_data = employee_create.json()
    employee_login_id = employee_data["login_id"]
    temp_password = employee_data["temporary_password"]
    print(f"✓ Employee created: {employee_login_id}")
    
    # Step 4: Employee Login
    employee_login = await async_client.post("/auth/login", json={
        "login_id_or_email": "john.doe@dayflow.com",
        "password": temp_password
    })
    assert employee_login.status_code == 200
    employee_token = employee_login.json()["access_token"]
    print(f"✓ Employee logged in successfully")
    
    # ========== PHASE 2: ATTENDANCE ==========
    print("\n=== Phase 2: Attendance ===")
    
    # Step 5: Employee checks in
    checkin_response = await async_client.post("/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert checkin_response.status_code == 200
    checkin_data = checkin_response.json()
    assert checkin_data["status"] == "PRESENT"
    print(f"✓ Employee checked in at {checkin_data['check_in_time']}")
    
    # Step 6: Verify Dashboard shows "Present" (Green)
    dashboard_response = await async_client.get("/dashboard/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert dashboard_response.status_code == 200
    employees = dashboard_response.json()
    john = next((e for e in employees if e["login_id"] == employee_login_id), None)
    assert john is not None
    assert john["status"] == "Green"
    assert john["status_label"] == "PRESENT"
    print(f"✓ Dashboard verified: {john['first_name']} is {john['status_label']}")
    
    # Step 7: Employee checks out
    checkout_response = await async_client.post("/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert checkout_response.status_code == 200
    checkout_data = checkout_response.json()
    assert "total_hours" in checkout_data
    print(f"✓ Employee checked out after {checkout_data['total_hours']} hours")
    
    # ========== PHASE 3: SALARY CONFIGURATION ==========
    print("\n=== Phase 3: Salary Configuration ===")
    
    # Step 8: RBAC Check - Employee tries to view their own salary (should fail)
    unauthorized_response = await async_client.get(
        f"/admin/salary/{employee_login_id}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert unauthorized_response.status_code == 403
    print("✓ RBAC verified: Employee cannot access salary endpoint (403 Forbidden)")
    
    # Step 9: Admin sets Employee wage to 50,000
    salary_config = await async_client.put(
        f"/admin/salary/{employee_login_id}",
        json={"monthly_wage": 50000.0, "working_days_per_week": 5},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert salary_config.status_code == 200
    salary_data = salary_config.json()
    print(f"✓ Salary configured: ₹{salary_data['monthly_wage']}/month")
    
    # Step 10: Verify Basic Salary == 25,000 (50% of wage)
    basic = next((c for c in salary_data["breakdown"] if c["name"] == "Basic Salary"), None)
    assert basic is not None
    assert basic["calculated_amount"] == 25000.0
    print(f"✓ Basic Salary verified: ₹{basic['calculated_amount']} (50% of wage)")
    
    # Step 11: Verify HRA == 12,500 (50% of Basic)
    hra = next((c for c in salary_data["breakdown"] if c["name"] == "House Rent Allowance"), None)
    assert hra is not None
    assert hra["calculated_amount"] == 12500.0
    print(f"✓ HRA verified: ₹{hra['calculated_amount']} (50% of Basic)")
    
    # Step 12: Verify Fixed Allowance matches the remainder exactly
    total_earnings = sum(c["calculated_amount"] for c in salary_data["breakdown"])
    assert abs(total_earnings - 50000.0) < 0.01
    print(f"✓ Total earnings verified: ₹{total_earnings} (exact match)")
    
    # Step 13: Verify Deductions
    assert salary_data["deductions"]["provident_fund"] == 3000.0  # 12% of Basic
    assert salary_data["deductions"]["professional_tax"] == 200.0  # Fixed
    print(f"✓ Deductions verified: PF=₹3000, PT=₹200")
    
    # Step 14: Math Integrity - Set messy wage (12,345.67)
    messy_wage_config = await async_client.put(
        f"/admin/salary/{employee_login_id}",
        json={"monthly_wage": 12345.67, "working_days_per_week": 5},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert messy_wage_config.status_code == 200
    messy_data = messy_wage_config.json()
    
    # Verify sum equals exactly 12,345.67
    messy_total = sum(c["calculated_amount"] for c in messy_data["breakdown"])
    assert abs(messy_total - 12345.67) < 0.01
    print(f"✓ Math integrity verified: Messy wage ₹12,345.67 = ₹{messy_total} (exact)")
    
    # Step 15: Update salary again (raise to 60,000)
    update_response = await async_client.put(
        f"/admin/salary/{employee_login_id}",
        json={"monthly_wage": 60000.0, "working_days_per_week": 5},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_response.status_code == 200
    
    # Verify it's an update, not a duplicate
    all_salaries = await SalaryStructure.find(
        SalaryStructure.user_id == employee_login_id
    ).to_list()
    assert len(all_salaries) == 1  # Should be only ONE record
    assert all_salaries[0].monthly_wage == 60000.0
    print(f"✓ Salary update verified: ₹60,000 (no duplicate record)")
    
    # Step 16: Verify yearly wage is calculated correctly
    assert update_response.json()["yearly_wage"] == 720000.0  # 60,000 * 12
    print(f"✓ Yearly wage verified: ₹{update_response.json()['yearly_wage']}")
    
    print("\n=== ✅ ALL PHASES TESTED SUCCESSFULLY ===\n")


# ==================== INDIVIDUAL PHASE 3 TESTS ====================

@pytest.mark.asyncio
async def test_salary_calculation_accuracy(async_client):
    """Test exact salary calculations with various wage amounts."""
    # Create admin and employee
    admin_signup = await async_client.post("/auth/signup", json={
        "company_name": "Test Co",
        "email": "admin@test.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "User"
    })
    admin_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "admin@test.com",
        "password": "Admin@123"
    })).json()["access_token"]
    
    employee_data = (await async_client.post("/admin/create-employee",
        json={
            "email": "employee@test.com",
            "first_name": "Test",
            "last_name": "Employee",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )).json()
    employee_id = employee_data["login_id"]
    
    # Test various wage amounts
    test_wages = [50000.0, 12345.67, 99999.99, 25000.0, 100000.0]
    
    for wage in test_wages:
        response = await async_client.put(
            f"/admin/salary/{employee_id}",
            json={"monthly_wage": wage},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify total equals wage exactly
        total = sum(c["calculated_amount"] for c in data["breakdown"])
        assert abs(total - wage) < 0.01, f"Failed for wage {wage}: {total} != {wage}"
        
        # Verify Basic is 50% of wage
        basic = next(c for c in data["breakdown"] if c["name"] == "Basic Salary")
        assert abs(basic["calculated_amount"] - (wage * 0.50)) < 0.01
        
        # Verify HRA is 50% of Basic
        hra = next(c for c in data["breakdown"] if c["name"] == "House Rent Allowance")
        assert abs(hra["calculated_amount"] - (basic["calculated_amount"] * 0.50)) < 0.01
        
        # Verify PF is 12% of Basic
        assert abs(data["deductions"]["provident_fund"] - (basic["calculated_amount"] * 0.12)) < 0.01
        
        print(f"✓ Wage ₹{wage}: All calculations accurate")


@pytest.mark.asyncio
async def test_employee_cannot_access_salary(async_client):
    """Test that regular employees cannot access salary endpoints."""
    # Create admin
    admin_token = (await async_client.post("/auth/signup", json={
        "company_name": "Test Co",
        "email": "admin2@test.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "Two"
    })).status_code
    
    admin_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "admin2@test.com",
        "password": "Admin@123"
    })).json()["access_token"]
    
    # Create two employees
    emp1_data = (await async_client.post("/admin/create-employee",
        json={
            "email": "emp1@test.com",
            "first_name": "Employee",
            "last_name": "One",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )).json()
    
    emp2_data = (await async_client.post("/admin/create-employee",
        json={
            "email": "emp2@test.com",
            "first_name": "Employee",
            "last_name": "Two",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )).json()
    
    # Login as Employee 1
    emp1_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "emp1@test.com",
        "password": emp1_data["temporary_password"]
    })).json()["access_token"]
    
    # Configure salary for Employee 2
    await async_client.put(
        f"/admin/salary/{emp2_data['login_id']}",
        json={"monthly_wage": 50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Employee 1 tries to view Employee 2's salary
    response = await async_client.get(
        f"/admin/salary/{emp2_data['login_id']}",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert response.status_code == 403
    
    # Employee 1 tries to view their own salary
    response = await async_client.get(
        f"/admin/salary/{emp1_data['login_id']}",
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert response.status_code == 403
    
    # Employee 1 tries to configure salary
    response = await async_client.put(
        f"/admin/salary/{emp1_data['login_id']}",
        json={"monthly_wage": 100000.0},
        headers={"Authorization": f"Bearer {emp1_token}"}
    )
    assert response.status_code == 403
    
    print("✓ All employee access attempts properly denied (403)")


@pytest.mark.asyncio
async def test_salary_components_formula(async_client):
    """Test that salary components follow exact formulas."""
    # Setup
    admin_token = (await async_client.post("/auth/signup", json={
        "company_name": "Formula Test",
        "email": "admin3@test.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "Three"
    })).status_code
    
    admin_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "admin3@test.com",
        "password": "Admin@123"
    })).json()["access_token"]
    
    emp_data = (await async_client.post("/admin/create-employee",
        json={
            "email": "formula@test.com",
            "first_name": "Formula",
            "last_name": "Test",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )).json()
    
    # Configure salary
    response = await async_client.put(
        f"/admin/salary/{emp_data['login_id']}",
        json={"monthly_wage": 50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Get components
    basic = next(c for c in data["breakdown"] if c["name"] == "Basic Salary")
    hra = next(c for c in data["breakdown"] if c["name"] == "House Rent Allowance")
    std_allow = next(c for c in data["breakdown"] if c["name"] == "Standard Allowance")
    perf_bonus = next(c for c in data["breakdown"] if c["name"] == "Performance Bonus")
    lta = next(c for c in data["breakdown"] if c["name"] == "Leave Travel Allowance")
    fixed_allow = next(c for c in data["breakdown"] if c["name"] == "Fixed Allowance")
    
    # Verify formulas
    assert basic["calculated_amount"] == 25000.0  # 50% of 50000
    assert hra["calculated_amount"] == 12500.0    # 50% of 25000
    assert std_allow["calculated_amount"] == 4167.0  # Fixed
    assert abs(perf_bonus["calculated_amount"] - 2082.5) < 0.01  # 8.33% of 25000
    assert abs(lta["calculated_amount"] - 2082.5) < 0.01  # 8.33% of 25000
    
    # Fixed Allowance should balance to exact total
    expected_fixed = 50000.0 - (25000.0 + 12500.0 + 4167.0 + 2082.5 + 2082.5)
    assert abs(fixed_allow["calculated_amount"] - expected_fixed) < 0.01
    
    # Verify deductions
    assert data["deductions"]["provident_fund"] == 3000.0  # 12% of 25000
    assert data["deductions"]["professional_tax"] == 200.0  # Fixed
    
    print("✓ All component formulas verified")


@pytest.mark.asyncio
async def test_negative_wage_rejected(async_client):
    """Test that negative wages are rejected."""
    # Setup
    admin_token = (await async_client.post("/auth/signup", json={
        "company_name": "Negative Test",
        "email": "admin4@test.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "Four"
    })).status_code
    
    admin_token = (await async_client.post("/auth/login", json={
        "login_id_or_email": "admin4@test.com",
        "password": "Admin@123"
    })).json()["access_token"]
    
    emp_data = (await async_client.post("/admin/create-employee",
        json={
            "email": "negative@test.com",
            "first_name": "Negative",
            "last_name": "Test",
            "joining_date": datetime.utcnow().isoformat()
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )).json()
    
    # Try to configure negative wage
    response = await async_client.put(
        f"/admin/salary/{emp_data['login_id']}",
        json={"monthly_wage": -50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422
    
    # Try zero wage
    response = await async_client.put(
        f"/admin/salary/{emp_data['login_id']}",
        json={"monthly_wage": 0.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422
    
    print("✓ Negative and zero wages properly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
