"""
Phase 5: Attendance Analytics Routes
Provides statistics and analytics for attendance tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime, date
from typing import Optional, List
from models import User, Attendance, AttendanceStatus
from routes import get_current_user, get_current_admin
from pydantic import BaseModel
from calendar import monthrange


analytics_router = APIRouter(prefix="/attendance", tags=["Attendance Analytics"])


# ==================== RESPONSE MODELS ====================

class AttendanceStatsResponse(BaseModel):
    """Response model for attendance statistics"""
    month: str
    days_present: int
    leave_count: int
    total_working_days: int
    extra_hours: float
    absent_days: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": "01-2026",
                "days_present": 22,
                "leave_count": 2,
                "total_working_days": 31,
                "extra_hours": 0.0,
                "absent_days": 7
            }
        }


class EmployeeAttendanceRecord(BaseModel):
    """Single employee attendance record for a specific date"""
    login_id: str
    name: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    work_hours: float
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "DAJODO20260001",
                "name": "John Doe",
                "check_in_time": "2026-01-03T09:00:00",
                "check_out_time": "2026-01-03T18:00:00",
                "work_hours": 9.0,
                "status": "PRESENT"
            }
        }


# ==================== ENDPOINTS ====================

@analytics_router.get("/stats/me", response_model=AttendanceStatsResponse)
async def get_my_attendance_stats(
    month: Optional[str] = Query(None, description="Month in MM-YYYY format (e.g., '01-2026')"),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance statistics for the logged-in employee.
    
    - **Access**: Employee (any authenticated user)
    - **Input**: month (optional, defaults to current month)
    - **Returns**: Days present, leaves, total working days, extra hours
    """
    # Parse month or use current
    if month:
        try:
            month_date = datetime.strptime(month, "%m-%Y")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format. Use MM-YYYY (e.g., '01-2026')"
            )
    else:
        month_date = datetime.utcnow()
        month = month_date.strftime("%m-%Y")
    
    # Get month boundaries
    year = month_date.year
    month_num = month_date.month
    _, last_day = monthrange(year, month_num)
    
    start_date = datetime(year, month_num, 1)
    end_date = datetime(year, month_num, last_day, 23, 59, 59)
    
    # Fetch attendance records for the month
    attendance_records = await Attendance.find(
        Attendance.user_id == current_user.login_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).to_list()
    
    # Count present days (records with check-in)
    days_present = len([a for a in attendance_records if a.status == AttendanceStatus.PRESENT])
    
    # Count leave days (we'll check Leave model in a real scenario, for now use LEAVE status)
    leave_count = len([a for a in attendance_records if a.status == AttendanceStatus.LEAVE])
    
    # Calculate absent days
    total_working_days = last_day
    recorded_days = len(attendance_records)
    absent_days = max(0, total_working_days - recorded_days)
    
    return AttendanceStatsResponse(
        month=month,
        days_present=days_present,
        leave_count=leave_count,
        total_working_days=total_working_days,
        extra_hours=0.0,  # Placeholder for future enhancement
        absent_days=absent_days
    )


@analytics_router.get("/list", response_model=List[EmployeeAttendanceRecord])
async def get_attendance_list(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get attendance list for all employees on a specific date.
    
    - **Access**: Admin Only
    - **Input**: date (required, format: YYYY-MM-DD)
    - **Returns**: List of all employees with check-in/out times and work hours
    """
    # Parse date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD (e.g., '2026-01-03')"
        )
    
    # Set date boundaries (start and end of day)
    start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    # Fetch all users (employees)
    all_users = await User.find(User.role == "EMPLOYEE").to_list()
    
    # Fetch attendance records for the date
    attendance_records = await Attendance.find(
        Attendance.date >= start_of_day,
        Attendance.date <= end_of_day
    ).to_list()
    
    # Create a mapping of user_id to attendance
    attendance_map = {a.user_id: a for a in attendance_records}
    
    # Build response
    result = []
    for user in all_users:
        attendance = attendance_map.get(user.login_id)
        
        if attendance:
            # Calculate work hours
            if attendance.check_in_time and attendance.check_out_time:
                time_diff = attendance.check_out_time - attendance.check_in_time
                work_hours = round(time_diff.total_seconds() / 3600, 2)
            else:
                work_hours = 0.0
            
            result.append(EmployeeAttendanceRecord(
                login_id=user.login_id,
                name=f"{user.first_name} {user.last_name}",
                check_in_time=attendance.check_in_time.isoformat() if attendance.check_in_time else None,
                check_out_time=attendance.check_out_time.isoformat() if attendance.check_out_time else None,
                work_hours=work_hours,
                status=attendance.status
            ))
        else:
            # No attendance record - mark as absent
            result.append(EmployeeAttendanceRecord(
                login_id=user.login_id,
                name=f"{user.first_name} {user.last_name}",
                check_in_time=None,
                check_out_time=None,
                work_hours=0.0,
                status="ABSENT"
            ))
    
    return result
