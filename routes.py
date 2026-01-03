from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import (
    User,
    UserRole,
    SignupRequest,
    SignupResponse,
    CreateEmployeeRequest,
    CreateEmployeeResponse,
    LoginRequest,
    LoginResponse,
)
from utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_login_id,
    generate_temporary_password,
)
from config import settings


# Security
security = HTTPBearer()

# Routers
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    login_id = decode_access_token(token)
    
    if login_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await User.find_one(User.login_id == login_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user has ADMIN role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required.",
        )
    return current_user


# Auth Routes
@auth_router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new company admin.
    
    This is the first user for a company and will have ADMIN role.
    The login_id is auto-generated based on company and user details.
    """
    # Check if email already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Generate login ID
    joining_date = datetime.utcnow()
    login_id = await generate_login_id(
        company_name=request.company_name,
        first_name=request.first_name,
        last_name=request.last_name,
        joining_date=joining_date,
    )
    
    # Check if login_id already exists (very rare, but handle it)
    existing_login = await User.find_one(User.login_id == login_id)
    if existing_login:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login ID generation conflict. Please try again.",
        )
    
    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        login_id=login_id,
        email=request.email,
        hashed_password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        company_name=request.company_name,
        role=UserRole.ADMIN,
        joining_date=joining_date,
    )
    
    await user.insert()
    
    return SignupResponse(
        message="Company admin registered successfully",
        login_id=user.login_id,
        email=user.email,
        role=user.role.value,
    )


@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user and return a JWT access token.
    
    Accepts either login_id or email along with password.
    """
    # Try to find user by login_id or email
    user = await User.find_one(
        {"$or": [
            {"login_id": request.login_id_or_email},
            {"email": request.login_id_or_email}
        ]}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login_id},
        expires_delta=access_token_expires,
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        login_id=user.login_id,
        email=user.email,
        role=user.role.value,
    )


# Admin Routes
@admin_router.post(
    "/create-employee",
    response_model=CreateEmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
    request: CreateEmployeeRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new employee (Admin only).
    
    Generates a temporary password and login_id for the employee.
    Returns both so the admin can provide them to the employee.
    """
    # Check if email already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Generate login ID using the admin's company name
    login_id = await generate_login_id(
        company_name=current_admin.company_name,
        first_name=request.first_name,
        last_name=request.last_name,
        joining_date=request.joining_date,
    )
    
    # Check if login_id already exists
    existing_login = await User.find_one(User.login_id == login_id)
    if existing_login:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login ID generation conflict. Please try again.",
        )
    
    # Generate temporary password
    temp_password = generate_temporary_password()
    hashed_password = get_password_hash(temp_password)
    
    # Create employee
    employee = User(
        login_id=login_id,
        email=request.email,
        hashed_password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        company_name=current_admin.company_name,
        role=UserRole.EMPLOYEE,
        joining_date=request.joining_date,
    )
    
    await employee.insert()
    
    return CreateEmployeeResponse(
        message="Employee created successfully",
        login_id=employee.login_id,
        email=employee.email,
        temporary_password=temp_password,
        role=employee.role.value,
    )
