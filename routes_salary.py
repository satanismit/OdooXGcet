from datetime import datetime
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    User,
    UserRole,
    SalaryStructure,
    SalaryConfigRequest,
    SalaryConfigResponse,
    SalaryComponent,
    SalaryDeductions,
)
from routes import get_current_user, get_current_admin
from salary_utils import calculate_salary_breakdown, get_salary_summary


# Router
salary_router = APIRouter(prefix="/salary", tags=["Salary"])


@salary_router.post("/configure/{user_id}", response_model=SalaryConfigResponse)
async def configure_salary(
    user_id: str,
    request: SalaryConfigRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    Configure salary structure for an employee (Admin only).
    
    Automatically calculates salary components based on total wage:
    - Basic Salary: 50% of total wage
    - HRA: 50% of basic salary
    - Standard Allowance: Fixed amount (default 4167)
    - Performance Bonus: 8.33% of total wage
    - LTA: 8.333% of total wage
    - Fixed Allowance: Remaining amount (balancing component)
    
    The sum of all components equals the total wage exactly.
    """
    # Validate total wage is positive
    if request.total_wage <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total wage must be a positive number"
        )
    
    # Check if employee exists
    employee = await User.find_one(User.login_id == user_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with login_id '{user_id}' not found"
        )
    
    # Calculate salary breakdown
    components = calculate_salary_breakdown(
        total_wage=Decimal(str(request.total_wage)),
        standard_allowance=Decimal(str(request.standard_allowance)) if request.standard_allowance else Decimal("4167"),
        performance_bonus_percent=Decimal(str(request.performance_bonus_percent)) if request.performance_bonus_percent else Decimal("8.33"),
        lta_percent=Decimal(str(request.lta_percent)) if request.lta_percent else Decimal("8.333")
    )
    
    # Check if salary structure already exists
    existing_salary = await SalaryStructure.find_one(
        SalaryStructure.user_id == user_id
    )
    
    if existing_salary:
        # Update existing structure
        existing_salary.monthly_wage = request.total_wage
        existing_salary.yearly_wage = request.total_wage * 12
        existing_salary.breakdown = components
        existing_salary.updated_at = datetime.utcnow()
        existing_salary.configured_by = current_admin.login_id
        await existing_salary.save()
        salary_structure = existing_salary
    else:
        # Create new structure
        salary_structure = SalaryStructure(
            user_id=user_id,
            monthly_wage=request.total_wage,
            yearly_wage=request.total_wage * 12,
            breakdown=components,
            configured_by=current_admin.login_id
        )
        await salary_structure.insert()
    
    # Get summary for response
    summary = get_salary_summary(components)
    
    # Create default deductions for the response
    basic_salary = next((c.calculated_amount for c in components if c.name == "Basic"), 0)
    default_deductions = SalaryDeductions(
        provident_fund=basic_salary * 0.12,
        professional_tax=200.0
    )

    return SalaryConfigResponse(
        message="Salary configured successfully",
        user_id=user_id,
        monthly_wage=request.total_wage,
        yearly_wage=request.total_wage * 12,
        working_days_per_week=5,  # Default
        breakdown=components,
        deductions=default_deductions,
        summary=summary
    )


@salary_router.get("/{user_id}", response_model=SalaryConfigResponse)
async def get_salary_structure(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get salary structure for an employee.
    
    Authorization:
    - Admins can view any employee's salary
    - Regular employees can only view their own salary
    """
    # Check authorization
    if current_user.role != UserRole.ADMIN and current_user.login_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this salary information"
        )
    
    # Get salary structure
    salary_structure = await SalaryStructure.find_one(
        SalaryStructure.user_id == user_id
    )
    
    if not salary_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salary structure not found for user '{user_id}'"
        )
    
    # Get summary
    summary = get_salary_summary(salary_structure.breakdown)
    
    # Create default deductions if none exist
    deductions = salary_structure.deductions
    if not deductions:
        # Default deductions: 12% PF of basic salary + 200 PT
        basic_salary = next((c.calculated_amount for c in salary_structure.breakdown if c.name == "Basic"), 0)
        deductions = SalaryDeductions(
            provident_fund=basic_salary * 0.12,
            professional_tax=200.0
        )

    return SalaryConfigResponse(
        message="Salary structure retrieved successfully",
        user_id=user_id,
        monthly_wage=salary_structure.monthly_wage,
        yearly_wage=salary_structure.yearly_wage,
        working_days_per_week=salary_structure.working_days_per_week,
        breakdown=salary_structure.breakdown,
        deductions=deductions,
        summary=summary
    )


@salary_router.get("/", response_model=List[dict])
async def list_all_salaries(
    current_admin: User = Depends(get_current_admin)
):
    """
    List all salary structures (Admin only).
    
    Returns a summary of all configured salaries.
    """
    salary_structures = await SalaryStructure.find_all().to_list()
    
    result = []
    for salary in salary_structures:
        # Get employee details
        employee = await User.find_one(User.login_id == salary.user_id)
        
        result.append({
            "user_id": salary.user_id,
            "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
            "total_wage": salary.total_wage,
            "configured_by": salary.configured_by,
            "updated_at": salary.updated_at.isoformat()
        })
    
    return result
