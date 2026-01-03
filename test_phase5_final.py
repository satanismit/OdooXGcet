"""
Phase 5 Final Test Suite: Attendance Analytics & Payslip Logic
This is the ULTIMATE test that integrates all phases together
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, date, timedelta
from main import app
from models import User, Attendance, Leave, SalaryStructure, Payslip
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import settings


@pytest.fixture(scope="function")
async def async_client():
    """Create async test client with database setup."""
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[f"{settings.DATABASE_NAME}_test_phase5"]
    
    # Initialize Beanie with all models
    await init_beanie(
        database=database,
        document_models=[User, Attendance, Leave, SalaryStructure, Payslip]
    )
    
    # Clear all collections before each test
    await User.delete_all()
    await Attendance.delete_all()
    await Leave.delete_all()
    await SalaryStructure.delete_all()
    await Payslip.delete_all()
    
    # Create test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Cleanup after test
    await User.delete_all()
    await Attendance.delete_all()
    await Leave.delete_all()
    await SalaryStructure.delete_all()
    await Payslip.delete_all()
    client.close()


async def create_admin_and_login(client: AsyncClient):
    """Helper: Create admin user and return token."""
    signup_response = await client.post("/auth/signup", json={
        "company_name": "Dayflow Corp",
        "email": "admin@dayflow.com",
        "password": "Admin@123",
        "first_name": "Admin",
        "last_name": "User"
    })
    assert signup_response.status_code == 201
    
    login_response = await client.post("/auth/login", json={
        "login_id_or_email": "admin@dayflow.com",
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


# ==================== THE ULTIMATE INTEGRATION TEST ====================

@pytest.mark.asyncio
async def test_full_payroll_system_integration(async_client):
    """
    THE ULTIMATE TEST - Integrates all 5 phases:
    Phase 1: Authentication
    Phase 2: Attendance
    Phase 3: Salary Configuration
    Phase 4: Profile Management
    Phase 5: Analytics & Payslip Generation
    
    Scenario:
    - Create user with 60,000/month salary (2,000/day based on 30-day month)
    - Simulate 3 days: Day 1 & 2 present, Day 3 absent
    - Verify analytics show 2 present days
    - Generate payslip and verify net salary = 4,000 (2 days * 2,000)
    """
    print("\n" + "="*70)
    print("🚀 ULTIMATE INTEGRATION TEST - ALL 5 PHASES")
    print("="*70)
    
    # ========== PHASE 1: AUTHENTICATION ==========
    print("\n=== Phase 1: Authentication ===")
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "employee@dayflow.com", "John", "Doe"
    )
    print(f"✓ Admin & Employee created and authenticated")
    print(f"✓ Employee ID: {login_id}")
    
    # ========== PHASE 3: SALARY CONFIGURATION ==========
    print("\n=== Phase 3: Salary Configuration ===")
    salary_response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 60000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert salary_response.status_code == 200
    print(f"✓ Salary configured: ₹60,000/month (₹2,000/day)")
    
    # ========== PHASE 2: ATTENDANCE SIMULATION ==========
    print("\n=== Phase 2: Attendance Tracking ===")
    
    # Get current month for testing
    now = datetime.utcnow()
    current_month = now.strftime("%m-%Y")
    
    # Day 1: Check In/Out (Present)
    day1_checkin = await async_client.post("/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert day1_checkin.status_code == 200
    day1_checkout = await async_client.post("/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert day1_checkout.status_code == 200
    print(f"✓ Day 1: Checked in and out (PRESENT)")
    
    # Simulate Day 2: Create another attendance record
    # We need to manually create a record for a different day
    user = await User.find_one(User.login_id == login_id)
    day2_date = now - timedelta(days=1)
    day2_attendance = Attendance(
        user_id=login_id,
        date=day2_date,
        check_in_time=day2_date.replace(hour=9, minute=0),
        check_out_time=day2_date.replace(hour=18, minute=0),
        status="PRESENT"
    )
    await day2_attendance.insert()
    print(f"✓ Day 2: Checked in and out (PRESENT)")
    
    # Day 3: No record (Absent)
    print(f"✓ Day 3: No attendance record (ABSENT)")
    
    # ========== PHASE 5: ANALYTICS CHECK ==========
    print("\n=== Phase 5: Attendance Analytics ===")
    stats_response = await async_client.get(
        f"/attendance/stats/me?month={current_month}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    
    print(f"✓ Analytics retrieved for month: {current_month}")
    print(f"  - Present Days: {stats_data['days_present']}")
    print(f"  - Leave Days: {stats_data['leave_count']}")
    print(f"  - Absent Days: {stats_data['absent_days']}")
    print(f"  - Total Working Days: {stats_data['total_working_days']}")
    
    # Assert present days == 2
    assert stats_data['days_present'] == 2, f"Expected 2 present days, got {stats_data['days_present']}"
    print(f"✓ VERIFIED: Present days = 2")
    
    # ========== PHASE 5: PAYROLL GENERATION ==========
    print("\n=== Phase 5: Payroll & Payslip Generation ===")
    payslip_response = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert payslip_response.status_code == 201
    payslip_data = payslip_response.json()
    
    print(f"✓ Payslip generated for {current_month}")
    print(f"  - Total Working Days: {payslip_data['total_working_days']}")
    print(f"  - Present Days: {payslip_data['present_days']}")
    print(f"  - Leave Days: {payslip_data['leave_days']}")
    print(f"  - Absent Days: {payslip_data['absent_days']}")
    print(f"  - Payable Days: {payslip_data['payable_days']}")
    print(f"  - Monthly Wage: ₹{payslip_data['monthly_wage']}")
    print(f"  - Daily Rate: ₹{payslip_data['daily_rate']}")
    print(f"  - Net Salary: ₹{payslip_data['net_salary']}")
    
    # Assert payable days == 2 (only present days, no leaves)
    assert payslip_data['payable_days'] == 2.0, f"Expected 2 payable days, got {payslip_data['payable_days']}"
    print(f"✓ VERIFIED: Payable Days = 2.0")
    
    # Assert net salary == 4,000 (2 days * 2,000/day)
    expected_net_salary = 4000.0
    assert payslip_data['net_salary'] == expected_net_salary, \
        f"Expected ₹{expected_net_salary}, got ₹{payslip_data['net_salary']}"
    print(f"✓ VERIFIED: Net Salary = ₹{expected_net_salary} (2 days × ₹2,000)")
    
    # Verify absent days correctly reduced salary
    full_month_salary = 60000.0
    salary_reduction = full_month_salary - expected_net_salary
    print(f"✓ VERIFIED: Salary reduced by ₹{salary_reduction} due to absences")
    
    print("\n" + "="*70)
    print("✅ ULTIMATE INTEGRATION TEST PASSED!")
    print("="*70)


@pytest.mark.asyncio
async def test_attendance_stats_endpoint(async_client):
    """Test attendance statistics endpoint."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "stats@test.com", "Stats", "User"
    )
    
    # Check in
    await async_client.post("/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # Get stats
    current_month = datetime.utcnow().strftime("%m-%Y")
    response = await async_client.get(
        f"/attendance/stats/me?month={current_month}",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "days_present" in data
    assert "leave_count" in data
    assert "total_working_days" in data
    assert "extra_hours" in data
    print("✓ Attendance stats endpoint working")


@pytest.mark.asyncio
async def test_admin_attendance_list(async_client):
    """Test admin can view attendance list for specific date."""
    admin_token = await create_admin_and_login(async_client)
    login_id1, token1 = await create_employee_and_login(
        async_client, admin_token, "emp1@test.com", "Employee", "One"
    )
    login_id2, token2 = await create_employee_and_login(
        async_client, admin_token, "emp2@test.com", "Employee", "Two"
    )
    
    # Employee 1 checks in
    await async_client.post("/attendance/check-in",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # Employee 2 does not check in
    
    # Admin views attendance list
    today = datetime.utcnow().strftime("%Y-%m-%d")
    response = await async_client.get(
        f"/attendance/list?date={today}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Both employees in list
    
    # Find employee 1 and 2
    emp1_record = next((e for e in data if e["login_id"] == login_id1), None)
    emp2_record = next((e for e in data if e["login_id"] == login_id2), None)
    
    assert emp1_record is not None
    assert emp1_record["status"] == "PRESENT"
    assert emp1_record["check_in_time"] is not None
    
    assert emp2_record is not None
    assert emp2_record["status"] == "ABSENT"
    assert emp2_record["check_in_time"] is None
    
    print("✓ Admin attendance list working correctly")


@pytest.mark.asyncio
async def test_payslip_with_leaves(async_client):
    """Test payslip calculation includes approved leaves as paid days."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "leave@test.com", "Leave", "Tester"
    )
    
    # Configure salary: 30,000/month (1,000/day)
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 30000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Simulate attendance for 3 days in current month
    user = await User.find_one(User.login_id == login_id)
    now = datetime.utcnow()
    current_month = now.strftime("%m-%Y")
    
    # Create 3 attendance records
    for i in range(3):
        day_date = now - timedelta(days=i)
        attendance = Attendance(
            user_id=login_id,
            date=day_date,
            check_in_time=day_date.replace(hour=9),
            check_out_time=day_date.replace(hour=18),
            status="PRESENT"
        )
        await attendance.insert()
    
    # Apply for 2 days leave within current month
    # Make leave dates within this month
    leave_start = now.replace(day=min(now.day + 1, 28))  # Next day or day 28
    leave_end = leave_start + timedelta(days=1)
    
    leave_response = await async_client.post("/leave/apply",
        json={
            "start_date": leave_start.date().isoformat(),
            "end_date": leave_end.date().isoformat(),
            "reason": "Personal"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    leave_id = leave_response.json()["leave_id"]
    
    # Admin approves leave
    await async_client.post(f"/leave/approve/{leave_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Generate payslip
    payslip_response = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert payslip_response.status_code == 201
    payslip = payslip_response.json()
    
    # Should have 3 present days + 2 leave days = 5 payable days
    assert payslip["present_days"] == 3, f"Expected 3 present days, got {payslip['present_days']}"
    assert payslip["leave_days"] == 2, f"Expected 2 leave days, got {payslip['leave_days']}"
    assert payslip["payable_days"] == 5.0, f"Expected 5.0 payable days, got {payslip['payable_days']}"
    
    # Net salary should be 5,000 (5 days * 1,000/day)
    expected_salary = 5000.0
    assert payslip["net_salary"] == expected_salary, f"Expected ₹{expected_salary}, got ₹{payslip['net_salary']}"
    
    print(f"✓ Payslip with leaves: {payslip['present_days']} present + {payslip['leave_days']} leave = ₹{payslip['net_salary']}")


@pytest.mark.asyncio
async def test_payslip_update_not_duplicate(async_client):
    """Test that regenerating payslip updates existing record instead of creating duplicate."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "update@test.com", "Update", "Test"
    )
    
    # Configure salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Generate payslip first time
    current_month = datetime.utcnow().strftime("%m-%Y")
    response1 = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response1.status_code == 201
    
    # Add some attendance
    await async_client.post("/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    await async_client.post("/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    # Regenerate payslip
    response2 = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response2.status_code == 201
    
    # Should be same payslip ID (updated, not new)
    assert response1.json()["payslip_id"] == response2.json()["payslip_id"]
    
    # Verify only one payslip exists in database
    all_payslips = await Payslip.find(Payslip.user_id == login_id).to_list()
    assert len(all_payslips) == 1
    
    print("✓ Payslip update verified (no duplicates)")


@pytest.mark.asyncio
async def test_employee_cannot_generate_payslip(async_client):
    """Test that employees cannot generate payslips (admin only)."""
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "noauth@test.com", "No", "Auth"
    )
    
    # Configure salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 40000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Employee tries to generate their own payslip
    current_month = datetime.utcnow().strftime("%m-%Y")
    response = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {employee_token}"}  # Employee token
    )
    
    assert response.status_code == 403
    print("✓ Employee correctly denied payslip generation (403)")


@pytest.mark.asyncio
async def test_invalid_month_format(async_client):
    """Test that invalid month format is rejected."""
    admin_token = await create_admin_and_login(async_client)
    login_id, _ = await create_employee_and_login(
        async_client, admin_token, "invalid@test.com", "Invalid", "Month"
    )
    
    # Configure salary
    await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 50000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Try invalid month format
    response = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": "2026-01"},  # Wrong format (should be MM-YYYY)
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()
    print("✓ Invalid month format correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
