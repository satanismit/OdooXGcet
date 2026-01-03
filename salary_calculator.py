"""
Salary Calculator for Phase 3 - Dayflow HRMS
Implements exact payroll calculations with proper deductions
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple
from models import SalaryComponent, SalaryComponentType, SalaryDeductions


def calculate_payroll_structure(monthly_wage: float) -> Tuple[List[SalaryComponent], SalaryDeductions]:
    """
    Calculate complete payroll structure based on monthly wage.
    
    Earnings Formula (Phase 3 - Correct):
    1. Basic Salary: 50% of Monthly Wage
    2. HRA: 50% of Basic Salary (NOT Wage)
    3. Standard Allowance: Fixed 4167.00
    4. Performance Bonus: 8.33% of Basic Salary (NOT Wage)
    5. LTA: 8.33% of Basic Salary (NOT Wage)
    6. Fixed Allowance: Balancing figure to match Monthly Wage exactly
    
    Deductions (not subtracted from wage total):
    1. Provident Fund (PF): 12% of Basic Salary
    2. Professional Tax: Fixed 200.00
    
    Args:
        monthly_wage: Total monthly wage amount
        
    Returns:
        Tuple of (earnings_components, deductions)
        
    Raises:
        ValueError: If calculations don't sum to monthly wage
    """
    # Use Decimal for exact calculations
    wage = Decimal(str(monthly_wage))
    
    # Standard fixed values
    standard_allowance = Decimal("4167.00")
    professional_tax = Decimal("200.00")
    
    # Step 1: Calculate Basic Salary (50% of Monthly Wage)
    basic = (wage * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Step 2: Calculate HRA (50% of Basic Salary)
    hra = (basic * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Step 3: Calculate Performance Bonus (8.33% of Basic Salary)
    performance_bonus = (basic * Decimal("0.0833")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Step 4: Calculate LTA (8.33% of Basic Salary)
    lta = (basic * Decimal("0.0833")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Step 5: Calculate Fixed Allowance (balancing figure)
    # Formula: Monthly Wage - (Basic + HRA + StdAllow + PerfBonus + LTA)
    fixed_allowance = wage - (basic + hra + standard_allowance + performance_bonus + lta)
    fixed_allowance = fixed_allowance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Deductions Calculation
    # PF: 12% of Basic Salary
    pf = (basic * Decimal("0.12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Create earnings components
    earnings = [
        SalaryComponent(
            name="Basic Salary",
            type=SalaryComponentType.PERCENTAGE_OF_WAGE,
            value=50.0,
            calculated_amount=float(basic)
        ),
        SalaryComponent(
            name="House Rent Allowance",
            type=SalaryComponentType.PERCENTAGE_OF_BASIC,
            value=50.0,
            calculated_amount=float(hra)
        ),
        SalaryComponent(
            name="Standard Allowance",
            type=SalaryComponentType.FIXED_AMOUNT,
            value=4167.0,
            calculated_amount=float(standard_allowance)
        ),
        SalaryComponent(
            name="Performance Bonus",
            type=SalaryComponentType.PERCENTAGE_OF_BASIC,
            value=8.33,
            calculated_amount=float(performance_bonus)
        ),
        SalaryComponent(
            name="Leave Travel Allowance",
            type=SalaryComponentType.PERCENTAGE_OF_BASIC,
            value=8.33,
            calculated_amount=float(lta)
        ),
        SalaryComponent(
            name="Fixed Allowance",
            type=SalaryComponentType.FIXED_AMOUNT,
            value=float(fixed_allowance),
            calculated_amount=float(fixed_allowance)
        ),
    ]
    
    # Create deductions object
    deductions = SalaryDeductions(
        provident_fund=float(pf),
        professional_tax=float(professional_tax)
    )
    
    # Final verification: sum must equal monthly wage
    total_earnings = sum(c.calculated_amount for c in earnings)
    assert abs(float(total_earnings) - float(monthly_wage)) < 0.01, (
        f"Calculation error: {total_earnings} != {monthly_wage}"
    )
    
    return earnings, deductions


def verify_payroll_structure(
    monthly_wage: float,
    earnings: List[SalaryComponent],
    deductions: SalaryDeductions
) -> bool:
    """
    Verify that payroll calculations are correct.
    
    Args:
        monthly_wage: Expected monthly wage
        earnings: List of earning components
        deductions: Deductions structure
        
    Returns:
        True if calculations are valid
    """
    total_earnings = sum(c.calculated_amount for c in earnings)
    
    # Check earnings sum to monthly wage
    if abs(total_earnings - monthly_wage) >= 0.01:
        return False
    
    # Verify Basic is 50% of wage
    basic_component = next((c for c in earnings if c.name == "Basic Salary"), None)
    if not basic_component:
        return False
    
    expected_basic = monthly_wage * 0.50
    if abs(basic_component.calculated_amount - expected_basic) >= 0.01:
        return False
    
    # Verify HRA is 50% of Basic
    hra_component = next((c for c in earnings if c.name == "House Rent Allowance"), None)
    if not hra_component:
        return False
    
    expected_hra = basic_component.calculated_amount * 0.50
    if abs(hra_component.calculated_amount - expected_hra) >= 0.01:
        return False
    
    # Verify PF is 12% of Basic
    expected_pf = basic_component.calculated_amount * 0.12
    if abs(deductions.provident_fund - expected_pf) >= 0.01:
        return False
    
    # Verify Professional Tax is 200
    if abs(deductions.professional_tax - 200.0) >= 0.01:
        return False
    
    return True


def get_payroll_summary(earnings: List[SalaryComponent], deductions: SalaryDeductions) -> dict:
    """
    Get a summary of payroll breakdown.
    
    Args:
        earnings: List of earning components
        deductions: Deductions structure
        
    Returns:
        Dictionary with summary information
    """
    total_earnings = sum(c.calculated_amount for c in earnings)
    total_deductions = deductions.provident_fund + deductions.professional_tax
    net_salary = total_earnings - total_deductions
    
    summary = {
        "total_earnings": round(total_earnings, 2),
        "total_deductions": round(total_deductions, 2),
        "net_salary": round(net_salary, 2),
    }
    
    # Add individual components
    for component in earnings:
        summary[component.name.lower().replace(" ", "_")] = component.calculated_amount
    
    summary["provident_fund"] = deductions.provident_fund
    summary["professional_tax"] = deductions.professional_tax
    
    return summary
