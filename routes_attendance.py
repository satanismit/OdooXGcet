from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from models import (
    User,
    Attendance,
    Leave,
    AttendanceStatus,
    LeaveStatus,
    CheckInRequest,
    CheckOutRequest,
    CheckInResponse,
    CheckOutResponse,
    EmployeeStatusResponse,
    LeaveRequest,
    LeaveApplyResponse,
)
from routes import get_current_user, get_current_admin


# Router
attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
leave_router = APIRouter(prefix="/leave", tags=["Leave"])


@dashboard_router.get("/employees", response_model=List[EmployeeStatusResponse])
async def get_employee_dashboard(
    search: Optional[str] = Query(None, description="Search by employee name"),
    current_user: User = Depends(get_current_user)
):
    """
    Get all employees with their current status for dashboard display.
    
    Status indicators:
    - Green (PRESENT): User has checked in today
    - Airplane (LEAVE): User has approved leave for today
    - Yellow (ABSENT): User hasn't checked in and no approved leave
    """
    # Build query
    query = {}
    if search:
        # Search by first name or last name (case-insensitive)
        query = {
            "$or": [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
            ]
        }
    
    # Get all users
    users = await User.find(query).to_list()
    
    # Get today's date
    today = datetime.combine(date.today(), datetime.min.time())
    
    # Build response with status for each user
    result = []
    for user in users:
        status_icon, status_label = await get_user_status(user.login_id, today)
        
        result.append(EmployeeStatusResponse(
            login_id=user.login_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            status=status_icon,
            status_label=status_label
        ))
    
    return result


async def get_user_status(user_id: str, check_date: datetime) -> tuple[str, str]:
    """
    Determine user status for a given date.
    
    Returns:
        Tuple of (status_icon, status_label)
        - ("Green", "PRESENT"): Checked in
        - ("Airplane", "LEAVE"): On approved leave
        - ("Yellow", "ABSENT"): Not checked in, no leave
    """
    # Check if user has checked in today (compare dates only)
    attendance = await Attendance.find_one(
        Attendance.user_id == user_id,
        Attendance.date >= datetime.combine(check_date.date(), datetime.min.time()),
        Attendance.date < datetime.combine(check_date.date() + timedelta(days=1), datetime.min.time())
    )
    
    if attendance and attendance.check_in_time:
        return ("Green", "PRESENT")
    
    # Check if user has approved leave for today
    leave = await Leave.find_one(
        Leave.user_id == user_id,
        Leave.status == LeaveStatus.APPROVED,
        Leave.start_date <= check_date,
        Leave.end_date >= check_date
    )
    
    if leave:
        return ("Airplane", "LEAVE")
    
    # Default to absent
    return ("Yellow", "ABSENT")


@attendance_router.post("/check-in", response_model=CheckInResponse)
async def check_in(current_user: User = Depends(get_current_user)):
    """
    Record employee check-in for today.
    
    Rules:
    - Records current timestamp
    - Sets status to PRESENT
    - Cannot check in twice on same day
    """
    today = datetime.combine(date.today(), datetime.min.time())
    
    # Check if already checked in today
    existing_attendance = await Attendance.find_one(
        Attendance.user_id == current_user.login_id,
        Attendance.date >= today,
        Attendance.date < today + timedelta(days=1)
    )
    
    if existing_attendance and existing_attendance.check_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already checked in today at {existing_attendance.check_in_time.strftime('%H:%M:%S')}"
        )
    
    # Create or update attendance record
    now = datetime.utcnow()
    
    if existing_attendance:
        # Update existing record
        existing_attendance.check_in_time = now
        existing_attendance.status = AttendanceStatus.PRESENT
        existing_attendance.updated_at = now
        await existing_attendance.save()
        attendance = existing_attendance
    else:
        # Create new record
        attendance = Attendance(
            user_id=current_user.login_id,
            date=today,
            check_in_time=now,
            status=AttendanceStatus.PRESENT
        )
        await attendance.insert()
    
    return CheckInResponse(
        message="Checked in successfully",
        user_id=current_user.login_id,
        check_in_time=now,
        status=attendance.status.value
    )


@attendance_router.post("/check-out", response_model=CheckOutResponse)
async def check_out(current_user: User = Depends(get_current_user)):
    """
    Record employee check-out for today.
    
    Rules:
    - Records current timestamp
    - Calculates total hours worked
    - Must have checked in first
    """
    today = datetime.combine(date.today(), datetime.min.time())
    
    # Find today's attendance record
    attendance = await Attendance.find_one(
        Attendance.user_id == current_user.login_id,
        Attendance.date >= today,
        Attendance.date < today + timedelta(days=1)
    )
    
    if not attendance or not attendance.check_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check out without checking in first"
        )
    
    if attendance.check_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already checked out today at {attendance.check_out_time.strftime('%H:%M:%S')}"
        )
    
    # Update check-out time
    now = datetime.utcnow()
    attendance.check_out_time = now
    attendance.updated_at = now
    await attendance.save()
    
    # Calculate total hours
    time_diff = now - attendance.check_in_time
    total_hours = round(time_diff.total_seconds() / 3600, 2)
    
    return CheckOutResponse(
        message="Checked out successfully",
        user_id=current_user.login_id,
        check_out_time=now,
        total_hours=total_hours
    )


@leave_router.post("/apply", response_model=LeaveApplyResponse)
async def apply_leave(
    request: LeaveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Apply for leave.
    
    Employee can request leave which will be pending approval.
    """
    # Parse dates and convert to datetime at start of day
    start_dt = datetime.combine(request.start_date, datetime.min.time())
    end_dt = datetime.combine(request.end_date, datetime.min.time())
    
    # Create leave request
    leave = Leave(
        user_id=current_user.login_id,
        start_date=start_dt,
        end_date=end_dt,
        reason=request.reason,
        status=LeaveStatus.PENDING
    )
    
    await leave.insert()
    
    return LeaveApplyResponse(
        message="Leave request submitted successfully",
        leave_id=str(leave.id),
        status=leave.status.value
    )


@leave_router.post("/approve/{leave_id}")
async def approve_leave(
    leave_id: str,
    current_admin: User = Depends(get_current_admin)
):
    """
    Approve a leave request (Admin only).
    """
    from beanie import PydanticObjectId
    
    # Find the leave request
    leave = await Leave.get(PydanticObjectId(leave_id))
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave is already {leave.status.value}"
        )
    
    # Approve leave
    leave.status = LeaveStatus.APPROVED
    leave.approved_by = current_admin.login_id
    leave.updated_at = datetime.utcnow()
    await leave.save()
    
    return {
        "message": "Leave approved successfully",
        "leave_id": str(leave.id),
        "status": leave.status.value
    }


@leave_router.get("/my-leaves")
async def get_my_leaves(current_user: User = Depends(get_current_user)):
    """
    Get all leave requests for the current user.
    """
    leaves = await Leave.find(Leave.user_id == current_user.login_id).to_list()
    
    return {
        "leaves": [
            {
                "id": str(leave.id),
                "start_date": leave.start_date.isoformat(),
                "end_date": leave.end_date.isoformat(),
                "reason": leave.reason,
                "status": leave.status.value,
                "approved_by": leave.approved_by,
            }
            for leave in leaves
        ]
    }
