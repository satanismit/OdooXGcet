import pytest
from httpx import AsyncClient, ASGITransport
from datetime import date, timedelta
from decimal import Decimal
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
    database = client[f"{settings.DATABASE_NAME}_test_phase2"]
    
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


async def create_admin_and_login(client: AsyncClient):
    """Helper to create admin and get auth token."""
    admin_data = {
        "company_name": "Dayflow",
        "email": "admin@dayflow.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    signup_response = await client.post("/auth/signup", json=admin_data)
    assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
    
    login_response = await client.post(
        "/auth/login",
        json={"login_id_or_email": "admin@dayflow.com", "password": "Admin@123"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    return login_response.json()["access_token"]


async def create_employee_and_login(client: AsyncClient, admin_token: str, email: str, first_name: str, last_name: str):
    """Helper to create employee and get auth token."""
    from datetime import datetime
    
    employee_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "joining_date": datetime.utcnow().isoformat()
    }
    
    response = await client.post(
        "/admin/create-employee",
        json=employee_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201, f"Employee creation failed: {response.text}"
    
    login_id = response.json()["login_id"]
    temp_password = response.json()["temporary_password"]
    
    login_response = await client.post(
        "/auth/login",
        json={"login_id_or_email": email, "password": temp_password}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    return login_id, login_response.json()["access_token"]


# ==================== ATTENDANCE TESTS ====================

@pytest.mark.asyncio
async def test_check_in_success(async_client):
    """Test successful check-in."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "john@dayflow.com", "John", "Doe"
    )
    
    response = await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Checked in successfully"
    assert data["user_id"] == login_id
    assert data["status"] == "PRESENT"
    assert "check_in_time" in data


@pytest.mark.asyncio
async def test_double_check_in_fails(async_client):
    """Test that checking in twice on the same day returns 400 error."""
    admin_token = await create_admin_and_login(async_client)
    _, employee_token = await create_employee_and_login(
        async_client, admin_token, "jane@dayflow.com", "Jane", "Smith"
    )
    
    # First check-in should succeed
    response1 = await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response1.status_code == 200
    
    # Second check-in should fail
    response2 = await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response2.status_code == 400
    assert "Already checked in today" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_ghost_check_out_fails(async_client):
    """Test that checking out without checking in returns 400 error."""
    admin_token = await create_admin_and_login(async_client)
    _, employee_token = await create_employee_and_login(
        async_client, admin_token, "ghost@dayflow.com", "Ghost", "User"
    )
    
    # Try to check out without checking in
    response = await async_client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 400
    assert "Cannot check out without checking in first" in response.json()["detail"]


@pytest.mark.asyncio
async def test_check_in_and_check_out(async_client):
    """Test successful check-in and check-out flow."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "worker@dayflow.com", "Hard", "Worker"
    )
    
    # Check in
    checkin_response = await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert checkin_response.status_code == 200
    
    # Check out
    checkout_response = await async_client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert checkout_response.status_code == 200
    data = checkout_response.json()
    assert data["message"] == "Checked out successfully"
    assert data["user_id"] == login_id
    assert "total_hours" in data
    assert data["total_hours"] >= 0


@pytest.mark.asyncio
async def test_double_check_out_fails(async_client):
    """Test that checking out twice fails."""
    admin_token = await create_admin_and_login(async_client)
    _, employee_token = await create_employee_and_login(
        async_client, admin_token, "double@dayflow.com", "Double", "Checkout"
    )
    
    # Check in
    await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # First check-out
    response1 = await async_client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response1.status_code == 200
    
    # Second check-out should fail
    response2 = await async_client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response2.status_code == 400
    assert "Already checked out today" in response2.json()["detail"]


# ==================== SALARY CONFIGURATION TESTS ====================

@pytest.mark.asyncio
async def test_salary_configuration_success(async_client):
    """Test successful salary configuration by admin."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "salaried@dayflow.com", "Salary", "Person"
    )
    
    response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == login_id
    assert data["monthly_wage"] == 50000.0
    assert len(data["breakdown"]) == 6
    assert "deductions" in data


@pytest.mark.asyncio
async def test_salary_math_integrity_weird_wage(async_client):
    """Test that salary components sum exactly to total wage (weird amount)."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "weird@dayflow.com", "Weird", "Wage"
    )
    
    # Use a weird wage amount
    weird_wage = 50001.55
    
    response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": weird_wage},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Calculate sum of components
    total_from_components = sum(comp["calculated_amount"] for comp in data["breakdown"])
    
    # Assert exact match (no rounding errors)
    assert abs(total_from_components - weird_wage) < 0.01
    assert abs(data["monthly_wage"] - weird_wage) < 0.01


@pytest.mark.asyncio
async def test_negative_salary_fails(async_client):
    """Test that configuring a negative wage fails with validation error."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "negative@dayflow.com", "Negative", "Salary"
    )
    
    response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": -50000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Pydantic validation returns 422
    assert response.status_code == 422
    assert "greater than 0" in response.json()["detail"][0]["msg"].lower() or "positive" in response.json()["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_zero_salary_fails(async_client):
    """Test that configuring zero wage fails."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "zero@dayflow.com", "Zero", "Salary"
    )
    
    response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Pydantic validation returns 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_salary_components_breakdown(async_client):
    """Test that salary components are calculated correctly."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "breakdown@dayflow.com", "Break", "Down"
    )
    
    monthly_wage = 100000
    
    response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": monthly_wage},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all components exist
    component_names = {comp["name"] for comp in data["breakdown"]}
    assert "Basic Salary" in component_names
    assert "House Rent Allowance" in component_names
    
    # Verify Basic Salary is exactly 50% of total
    basic = next(c["calculated_amount"] for c in data["breakdown"] if c["name"] == "Basic Salary")
    assert abs(basic - monthly_wage * 0.5) < 1


@pytest.mark.asyncio
async def test_unauthorized_salary_access(async_client):
    """Test that Employee A cannot view Employee B's salary (403 Forbidden)."""
    admin_token = await create_admin_and_login(async_client)
    
    # Create Employee A
    login_id_a, token_a = await create_employee_and_login(
        async_client, admin_token, "employeeA@dayflow.com", "Employee", "A"
    )
    
    # Create Employee B
    login_id_b, token_b = await create_employee_and_login(
        async_client, admin_token, "employeeB@dayflow.com", "Employee", "B"
    )
    
    # Configure salary for Employee B
    await async_client.put(
        f"/admin/salary/{login_id_b}",
        json={"monthly_wage": 60000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Employee A tries to view Employee B's salary
    response = await async_client.get(
        f"/admin/salary/{login_id_b}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_employee_can_view_own_salary(async_client):
    """Test that employee CANNOT view their own salary (Phase 3: Admin Only)."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "ownsal@dayflow.com", "Own", "Salary"
    )
    
    # Admin configures salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 75000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Employee tries to view their own salary - should fail (Phase 3: Admin Only)
    response = await async_client.get(
        f"/admin/salary/{login_id}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_can_view_any_salary(async_client):
    """Test that admin can view any employee's salary."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "anysal@dayflow.com", "Any", "Salary"
    )
    
    # Configure salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 80000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Admin views employee's salary
    response = await async_client.get(
        f"/admin/salary/{login_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["user_id"] == login_id


# ==================== LEAVE MANAGEMENT TESTS ====================

@pytest.mark.asyncio
async def test_apply_leave_success(async_client):
    """Test successful leave application."""
    admin_token = await create_admin_and_login(async_client)
    _, employee_token = await create_employee_and_login(
        async_client, admin_token, "leavereq@dayflow.com", "Leave", "Requester"
    )
    
    tomorrow = date.today() + timedelta(days=1)
    next_week = tomorrow + timedelta(days=7)
    
    response = await async_client.post(
        "/leave/apply",
        json={
            "start_date": tomorrow.isoformat(),
            "end_date": next_week.isoformat(),
            "reason": "Vacation"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Leave request submitted successfully"
    assert data["status"] == "PENDING"
    assert "leave_id" in data


@pytest.mark.asyncio
async def test_approve_leave_by_admin(async_client):
    """Test that admin can approve leave requests."""
    admin_token = await create_admin_and_login(async_client)
    _, employee_token = await create_employee_and_login(
        async_client, admin_token, "approve@dayflow.com", "Approve", "Leave"
    )
    
    # Apply for leave
    tomorrow = date.today() + timedelta(days=1)
    apply_response = await async_client.post(
        "/leave/apply",
        json={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
            "reason": "Medical"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    leave_id = apply_response.json()["leave_id"]
    
    # Admin approves leave
    approve_response = await async_client.post(
        f"/leave/approve/{leave_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert approve_response.status_code == 200
    data = approve_response.json()
    assert data["message"] == "Leave approved successfully"
    assert data["status"] == "APPROVED"


# ==================== DASHBOARD STATUS TESTS ====================

@pytest.mark.asyncio
async def test_dashboard_status_present(async_client):
    """Test that checked-in user shows Green (PRESENT) status."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "present@dayflow.com", "Present", "User"
    )
    
    # Check in
    await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # Get dashboard
    dashboard_response = await async_client.get(
        "/dashboard/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert dashboard_response.status_code == 200
    employees = dashboard_response.json()
    
    # Find the checked-in user
    user_status = next((e for e in employees if e["login_id"] == login_id), None)
    assert user_status is not None
    assert user_status["status"] == "Green"
    assert user_status["status_label"] == "PRESENT"


@pytest.mark.asyncio
async def test_dashboard_status_on_leave(async_client):
    """Test that user with approved leave shows Airplane (LEAVE) status."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "onleave@dayflow.com", "On", "Leave"
    )
    
    # Apply for leave today
    today = date.today()
    apply_response = await async_client.post(
        "/leave/apply",
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "reason": "Sick leave"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    leave_id = apply_response.json()["leave_id"]
    
    # Admin approves leave
    await async_client.post(
        f"/leave/approve/{leave_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Get dashboard
    dashboard_response = await async_client.get(
        "/dashboard/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert dashboard_response.status_code == 200
    employees = dashboard_response.json()
    
    # Find the user on leave
    user_status = next((e for e in employees if e["login_id"] == login_id), None)
    assert user_status is not None
    assert user_status["status"] == "Airplane"
    assert user_status["status_label"] == "LEAVE"


@pytest.mark.asyncio
async def test_dashboard_status_absent(async_client):
    """Test that user who hasn't checked in shows Yellow (ABSENT) status."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "absent@dayflow.com", "Absent", "User"
    )
    
    # Don't check in or apply for leave
    
    # Get dashboard
    dashboard_response = await async_client.get(
        "/dashboard/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert dashboard_response.status_code == 200
    employees = dashboard_response.json()
    
    # Find the absent user
    user_status = next((e for e in employees if e["login_id"] == login_id), None)
    assert user_status is not None
    assert user_status["status"] == "Yellow"
    assert user_status["status_label"] == "ABSENT"


@pytest.mark.asyncio
async def test_dashboard_search_by_name(async_client):
    """Test dashboard search functionality."""
    admin_token = await create_admin_and_login(async_client)
    
    # Create multiple employees
    await create_employee_and_login(async_client, admin_token, "alice@dayflow.com", "Alice", "Anderson")
    await create_employee_and_login(async_client, admin_token, "bob@dayflow.com", "Bob", "Brown")
    await create_employee_and_login(async_client, admin_token, "charlie@dayflow.com", "Charlie", "Chen")
    
    # Search for "Alice"
    response = await async_client.get(
        "/dashboard/employees?search=Alice",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 1
    assert employees[0]["first_name"] == "Alice"


# ==================== INTEGRATION TESTS ====================

@pytest.mark.asyncio
async def test_complete_employee_workflow(async_client):
    """Test complete workflow: create employee, configure salary, check-in, apply leave."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "complete@dayflow.com", "Complete", "Workflow"
    )
    
    # 1. Configure salary
    salary_response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 55000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert salary_response.status_code == 200
    
    # 2. Check in
    checkin_response = await async_client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert checkin_response.status_code == 200
    
    # 3. Apply for leave
    tomorrow = date.today() + timedelta(days=1)
    leave_response = await async_client.post(
        "/leave/apply",
        json={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
            "reason": "Personal"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert leave_response.status_code == 200
    
    # 4. Verify dashboard shows Green (PRESENT)
    dashboard_response = await async_client.get(
        "/dashboard/employees",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    employees = dashboard_response.json()
    user_status = next((e for e in employees if e["login_id"] == login_id), None)
    assert user_status["status"] == "Green"


@pytest.mark.asyncio
async def test_salary_update_workflow(async_client):
    """Test that salary can be updated and new values are reflected."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "update@dayflow.com", "Update", "Salary"
    )
    
    # Configure initial salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 50000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Update salary
    update_response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 60000},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_response.status_code == 200
    
    # Verify new salary (admin only)
    get_response = await async_client.get(
        f"/admin/salary/{login_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.json()["monthly_wage"] == 60000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
