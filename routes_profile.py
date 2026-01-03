"""
Phase 4: Profile Management Routes
Handles Private Info and Security features for user profiles
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date
from models import User, PersonalDetails, BankDetails, Gender, MaritalStatus
from routes import get_current_user, get_current_admin
from utils import get_password_hash, verify_password


profile_router = APIRouter(prefix="/users", tags=["Profile Management"])


# ==================== REQUEST/RESPONSE MODELS ====================

class UpdatePrivateInfoRequest(BaseModel):
    """Request model for updating private information"""
    personal_details: Optional[PersonalDetails] = None
    bank_details: Optional[BankDetails] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "personal_details": {
                    "date_of_birth": "1990-05-15",
                    "gender": "Male",
                    "marital_status": "Single",
                    "current_address": "123 Main St, Mumbai",
                    "personal_email": "john.personal@gmail.com"
                },
                "bank_details": {
                    "bank_name": "HDFC Bank",
                    "account_number": "12345678901234",
                    "ifsc_code": "HDFC0001234",
                    "pan_number": "ABCDE1234F",
                    "uan_number": "123456789012"
                }
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    """Request model for changing password"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPassword123",
                "new_password": "NewSecurePassword456",
                "confirm_new_password": "NewSecurePassword456"
            }
        }
    )


class FullProfileResponse(BaseModel):
    """Response model for full user profile"""
    login_id: str
    email: str
    first_name: str
    last_name: str
    company_name: str
    role: str
    joining_date: str
    personal_details: Optional[PersonalDetails] = None
    bank_details: Optional[BankDetails] = None


# ==================== ENDPOINTS ====================

@profile_router.patch("/me/private-info", status_code=200)
async def update_private_info(
    request: UpdatePrivateInfoRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update the logged-in user's personal and bank details.
    
    - **Access**: Authenticated User (Employee or Admin)
    - **Action**: Allows user to fill in or update their own private information
    - **Validation**: Ensures email, PAN, IFSC formats are valid
    """
    # Update personal details if provided
    if request.personal_details is not None:
        current_user.personal_details = request.personal_details
    
    # Update bank details if provided
    if request.bank_details is not None:
        current_user.bank_details = request.bank_details
    
    # Save to database
    await current_user.save()
    
    return {
        "message": "Private information updated successfully",
        "login_id": current_user.login_id,
        "personal_details": current_user.personal_details,
        "bank_details": current_user.bank_details
    }


@profile_router.post("/me/change-password", status_code=200)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Change the logged-in user's password.
    
    - **Access**: Authenticated User
    - **Validation**: 
        - Current password must match DB hash
        - New password must match confirmation
        - New password must be at least 8 characters
    """
    # Step 1: Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Step 2: Verify new password matches confirmation
    if request.new_password != request.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )
    
    # Step 3: Verify new password is different from current
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Step 4: Hash and update password
    current_user.hashed_password = get_password_hash(request.new_password)
    await current_user.save()
    
    return {
        "message": "Password changed successfully",
        "login_id": current_user.login_id
    }


@profile_router.get("/{user_id}/full-profile", response_model=FullProfileResponse)
async def get_full_profile(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get full profile including private information.
    
    - **Access**: Admin OR The User themselves (Strict RBAC)
    - **Security**: User A cannot view User B's profile (403 Forbidden)
    - **Returns**: Complete user profile with personal and bank details
    """
    # Fetch the target user
    target_user = await User.find_one(User.login_id == user_id)
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with login_id '{user_id}' not found"
        )
    
    # RBAC Check: Admin can view anyone, Employee can only view themselves
    if current_user.role != "ADMIN" and current_user.login_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this profile"
        )
    
    # Return full profile
    return FullProfileResponse(
        login_id=target_user.login_id,
        email=target_user.email,
        first_name=target_user.first_name,
        last_name=target_user.last_name,
        company_name=target_user.company_name,
        role=target_user.role,
        joining_date=target_user.joining_date.isoformat(),
        personal_details=target_user.personal_details,
        bank_details=target_user.bank_details
    )
