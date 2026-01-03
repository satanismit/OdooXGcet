"""
Phase 5: Payroll Routes
Handles payslip generation based on attendance and salary data
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import Optional
from models import User, Attendance, AttendanceStatus, SalaryStructure, Payslip, Leave, LeaveStatus
from routes import get_current_admin
from pydantic import BaseModel
from calendar import monthrange


payroll_router = APIRouter(prefix="/payroll", tags=["Payroll Management"])


# ==================== REQUEST/RESPONSE MODELS ====================

class GeneratePayslipRequest(BaseModel):
    """Request model for generating payslip"""
    month: str  # Format: MM-YYYY (e.g., "01-2026")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": "01-2026"
            }
        }


class PayslipResponse(BaseModel):
    """Response model for payslip"""
    payslip_id: str
    user_id: str
    month_year: str
    total_working_days: int
    present_days: int
    leave_days: int
    absent_days: int
    payable_days: float
    monthly_wage: float
    daily_rate: float
    net_salary: float
    generated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "payslip_id": "507f1f77bcf86cd799439011",
                "user_id": "DAJODO20260001",
                "month_year": "01-2026",
                "total_working_days": 31,
                "present_days": 22,
                "leave_days": 2,
                "absent_days": 7,
                "payable_days": 24.0,
                "monthly_wage": 60000.0,
                "daily_rate": 2000.0,
                "net_salary": 48000.0,
                "generated_at": "2026-01-31T23:59:59"
            }
        }


# ==================== ENDPOINTS ====================

@payroll_router.post("/generate-slip/{user_id}", response_model=PayslipResponse, status_code=201)
async def generate_payslip(
    user_id: str,
    request: GeneratePayslipRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    Generate payslip for an employee for a specific month.
    
    - **Access**: Admin Only
    - **Input**: user_id (path), month (body, format: MM-YYYY)
    - **Logic**:
        1. Fetch attendance records for the month
        2. Count present, leave, and absent days
        3. Calculate payable days
        4. Fetch salary structure
        5. Calculate pro-rated net salary
        6. Save and return payslip
    """
    # Validate user exists
    user = await User.find_one(User.login_id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with login_id '{user_id}' not found"
        )
    
    # Parse month
    try:
        month_date = datetime.strptime(request.month, "%m-%Y")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month format. Use MM-YYYY (e.g., '01-2026')"
        )
    
    # Get month boundaries
    year = month_date.year
    month_num = month_date.month
    _, last_day = monthrange(year, month_num)
    
    start_date = datetime(year, month_num, 1)
    end_date = datetime(year, month_num, last_day, 23, 59, 59)
    
    # Fetch attendance records for the month
    attendance_records = await Attendance.find(
        Attendance.user_id == user_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).to_list()
    
    # Count present days
    present_days = len([a for a in attendance_records if a.status == AttendanceStatus.PRESENT])
    
    # Fetch approved leaves for the month
    approved_leaves = await Leave.find(
        Leave.user_id == user_id,
        Leave.status == LeaveStatus.APPROVED,
        Leave.start_date >= start_date.date(),
        Leave.start_date <= end_date.date()
    ).to_list()
    
    # Count leave days (sum of all approved leave durations)
    leave_days = 0
    for leave in approved_leaves:
        # Calculate leave duration in days
        leave_duration = (leave.end_date - leave.start_date).days + 1
        leave_days += leave_duration
    
    # Calculate absent days
    total_working_days = last_day
    recorded_days = len(attendance_records)
    absent_days = max(0, total_working_days - present_days - leave_days)
    
    # Calculate payable days (Present + Paid Leaves)
    # In this implementation, all approved leaves are paid
    payable_days = float(present_days + leave_days)
    
    # Fetch salary structure
    salary_structure = await SalaryStructure.find_one(
        SalaryStructure.user_id == user_id
    )
    
    if not salary_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salary structure not configured for user '{user_id}'"
        )
    
    # Calculate net salary
    # Formula: (MonthlyWage / 30) * PayableDays
    monthly_wage = salary_structure.monthly_wage
    daily_rate = monthly_wage / 30.0
    net_salary = round(daily_rate * payable_days, 2)
    
    # Check if payslip already exists for this month
    existing_payslip = await Payslip.find_one(
        Payslip.user_id == user_id,
        Payslip.month_year == request.month
    )
    
    if existing_payslip:
        # Update existing payslip
        existing_payslip.total_working_days = total_working_days
        existing_payslip.present_days = present_days
        existing_payslip.leave_days = leave_days
        existing_payslip.absent_days = absent_days
        existing_payslip.payable_days = payable_days
        existing_payslip.monthly_wage = monthly_wage
        existing_payslip.net_salary = net_salary
        existing_payslip.generated_at = datetime.utcnow()
        
        await existing_payslip.save()
        payslip = existing_payslip
    else:
        # Create new payslip
        payslip = Payslip(
            user_id=user_id,
            month_year=request.month,
            total_working_days=total_working_days,
            present_days=present_days,
            leave_days=leave_days,
            absent_days=absent_days,
            payable_days=payable_days,
            monthly_wage=monthly_wage,
            net_salary=net_salary
        )
        
        await payslip.insert()
    
    return PayslipResponse(
        payslip_id=str(payslip.id),
        user_id=payslip.user_id,
        month_year=payslip.month_year,
        total_working_days=payslip.total_working_days,
        present_days=payslip.present_days,
        leave_days=payslip.leave_days,
        absent_days=payslip.absent_days,
        payable_days=payslip.payable_days,
        monthly_wage=payslip.monthly_wage,
        daily_rate=round(daily_rate, 2),
        net_salary=payslip.net_salary,
        generated_at=payslip.generated_at.isoformat()
    )


@payroll_router.get("/slip/{user_id}/{month}", response_model=PayslipResponse)
async def get_payslip(
    user_id: str,
    month: str,
    current_admin: User = Depends(get_current_admin)
):
    """
    Retrieve a specific payslip.
    
    - **Access**: Admin Only
    - **Input**: user_id (path), month (path, format: MM-YYYY)
    """
    payslip = await Payslip.find_one(
        Payslip.user_id == user_id,
        Payslip.month_year == month
    )
    
    if not payslip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payslip not found for user '{user_id}' in month '{month}'"
        )
    
    # Calculate daily rate for response
    daily_rate = payslip.monthly_wage / 30.0
    
    return PayslipResponse(
        payslip_id=str(payslip.id),
        user_id=payslip.user_id,
        month_year=payslip.month_year,
        total_working_days=payslip.total_working_days,
        present_days=payslip.present_days,
        leave_days=payslip.leave_days,
        absent_days=payslip.absent_days,
        payable_days=payslip.payable_days,
        monthly_wage=payslip.monthly_wage,
        daily_rate=round(daily_rate, 2),
        net_salary=payslip.net_salary,
        generated_at=payslip.generated_at.isoformat()
    )
