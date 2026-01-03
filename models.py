from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Annotated
from beanie import Document, Indexed, Link
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, field_serializer


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LEAVE = "LEAVE"
    HALF_DAY = "HALF_DAY"


class SalaryComponentType(str, Enum):
    FIXED_AMOUNT = "FIXED_AMOUNT"
    PERCENTAGE_OF_WAGE = "PERCENTAGE_OF_WAGE"
    PERCENTAGE_OF_BASIC = "PERCENTAGE_OF_BASIC"


class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"


class PersonalDetails(BaseModel):
    """Personal information nested model"""
    date_of_birth: Optional[str] = None  # Store as ISO string (YYYY-MM-DD)
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    current_address: Optional[str] = None
    personal_email: Optional[EmailStr] = None


class BankDetails(BaseModel):
    """Bank account information nested model"""
    bank_name: Optional[str] = None
    account_number: Optional[str] = Field(None, min_length=8)
    ifsc_code: Optional[str] = Field(None, pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    uan_number: Optional[str] = None


class User(Document):
    """MongoDB User Document"""
    login_id: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    company_name: str
    role: UserRole
    joining_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Phase 4: Private Info Fields
    personal_details: Optional[PersonalDetails] = None
    bank_details: Optional[BankDetails] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "login_id": "ODJODO20220001",
                "email": "john.doe@ode.com",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": "Ode",
                "role": "ADMIN",
                "joining_date": "2022-01-15T00:00:00",
            }
        }
    )

    class Settings:
        name = "users"
        indexes = [
            "login_id",
            "email",
        ]


# Request Models
class SignupRequest(BaseModel):
    company_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "Ode",
                "email": "admin@ode.com",
                "password": "SecurePassword123",
                "first_name": "John",
                "last_name": "Doe",
            }
        }
    )


class CreateEmployeeRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    joining_date: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@ode.com",
                "joining_date": "2026-01-15T00:00:00",
            }
        }
    )


class LoginRequest(BaseModel):
    login_id_or_email: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "login_id_or_email": "ODJODO20220001",
                "password": "SecurePassword123",
            }
        }
    )


# Response Models
class SignupResponse(BaseModel):
    message: str
    login_id: str
    email: str
    role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Company admin registered successfully",
                "login_id": "ODJODO20220001",
                "email": "admin@ode.com",
                "role": "ADMIN",
            }
        }
    )


class CreateEmployeeResponse(BaseModel):
    message: str
    login_id: str
    email: str
    temporary_password: str
    role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Employee created successfully",
                "login_id": "ODJASM20260002",
                "email": "jane.smith@ode.com",
                "temporary_password": "TempPass123!",
                "role": "EMPLOYEE",
            }
        }
    )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    login_id: str
    email: str
    role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "login_id": "ODJODO20220001",
                "email": "admin@ode.com",
                "role": "ADMIN",
            }
        }
    )


class TokenData(BaseModel):
    login_id: Optional[str] = None


# ========================
# Phase 2: Attendance, Leave, and Salary Models
# ========================

class Attendance(Document):
    """Attendance tracking for employees"""
    user_id: str  # References User.login_id
    date: datetime  # Stored as datetime but represents date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.ABSENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "attendance"
        indexes = [
            [("user_id", 1), ("date", 1)],  # Compound index for unique per user per day
        ]


class Leave(Document):
    """Leave requests and approvals"""
    user_id: str  # References User.login_id
    start_date: datetime  # Stored as datetime but represents date
    end_date: datetime  # Stored as datetime but represents date
    reason: str
    status: LeaveStatus = LeaveStatus.PENDING
    approved_by: Optional[str] = None  # Admin login_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "leaves"
        indexes = [
            "user_id",
            "status",
        ]


class SalaryComponent(BaseModel):
    """Individual salary component"""
    name: str
    type: SalaryComponentType
    value: float  # Percentage or fixed amount
    calculated_amount: float  # The actual computed amount

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Basic",
                "type": "PERCENTAGE_OF_WAGE",
                "value": 50.0,
                "calculated_amount": 25000.0,
            }
        }
    )


class SalaryDeductions(BaseModel):
    """Salary deductions structure"""
    provident_fund: float  # 12% of Basic
    professional_tax: float  # Fixed 200
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provident_fund": 3000.0,
                "professional_tax": 200.0,
            }
        }
    )


class SalaryStructure(Document):
    """Salary configuration for an employee"""
    user_id: str  # References User.login_id
    monthly_wage: float
    yearly_wage: float  # Computed: Monthly * 12
    working_days_per_week: int = 5
    breakdown: List[SalaryComponent] = []  # Earnings components
    deductions: Optional[SalaryDeductions] = None
    configured_by: Optional[str] = None  # Admin login_id who configured
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "salary_structures"
        indexes = [
            "user_id",
        ]


# ========================
# Phase 2: Request Models
# ========================

class CheckInRequest(BaseModel):
    """Check-in request (no body needed, uses auth token)"""
    pass


class CheckOutRequest(BaseModel):
    """Check-out request (no body needed, uses auth token)"""
    pass


class SalaryConfigRequest(BaseModel):
    """Salary configuration request for Phase 3"""
    monthly_wage: float = Field(..., gt=0, description="Monthly wage must be positive")
    working_days_per_week: int = Field(default=5, ge=1, le=7, description="Working days per week")

    @field_validator('monthly_wage')
    @classmethod
    def validate_positive_wage(cls, v):
        if v <= 0:
            raise ValueError('Monthly wage must be positive')
        return round(v, 2)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "monthly_wage": 50000.0,
                "working_days_per_week": 5,
            }
        }
    )


class LeaveRequest(BaseModel):
    """Leave application request"""
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1)

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2026-01-20",
                "end_date": "2026-01-22",
                "reason": "Personal work",
            }
        }
    )


# ========================
# Phase 2: Response Models
# ========================

class EmployeeStatusResponse(BaseModel):
    """Employee status for dashboard"""
    login_id: str
    first_name: str
    last_name: str
    email: str
    status: str  # "Green" (Present), "Yellow" (Absent), "Airplane" (Leave)
    status_label: str  # "PRESENT", "ABSENT", "LEAVE"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "login_id": "ODJODO20220001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@ode.com",
                "status": "Green",
                "status_label": "PRESENT",
            }
        }
    )


class CheckInResponse(BaseModel):
    """Check-in response"""
    message: str
    user_id: str
    check_in_time: datetime
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Checked in successfully",
                "user_id": "ODJODO20220001",
                "check_in_time": "2026-01-03T09:00:00",
                "status": "PRESENT",
            }
        }
    )


class CheckOutResponse(BaseModel):
    """Check-out response"""
    message: str
    user_id: str
    check_out_time: datetime
    total_hours: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Checked out successfully",
                "user_id": "ODJODO20220001",
                "check_out_time": "2026-01-03T18:00:00",
                "total_hours": 9.0,
            }
        }
    )


class SalaryConfigResponse(BaseModel):
    """Salary configuration response for Phase 3"""
    message: str
    user_id: str
    monthly_wage: float
    yearly_wage: float
    working_days_per_week: int
    breakdown: List[SalaryComponent]  # Earnings
    deductions: SalaryDeductions
    summary: Optional[dict] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Salary configured successfully",
                "user_id": "ODJODO20220001",
                "monthly_wage": 50000.0,
                "yearly_wage": 600000.0,
                "working_days_per_week": 5,
                "breakdown": [
                    {"name": "Basic", "type": "PERCENTAGE_OF_WAGE", "value": 50.0, "calculated_amount": 25000.0},
                ],
                "deductions": {"provident_fund": 3000.0, "professional_tax": 200.0},
                "summary": {"total_earnings": 50000.0, "total_deductions": 3200.0},
            }
        }
    )


class LeaveApplyResponse(BaseModel):
    """Leave application response"""
    message: str
    leave_id: str
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Leave request submitted successfully",
                "leave_id": "507f1f77bcf86cd799439011",
                "status": "PENDING",
            }
        }
    )

