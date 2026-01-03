"""
Phase 6: Complete Leave Management System
Handles Leave Applications, Balances, and Admin Approvals
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, date, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from models import (
    User, Leave, LeaveBalance, Attendance, 
    LeaveStatus, LeaveType, AttendanceStatus
)
from routes import get_current_user, get_current_admin


# Router Configuration
leave_router = APIRouter(prefix="/leaves", tags=["Leave Management"])


# ========================
# Request/Response Models
# ========================

class LeaveBalanceResponse(BaseModel):
    """Employee leave balance response"""
    paid: float
    sick: float
    year: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "paid": 24.0,
                "sick": 7.0,
                "year": 2026
            }
        }


class ApplyLeaveRequest(BaseModel):
    """Leave application request"""
    start_date: str  # ISO date string YYYY-MM-DD
    end_date: str    # ISO date string YYYY-MM-DD
    leave_type: LeaveType
    reason: str = Field(..., min_length=5)
    attachment_url: Optional[str] = None  # Optional for sick leave
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2026-01-10",
                "end_date": "2026-01-12",
                "leave_type": "PAID_LEAVE",
                "reason": "Family vacation",
                "attachment_url": None
            }
        }


class LeaveRequestResponse(BaseModel):
    """Leave request response"""
    request_id: str
    user_id: str
    employee_name: str
    start_date: str
    end_date: str
    leave_type: str
    days_count: int
    reason: str
    status: str
    attachment_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "507f1f77bcf86cd799439011",
                "user_id": "DAJODO20260001",
                "employee_name": "John Doe",
                "start_date": "2026-01-10",
                "end_date": "2026-01-12",
                "leave_type": "PAID_LEAVE",
                "days_count": 3,
                "reason": "Family vacation",
                "status": "PENDING",
                "attachment_url": None,
                "created_at": "2026-01-03T10:00:00"
            }
        }


class LeaveActionRequest(BaseModel):
    """Admin action on leave request"""
    action: str  # "APPROVE" or "REJECT"
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "APPROVE"
            }
        }


# ========================
# Helper Functions
# ========================

def calculate_days_between(start_date: date, end_date: date) -> int:
    """Calculate number of days between two dates (inclusive)"""
    return (end_date - start_date).days + 1


async def get_or_create_leave_balance(user_id: str, year: int) -> LeaveBalance:
    """Get existing leave balance or create new one for the year"""
    balance = await LeaveBalance.find_one(
        LeaveBalance.user_id == user_id,
        LeaveBalance.year == year
    )
    
    if not balance:
        # Create new balance for the year
        balance = LeaveBalance(
            user_id=user_id,
            paid_leave_balance=24.0,
            sick_leave_balance=7.0,
            year=year
        )
        await balance.insert()
    
    return balance


async def create_leave_attendance_records(user_id: str, start_date: date, end_date: date):
    """Create LEAVE status attendance records for approved leave days"""
    current_date = start_date
    while current_date <= end_date:
        # Check if attendance record already exists
        existing = await Attendance.find_one(
            Attendance.user_id == user_id,
            Attendance.date == datetime.combine(current_date, datetime.min.time())
        )
        
        if existing:
            # Update existing record to LEAVE status
            existing.status = AttendanceStatus.LEAVE
            existing.updated_at = datetime.utcnow()
            await existing.save()
        else:
            # Create new LEAVE attendance record
            attendance = Attendance(
                user_id=user_id,
                date=datetime.combine(current_date, datetime.min.time()),
                status=AttendanceStatus.LEAVE,
                check_in_time=None,
                check_out_time=None
            )
            await attendance.insert()
        
        current_date += timedelta(days=1)


# ========================
# API Endpoints
# ========================

@leave_router.get("/me/balance", response_model=LeaveBalanceResponse)
async def get_my_leave_balance(current_user: User = Depends(get_current_user)):
    """
    Get employee's current leave balance
    
    - **Access**: Employee (own balance only)
    - **Returns**: Paid and sick leave balances for current year
    """
    current_year = datetime.utcnow().year
    balance = await get_or_create_leave_balance(current_user.login_id, current_year)
    
    return LeaveBalanceResponse(
        paid=balance.paid_leave_balance,
        sick=balance.sick_leave_balance,
        year=balance.year
    )


@leave_router.get("/my-leaves")
async def get_my_leaves(current_user: User = Depends(get_current_user)):
    """
    Get all leave requests for the current user
    
    - **Access**: Employee (own leaves only)
    - **Returns**: List of leave requests with status
    """
    leaves = await Leave.find(Leave.user_id == current_user.login_id).to_list()
    
    return {
        "leaves": [
            {
                "id": str(leave.id),
                "leave_type": leave.leave_type.value,
                "start_date": leave.start_date.isoformat(),
                "end_date": leave.end_date.isoformat(),
                "status": leave.status.value,
                "reason": leave.reason,
                "applied_on": leave.applied_on.isoformat(),
                "days": (leave.end_date - leave.start_date).days + 1,
            }
            for leave in leaves
        ]
    }


@leave_router.post("/apply", response_model=LeaveRequestResponse)
async def apply_for_leave(
    request: ApplyLeaveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Apply for leave
    
    - **Access**: Employee
    - **Validation**: 
        - Start date cannot be in the past
        - End date must be >= start date
        - Check leave balance for PAID/SICK leaves
    - **Note**: UNPAID leaves allowed but will affect salary
    """
    # Parse dates
    try:
        start_date = datetime.fromisoformat(request.start_date).date()
        end_date = datetime.fromisoformat(request.end_date).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Validation: Start date cannot be in the past
    today = date.today()
    if start_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be in the past"
        )
    
    # Validation: End date >= Start date
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be greater than or equal to start date"
        )
    
    # Calculate days
    days_count = calculate_days_between(start_date, end_date)
    
    # Check leave balance for PAID_LEAVE or SICK_LEAVE
    if request.leave_type in [LeaveType.PAID_LEAVE, LeaveType.SICK_LEAVE]:
        current_year = datetime.utcnow().year
        balance = await get_or_create_leave_balance(current_user.login_id, current_year)
        
        if request.leave_type == LeaveType.PAID_LEAVE:
            if balance.paid_leave_balance < days_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient paid leave balance. Available: {balance.paid_leave_balance} days, Requested: {days_count} days"
                )
        elif request.leave_type == LeaveType.SICK_LEAVE:
            if balance.sick_leave_balance < days_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient sick leave balance. Available: {balance.sick_leave_balance} days, Requested: {days_count} days"
                )
    
    # Create leave request
    leave_request = Leave(
        user_id=current_user.login_id,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.min.time()),
        leave_type=request.leave_type,
        reason=request.reason,
        attachment_url=request.attachment_url,
        days_count=days_count,
        status=LeaveStatus.PENDING
    )
    await leave_request.insert()
    
    return LeaveRequestResponse(
        request_id=str(leave_request.id),
        user_id=leave_request.user_id,
        employee_name=f"{current_user.first_name} {current_user.last_name}",
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        leave_type=leave_request.leave_type.value,
        days_count=leave_request.days_count,
        reason=leave_request.reason,
        status=leave_request.status.value,
        attachment_url=leave_request.attachment_url,
        created_at=leave_request.created_at
    )


@leave_router.get("/admin/pending", response_model=List[LeaveRequestResponse])
async def get_pending_leave_requests(current_user: User = Depends(get_current_admin)):
    """
    Get all pending leave requests
    
    - **Access**: Admin Only
    - **Returns**: List of all leave requests with PENDING status
    """
    pending_requests = await Leave.find(Leave.status == LeaveStatus.PENDING).to_list()
    
    response = []
    for leave_req in pending_requests:
        # Get employee details
        employee = await User.find_one(User.login_id == leave_req.user_id)
        employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"
        
        response.append(LeaveRequestResponse(
            request_id=str(leave_req.id),
            user_id=leave_req.user_id,
            employee_name=employee_name,
            start_date=leave_req.start_date.date().isoformat(),
            end_date=leave_req.end_date.date().isoformat(),
            leave_type=leave_req.leave_type.value,
            days_count=leave_req.days_count,
            reason=leave_req.reason,
            status=leave_req.status.value,
            attachment_url=leave_req.attachment_url,
            created_at=leave_req.created_at
        ))
    
    return response


@leave_router.put("/admin/action/{request_id}", response_model=LeaveRequestResponse)
async def admin_action_on_leave(
    request_id: str,
    action_request: LeaveActionRequest,
    current_user: User = Depends(get_current_admin)
):
    """
    Admin approval or rejection of leave request
    
    - **Access**: Admin Only
    - **Actions**: "APPROVE" or "REJECT"
    - **On Approval**:
        - Deduct leave balance
        - Create LEAVE attendance records
        - Update status to APPROVED
    - **On Rejection**:
        - Update status to REJECTED
        - No balance deduction
    """
    # Validate action
    if action_request.action not in ["APPROVE", "REJECT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'APPROVE' or 'REJECT'"
        )
    
    # Find leave request
    leave_request = await Leave.get(request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    # Check if already processed
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave request already {leave_request.status.value}"
        )
    
    # Get employee details
    employee = await User.find_one(User.login_id == leave_request.user_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if action_request.action == "APPROVE":
        # APPROVAL LOGIC
        
        # 1. Deduct leave balance if PAID or SICK leave
        if leave_request.leave_type in [LeaveType.PAID_LEAVE, LeaveType.SICK_LEAVE]:
            current_year = datetime.utcnow().year
            balance = await get_or_create_leave_balance(leave_request.user_id, current_year)
            
            if leave_request.leave_type == LeaveType.PAID_LEAVE:
                balance.paid_leave_balance -= leave_request.days_count
            elif leave_request.leave_type == LeaveType.SICK_LEAVE:
                balance.sick_leave_balance -= leave_request.days_count
            
            balance.updated_at = datetime.utcnow()
            await balance.save()
        
        # 2. Create LEAVE attendance records for each day
        start_date = leave_request.start_date.date()
        end_date = leave_request.end_date.date()
        await create_leave_attendance_records(leave_request.user_id, start_date, end_date)
        
        # 3. Update leave request status
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by = current_user.login_id
        
    else:
        # REJECTION LOGIC
        leave_request.status = LeaveStatus.REJECTED
        leave_request.approved_by = current_user.login_id
    
    leave_request.updated_at = datetime.utcnow()
    await leave_request.save()
    
    return LeaveRequestResponse(
        request_id=str(leave_request.id),
        user_id=leave_request.user_id,
        employee_name=f"{employee.first_name} {employee.last_name}",
        start_date=leave_request.start_date.date().isoformat(),
        end_date=leave_request.end_date.date().isoformat(),
        leave_type=leave_request.leave_type.value,
        days_count=leave_request.days_count,
        reason=leave_request.reason,
        status=leave_request.status.value,
        attachment_url=leave_request.attachment_url,
        created_at=leave_request.created_at
    )
