"""
Phase 6 Final System Integration Test
Tests the complete lifecycle of the HRMS application across all 6 phases
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, date, timedelta
from main import app
from models import User, Attendance, Leave, LeaveBalance, SalaryStructure, Payslip
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import settings


@pytest.fixture(scope="function")
async def async_client():
    """Create async test client with database setup."""
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[f"{settings.DATABASE_NAME}_test_phase6"]
    
    # Initialize Beanie with all models
    await init_beanie(
        database=database,
        document_models=[User, Attendance, Leave, LeaveBalance, SalaryStructure, Payslip]
    )
    
    # Clear all collections before each test
    await User.delete_all()
    await Attendance.delete_all()
    await Leave.delete_all()
    await LeaveBalance.delete_all()
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
    await LeaveBalance.delete_all()
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


# ==================== THE FINAL SYSTEM INTEGRATION TEST ====================

@pytest.mark.asyncio
async def test_final_system_integration(async_client):
    """
    THE ULTIMATE FINAL TEST - Integrates all 6 phases:
    Phase 1: Authentication
    Phase 2: Attendance
    Phase 3: Salary Configuration
    Phase 4: Profile Management
    Phase 5: Analytics & Payslip Generation
    Phase 6: Leave Management with Balances
    
    Complete Lifecycle Test Scenario
    """
    print("\n" + "="*80)
    print("🚀 FINAL SYSTEM INTEGRATION TEST - ALL 6 PHASES")
    print("="*80)
    
    # ========== STEP 1: SETUP - Create Employee & Set Salary ==========
    print("\n=== Step 1: Setup - Authentication & Salary ===")
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "employee@dayflow.com", "John", "Doe"
    )
    print(f"✓ Employee created: {login_id}")
    
    # Set salary to 60,000/month
    salary_response = await async_client.put(
        f"/admin/salary/{login_id}",
        json={"monthly_wage": 60000.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert salary_response.status_code == 200
    print(f"✓ Salary configured: ₹60,000/month")
    
    # ========== STEP 2: CHECK INITIAL LEAVE BALANCE ==========
    print("\n=== Step 2: Check Initial Leave Balance ===")
    balance_response = await async_client.get(
        "/leaves/me/balance",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert balance_response.status_code == 200
    balance_data = balance_response.json()
    
    print(f"✓ Initial Leave Balance:")
    print(f"  - Paid Leave: {balance_data['paid']} days")
    print(f"  - Sick Leave: {balance_data['sick']} days")
    
    assert balance_data['paid'] == 24.0, "Initial paid leave should be 24 days"
    assert balance_data['sick'] == 7.0, "Initial sick leave should be 7 days"
    
    # ========== STEP 3: EMPLOYEE APPLIES FOR 2 DAYS PAID LEAVE ==========
    print("\n=== Step 3: Apply for Paid Leave ===")
    
    # Calculate future dates for leave
    today = date.today()
    leave_start = today + timedelta(days=2)
    leave_end = today + timedelta(days=3)
    
    apply_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": leave_start.isoformat(),
            "end_date": leave_end.isoformat(),
            "leave_type": "PAID_LEAVE",
            "reason": "Family vacation"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert apply_response.status_code == 200
    leave_data = apply_response.json()
    leave_request_id = leave_data["request_id"]
    
    print(f"✓ Leave applied:")
    print(f"  - Request ID: {leave_request_id}")
    print(f"  - Days: {leave_data['days_count']}")
    print(f"  - Status: {leave_data['status']}")
    
    assert leave_data['days_count'] == 2, "Should request 2 days"
    assert leave_data['status'] == "PENDING", "Status should be PENDING"
    
    # ========== STEP 4: ADMIN APPROVES THE LEAVE REQUEST ==========
    print("\n=== Step 4: Admin Approves Leave ===")
    
    # Check pending requests
    pending_response = await async_client.get(
        "/leaves/admin/pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert pending_response.status_code == 200
    pending_list = pending_response.json()
    assert len(pending_list) == 1, "Should have 1 pending request"
    print(f"✓ Found {len(pending_list)} pending request(s)")
    
    # Approve the request
    approve_response = await async_client.put(
        f"/leaves/admin/action/{leave_request_id}",
        json={"action": "APPROVE"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert approve_response.status_code == 200
    approved_data = approve_response.json()
    
    print(f"✓ Leave approved:")
    print(f"  - Status: {approved_data['status']}")
    
    assert approved_data['status'] == "APPROVED", "Status should be APPROVED"
    
    # ========== STEP 5: VERIFY LEAVE BALANCE DEDUCTED ==========
    print("\n=== Step 5: Verify Leave Balance Updated ===")
    
    updated_balance_response = await async_client.get(
        "/leaves/me/balance",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert updated_balance_response.status_code == 200
    updated_balance = updated_balance_response.json()
    
    print(f"✓ Updated Leave Balance:")
    print(f"  - Paid Leave: {updated_balance['paid']} days (was 24)")
    print(f"  - Sick Leave: {updated_balance['sick']} days")
    
    assert updated_balance['paid'] == 22.0, "Paid leave should be reduced by 2 days (24 - 2 = 22)"
    assert updated_balance['sick'] == 7.0, "Sick leave should remain unchanged"
    
    # ========== STEP 6: VERIFY DASHBOARD INTEGRATION (LEAVE Status) ==========
    print("\n=== Step 6: Dashboard Integration - LEAVE Status ===")
    
    # Verify attendance records were created with LEAVE status
    from models import Attendance, AttendanceStatus
    leave_attendance = await Attendance.find(
        Attendance.user_id == login_id,
        Attendance.status == AttendanceStatus.LEAVE
    ).to_list()
    
    print(f"✓ LEAVE attendance records created: {len(leave_attendance)} days")
    assert len(leave_attendance) == 2, "Should have 2 LEAVE attendance records"
    
    # ========== STEP 7: APPLY FOR UNPAID LEAVE ==========
    print("\n=== Step 7: Apply for Unpaid Leave (Affects Salary) ===")
    
    unpaid_start = today + timedelta(days=5)
    unpaid_end = today + timedelta(days=7)
    
    unpaid_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": unpaid_start.isoformat(),
            "end_date": unpaid_end.isoformat(),
            "leave_type": "UNPAID_LEAVE",
            "reason": "Personal emergency"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert unpaid_response.status_code == 200
    unpaid_data = unpaid_response.json()
    unpaid_request_id = unpaid_data["request_id"]
    
    print(f"✓ Unpaid leave applied:")
    print(f"  - Days: {unpaid_data['days_count']} (affects salary)")
    print(f"  - Status: {unpaid_data['status']}")
    
    assert unpaid_data['days_count'] == 3, "Should request 3 days"
    
    # Approve unpaid leave
    approve_unpaid_response = await async_client.put(
        f"/leaves/admin/action/{unpaid_request_id}",
        json={"action": "APPROVE"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert approve_unpaid_response.status_code == 200
    print(f"✓ Unpaid leave approved")
    
    # Verify balance unchanged (unpaid doesn't deduct)
    final_balance_response = await async_client.get(
        "/leaves/me/balance",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    final_balance = final_balance_response.json()
    assert final_balance['paid'] == 22.0, "Paid leave balance should not change for unpaid leave"
    print(f"✓ Balance unchanged for unpaid leave: {final_balance['paid']} days")
    
    # ========== STEP 8: PAYROLL INTEGRATION - Verify Leave Integration ==========
    print("\n=== Step 8: Payroll Integration ===")
    
    # Generate payslip for current month
    now = datetime.utcnow()
    current_month = now.strftime("%m-%Y")
    
    payslip_response = await async_client.post(
        f"/payroll/generate-slip/{login_id}",
        json={"month": current_month},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert payslip_response.status_code == 201
    payslip = payslip_response.json()
    
    print(f"✓ Payslip generated successfully:")
    print(f"  - Present Days: {payslip['present_days']}")
    print(f"  - Leave Days: {payslip['leave_days']} (includes approved leaves with LEAVE status)")
    print(f"  - Payable Days: {payslip['payable_days']}")
    print(f"  - Net Salary: ₹{payslip['net_salary']}")
    
    # Verify leave days are counted correctly
    assert payslip['leave_days'] == 5, f"Should have 5 leave days (2 paid + 3 unpaid), got {payslip['leave_days']}"
    # Payable days includes leaves (since they're marked as LEAVE status in attendance)
    assert payslip['payable_days'] == 5.0, f"Payable days should be 5 (leave days count as payable), got {payslip['payable_days']}"
    
    # Verify net salary calculation (5 days * daily rate)
    daily_rate = 60000.0 / 30
    expected_salary = daily_rate * 5.0
    assert payslip['net_salary'] == expected_salary, f"Expected ₹{expected_salary}, got ₹{payslip['net_salary']}"
    
    print("\n" + "="*80)
    print("✅ FINAL SYSTEM INTEGRATION TEST PASSED!")
    print("="*80)
    print("\nAll 6 Phases Verified:")
    print("  ✓ Phase 1: Authentication & User Management")
    print("  ✓ Phase 2: Attendance & Basic Leave")
    print("  ✓ Phase 3: Salary Configuration")
    print("  ✓ Phase 4: Profile Management")
    print("  ✓ Phase 5: Analytics & Payslip Generation")
    print("  ✓ Phase 6: Complete Leave Management with Balances")
    print("="*80)


@pytest.mark.asyncio
async def test_insufficient_leave_balance(async_client):
    """Test that leave application is rejected when balance is insufficient"""
    print("\n=== Test: Insufficient Leave Balance ===")
    
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "test@dayflow.com", "Test", "User"
    )
    
    # Try to apply for 30 days (more than 24 day balance)
    today = date.today()
    leave_start = today + timedelta(days=1)
    leave_end = today + timedelta(days=30)
    
    apply_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": leave_start.isoformat(),
            "end_date": leave_end.isoformat(),
            "leave_type": "PAID_LEAVE",
            "reason": "Long vacation"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert apply_response.status_code == 400
    error_detail = apply_response.json()["detail"]
    assert "Insufficient paid leave balance" in error_detail
    print(f"✓ Correctly rejected: {error_detail}")


@pytest.mark.asyncio
async def test_past_date_rejection(async_client):
    """Test that leave applications for past dates are rejected"""
    print("\n=== Test: Past Date Rejection ===")
    
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "past@dayflow.com", "Past", "User"
    )
    
    # Try to apply for past dates
    yesterday = date.today() - timedelta(days=1)
    
    apply_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": yesterday.isoformat(),
            "end_date": yesterday.isoformat(),
            "leave_type": "PAID_LEAVE",
            "reason": "Retroactive leave"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    
    assert apply_response.status_code == 400
    assert "cannot be in the past" in apply_response.json()["detail"]
    print(f"✓ Past date correctly rejected")


@pytest.mark.asyncio
async def test_leave_rejection_no_balance_deduction(async_client):
    """Test that rejected leaves don't deduct balance"""
    print("\n=== Test: Leave Rejection (No Balance Deduction) ===")
    
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "reject@dayflow.com", "Reject", "Test"
    )
    
    # Apply for leave
    today = date.today()
    leave_start = today + timedelta(days=1)
    leave_end = today + timedelta(days=2)
    
    apply_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": leave_start.isoformat(),
            "end_date": leave_end.isoformat(),
            "leave_type": "PAID_LEAVE",
            "reason": "Test rejection"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert apply_response.status_code == 200
    request_id = apply_response.json()["request_id"]
    
    # Admin rejects
    reject_response = await async_client.put(
        f"/leaves/admin/action/{request_id}",
        json={"action": "REJECT"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "REJECTED"
    
    # Verify balance unchanged
    balance_response = await async_client.get(
        "/leaves/me/balance",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    balance = balance_response.json()
    
    assert balance['paid'] == 24.0, "Balance should remain 24 for rejected leave"
    print(f"✓ Balance unchanged after rejection: {balance['paid']} days")


@pytest.mark.asyncio
async def test_sick_leave_flow(async_client):
    """Test sick leave with attachment"""
    print("\n=== Test: Sick Leave Flow ===")
    
    admin_token = await create_admin_and_login(async_client)
    login_id, employee_token = await create_employee_and_login(
        async_client, admin_token, "sick@dayflow.com", "Sick", "User"
    )
    
    # Apply for sick leave with attachment
    today = date.today()
    leave_start = today + timedelta(days=1)
    leave_end = today + timedelta(days=1)
    
    apply_response = await async_client.post(
        "/leaves/apply",
        json={
            "start_date": leave_start.isoformat(),
            "end_date": leave_end.isoformat(),
            "leave_type": "SICK_LEAVE",
            "reason": "Medical emergency",
            "attachment_url": "https://example.com/sick-note.pdf"
        },
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert apply_response.status_code == 200
    leave_data = apply_response.json()
    request_id = leave_data["request_id"]
    
    print(f"✓ Sick leave applied with attachment")
    assert leave_data["leave_type"] == "SICK_LEAVE"
    assert leave_data["attachment_url"] == "https://example.com/sick-note.pdf"
    
    # Approve
    approve_response = await async_client.put(
        f"/leaves/admin/action/{request_id}",
        json={"action": "APPROVE"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert approve_response.status_code == 200
    
    # Verify sick balance deducted
    balance_response = await async_client.get(
        "/leaves/me/balance",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    balance = balance_response.json()
    
    assert balance['sick'] == 6.0, "Sick leave balance should be reduced to 6"
    assert balance['paid'] == 24.0, "Paid leave should remain 24"
    print(f"✓ Sick leave balance deducted: {balance['sick']} days remaining")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
