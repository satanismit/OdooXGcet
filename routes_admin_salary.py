"""
Phase 3 Salary Routes - Admin Only
Implements salary configuration with proper authorization
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    User,
    UserRole,
    SalaryStructure,
    SalaryConfigRequest,
    SalaryConfigResponse,
)
from routes import get_current_user, get_current_admin
from salary_calculator import calculate_payroll_structure, get_payroll_summary


# Router
admin_salary_router = APIRouter(prefix="/admin/salary", tags=["Admin Salary"])


@admin_salary_router.put("/{employee_id}", response_model=SalaryConfigResponse)
async def configure_employee_salary(
    employee_id: str,
    request: SalaryConfigRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    Configure salary structure for an employee (Admin Only).
    
    Automatically calculates the breakdown:
    - Basic Salary: 50% of Monthly Wage
    - HRA: 50% of Basic Salary
    - Standard Allowance: Fixed 4167
    - Performance Bonus: 8.33% of Basic Salary
    - LTA: 8.33% of Basic Salary
    - Fixed Allowance: Balancing figure
    
    Deductions:
    - Provident Fund: 12% of Basic Salary
    - Professional Tax: Fixed 200
    
    The sum of all earnings equals the Monthly Wage exactly.
    """
    # Check if employee exists
    employee = await User.find_one(User.login_id == employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with login_id '{employee_id}' not found"
        )
    
    # Calculate payroll structure
    earnings, deductions = calculate_payroll_structure(request.monthly_wage)
    
    # Calculate yearly wage
    yearly_wage = request.monthly_wage * 12
    
    # Check if salary structure already exists
    existing_salary = await SalaryStructure.find_one(
        SalaryStructure.user_id == employee_id
    )
    
    if existing_salary:
        # Update existing structure
        existing_salary.monthly_wage = request.monthly_wage
        existing_salary.yearly_wage = yearly_wage
        existing_salary.working_days_per_week = request.working_days_per_week
        existing_salary.breakdown = earnings
        existing_salary.deductions = deductions
        existing_salary.updated_at = datetime.utcnow()
        existing_salary.configured_by = current_admin.login_id
        await existing_salary.save()
        salary_structure = existing_salary
    else:
        # Create new structure
        salary_structure = SalaryStructure(
            user_id=employee_id,
            monthly_wage=request.monthly_wage,
            yearly_wage=yearly_wage,
            working_days_per_week=request.working_days_per_week,
            breakdown=earnings,
            deductions=deductions,
            configured_by=current_admin.login_id
        )
        await salary_structure.insert()
    
    # Get summary for response
    summary = get_payroll_summary(earnings, deductions)
    
    return SalaryConfigResponse(
        message="Salary configured successfully",
        user_id=employee_id,
        monthly_wage=request.monthly_wage,
        yearly_wage=yearly_wage,
        working_days_per_week=request.working_days_per_week,
        breakdown=earnings,
        deductions=deductions,
        summary=summary
    )


@admin_salary_router.get("/{employee_id}", response_model=SalaryConfigResponse)
async def get_employee_salary(
    employee_id: str,
    current_admin: User = Depends(get_current_admin)
):
    """
    Get salary structure for an employee (Admin Only).
    
    Regular employees cannot access this endpoint (403 Forbidden).
    Only admins can view salary details.
    """
    # Get salary structure
    salary_structure = await SalaryStructure.find_one(
        SalaryStructure.user_id == employee_id
    )
    
    if not salary_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salary structure not found for user '{employee_id}'"
        )
    
    # Get summary
    summary = get_payroll_summary(salary_structure.breakdown, salary_structure.deductions)
    
    return SalaryConfigResponse(
        message="Salary structure retrieved successfully",
        user_id=employee_id,
        monthly_wage=salary_structure.monthly_wage,
        yearly_wage=salary_structure.yearly_wage,
        working_days_per_week=salary_structure.working_days_per_week,
        breakdown=salary_structure.breakdown,
        deductions=salary_structure.deductions,
        summary=summary
    )


@admin_salary_router.get("/", response_model=List[dict])
async def list_all_employee_salaries(
    current_admin: User = Depends(get_current_admin)
):
    """
    List all salary structures (Admin Only).
    
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
            "monthly_wage": salary.monthly_wage,
            "yearly_wage": salary.yearly_wage,
            "configured_by": salary.configured_by,
            "updated_at": salary.updated_at.isoformat()
        })
    
    return result
