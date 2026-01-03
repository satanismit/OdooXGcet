from decimal import Decimal, ROUND_HALF_UP
from typing import List
from models import SalaryComponent, SalaryComponentType


def calculate_salary_breakdown(
    total_wage: float,
    standard_allowance: float = 4167.0,
    performance_bonus_percent: float = 8.33,
    lta_percent: float = 8.333
) -> List[SalaryComponent]:
    """
    Calculate salary breakdown with exact mathematical precision.
    
    The formula follows these rules:
    1. Basic = 50% of Total Wage
    2. HRA = 50% of Basic (NOT total wage)
    3. Standard Allowance = Fixed amount (default 4167)
    4. Performance Bonus = Percentage of Total Wage (default 8.33%)
    5. LTA (Leave Travel Allowance) = Percentage of Total Wage (default 8.333%)
    6. Fixed Allowance = Remaining balance to match Total Wage exactly
    
    Args:
        total_wage: The total wage to be distributed
        standard_allowance: Fixed standard allowance amount
        performance_bonus_percent: Performance bonus as percentage of total wage
        lta_percent: LTA as percentage of total wage
    
    Returns:
        List of SalaryComponent objects with exact calculations
        
    Raises:
        ValueError: If total_wage is negative or zero
    """
    if total_wage <= 0:
        raise ValueError("Total wage must be positive")
    
    # Use Decimal for precise financial calculations
    total = Decimal(str(total_wage))
    std_allow = Decimal(str(standard_allowance))
    perf_bonus_pct = Decimal(str(performance_bonus_percent))
    lta_pct = Decimal(str(lta_percent))
    
    # Calculate each component with 2 decimal precision
    # 1. Basic = 50% of Total Wage
    basic = (total * Decimal('0.50')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # 2. HRA = 50% of Basic (NOT total wage)
    hra = (basic * Decimal('0.50')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # 3. Standard Allowance = Fixed
    standard_allowance_amt = std_allow.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # 4. Performance Bonus = X% of Total Wage
    performance_bonus = (total * perf_bonus_pct / Decimal('100')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    
    # 5. LTA = X% of Total Wage
    lta = (total * lta_pct / Decimal('100')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    
    # 6. Fixed Allowance = Remaining to balance Total Wage
    # This is the balancing component
    fixed_allowance = total - (basic + hra + standard_allowance_amt + performance_bonus + lta)
    fixed_allowance = fixed_allowance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Verify the sum equals total wage (should be exact)
    calculated_total = basic + hra + standard_allowance_amt + performance_bonus + lta + fixed_allowance
    
    # If there's any rounding difference, adjust the fixed allowance
    if calculated_total != total:
        difference = total - calculated_total
        fixed_allowance += difference
    
    # Convert Decimal back to float for storage
    components = [
        SalaryComponent(
            name="Basic",
            type=SalaryComponentType.PERCENTAGE_OF_WAGE,
            value=50.0,
            calculated_amount=float(basic)
        ),
        SalaryComponent(
            name="HRA",
            type=SalaryComponentType.PERCENTAGE_OF_BASIC,
            value=50.0,
            calculated_amount=float(hra)
        ),
        SalaryComponent(
            name="Standard Allowance",
            type=SalaryComponentType.FIXED_AMOUNT,
            value=float(std_allow),
            calculated_amount=float(standard_allowance_amt)
        ),
        SalaryComponent(
            name="Performance Bonus",
            type=SalaryComponentType.PERCENTAGE_OF_WAGE,
            value=float(perf_bonus_pct),
            calculated_amount=float(performance_bonus)
        ),
        SalaryComponent(
            name="Leave Travel Allowance",
            type=SalaryComponentType.PERCENTAGE_OF_WAGE,
            value=float(lta_pct),
            calculated_amount=float(lta)
        ),
        SalaryComponent(
            name="Fixed Allowance",
            type=SalaryComponentType.FIXED_AMOUNT,
            value=float(fixed_allowance),
            calculated_amount=float(fixed_allowance)
        ),
    ]
    
    # Final verification: sum must equal total wage
    total_calculated = sum(c.calculated_amount for c in components)
    assert abs(float(total_calculated) - float(total_wage)) < 0.01, (
        f"Calculation error: {total_calculated} != {total_wage}"
    )
    
    return components


def verify_salary_components(components: List[SalaryComponent], expected_total: float) -> bool:
    """
    Verify that salary components sum to expected total.
    
    Args:
        components: List of salary components
        expected_total: Expected total wage
    
    Returns:
        True if sum matches expected total (within 0.01 tolerance)
    """
    actual_total = sum(c.calculated_amount for c in components)
    return abs(actual_total - expected_total) < 0.01


def get_salary_summary(components: List[SalaryComponent]) -> dict:
    """
    Get a summary of salary breakdown.
    
    Args:
        components: List of salary components
    
    Returns:
        Dictionary with component names, amounts, and total
    """
    summary = {
        component.name: component.calculated_amount
        for component in components
    }
    summary["total_calculated"] = sum(c.calculated_amount for c in components)
    return summary
