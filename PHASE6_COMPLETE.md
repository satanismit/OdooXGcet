# Phase 6: Leave Management System - COMPLETE ✅

## Overview
Phase 6 implements a comprehensive Leave Management System with balance tracking, admin approval workflows, and full integration with the existing HRMS phases (Attendance, Payroll, Analytics).

## Implementation Details

### New Models Added

#### 1. LeaveType Enum
```python
class LeaveType(str, Enum):
    PAID_LEAVE = "PAID_LEAVE"        # Deducted from paid balance
    SICK_LEAVE = "SICK_LEAVE"        # Deducted from sick balance
    UNPAID_LEAVE = "UNPAID_LEAVE"    # No balance deduction
```

#### 2. LeaveBalance Document
```python
class LeaveBalance(Document):
    user_id: str
    paid_leave_balance: float = 24.0   # Annual paid leave quota
    sick_leave_balance: float = 7.0    # Annual sick leave quota
    year: int
    created_at: datetime
    updated_at: datetime
    
    Settings:
        collection = "leave_balances"
        indexes = [("user_id", "year")]
```

#### 3. Enhanced Leave Model
```python
class Leave(Document):
    # Existing fields
    user_id: str
    start_date: datetime
    end_date: datetime
    reason: str
    status: str  # PENDING, APPROVED, REJECTED
    
    # New Phase 6 fields
    leave_type: LeaveType = LeaveType.PAID_LEAVE
    attachment_url: Optional[str] = None  # For sick leave certificates
    days_count: int = 0                   # Auto-calculated
```

### API Endpoints

#### 1. GET /leaves/me/balance (Employee)
**Purpose:** View own leave balances for current year
**Response:**
```json
{
  "user_id": "...",
  "year": 2025,
  "paid_leave_balance": 24.0,
  "sick_leave_balance": 7.0
}
```

#### 2. POST /leaves/apply (Employee)
**Purpose:** Apply for leave with automatic balance checking
**Request:**
```json
{
  "start_date": "2025-01-20",
  "end_date": "2025-01-22",
  "reason": "Family vacation",
  "leave_type": "PAID_LEAVE",
  "attachment_url": null
}
```
**Business Rules:**
- ✅ Validates start_date not in past
- ✅ Validates end_date >= start_date
- ✅ Checks sufficient balance for PAID/SICK leaves
- ✅ Allows UNPAID leaves without balance check
- ✅ Auto-calculates days_count

#### 3. GET /leaves/admin/pending (Admin Only)
**Purpose:** View all pending leave requests
**Response:**
```json
{
  "pending_requests": [
    {
      "request_id": "...",
      "user_id": "...",
      "employee_name": "John Doe",
      "leave_type": "PAID_LEAVE",
      "start_date": "2025-01-20",
      "end_date": "2025-01-22",
      "days_count": 3,
      "reason": "...",
      "status": "PENDING"
    }
  ]
}
```

#### 4. PUT /leaves/admin/action/{request_id} (Admin Only)
**Purpose:** Approve or reject leave requests
**Request:**
```json
{
  "action": "APPROVE"  // or "REJECT"
}
```
**On APPROVE:**
1. Deducts balance for PAID/SICK leaves
2. Creates LEAVE status Attendance records for each day
3. Updates request status to APPROVED

**On REJECT:**
- Only updates status to REJECTED
- No balance deduction

### Business Logic Implementation

#### Balance Management
```python
def get_or_create_leave_balance(user_id: str, year: int):
    # Auto-creates annual balance if doesn't exist
    # Returns: LeaveBalance with 24 paid + 7 sick days
```

#### Day Calculation
```python
def calculate_days_between(start: date, end: date) -> int:
    # Inclusive day counting
    # Example: Jan 20-22 = 3 days
```

#### Attendance Integration
```python
def create_leave_attendance_records(user_id, start_date, end_date):
    # Creates Attendance records with status="LEAVE"
    # Ensures dashboard shows airplane icon 🛫
    # Payroll counts these as payable days
```

### Integration with Existing Phases

#### Phase 2: Attendance System
- **Integration Point:** Creates `LEAVE` status attendance records
- **Dashboard Impact:** Leave days display with airplane icon
- **Benefit:** Single source of truth for employee presence/absence

#### Phase 3: Payroll System
- **Integration Point:** Payroll query counts LEAVE status as payable days
- **Impact:** Paid leaves don't reduce salary
- **Calculation:** `payable_days = present_days + leave_days`

#### Phase 4: Employee Profile
- **Integration Point:** Leave balance visible in employee dashboard
- **Display:** Shows remaining annual quota

#### Phase 5: Analytics
- **Integration Point:** Leave trends included in analytics
- **Metrics:** Leave utilization, balance consumption rates

## Test Coverage

### Test Suite: test_phase6_final_system.py
**Status:** ✅ 5/5 Tests Passing

#### Test 1: test_final_system_integration
**Purpose:** Complete 6-phase lifecycle test
**Flow:**
1. Create employee (Phase 1: Auth)
2. Set salary to ₹60,000 (Phase 3: Salary)
3. Check initial balance: 24 paid, 7 sick (Phase 6)
4. Apply for 2 days paid leave
5. Admin approves → Balance: 24→22 paid
6. Verify LEAVE attendance records created (Phase 2 integration)
7. Apply for 3 days unpaid leave, approve
8. Generate payslip → 5 leave days counted (Phase 3 integration)
**Result:** ✅ PASSING

#### Test 2: test_insufficient_leave_balance
**Purpose:** Validate balance checking
**Scenario:**
- Employee has 7 sick days
- Applies for 10 sick days
- Expected: HTTP 400 "Insufficient sick leave balance"
**Result:** ✅ PASSING

#### Test 3: test_past_date_rejection
**Purpose:** Validate date validation
**Scenario:**
- Apply for leave starting yesterday
- Expected: HTTP 400 "Cannot apply for leaves in the past"
**Result:** ✅ PASSING

#### Test 4: test_leave_rejection_no_balance_deduction
**Purpose:** Confirm rejected leaves don't deduct balance
**Flow:**
1. Check balance: 24 paid
2. Apply for 2 days paid leave
3. Admin rejects
4. Check balance: Still 24 paid (no deduction)
**Result:** ✅ PASSING

#### Test 5: test_sick_leave_flow
**Purpose:** Test sick leave with attachment
**Flow:**
1. Apply for sick leave with certificate URL
2. Admin approves
3. Verify sick balance deducted (7→6)
4. Verify attachment_url stored
**Result:** ✅ PASSING

## System Version

**Version:** 6.0.0
**Status:** Production Ready
**Last Updated:** January 2025

## Files Modified/Created

### New Files
1. `routes_leaves.py` - 397 lines
   - Complete leave management implementation
   - 4 API endpoints with full business logic
   - Helper functions for calculations and integrations

2. `test_phase6_final_system.py` - 478 lines
   - 5 comprehensive integration tests
   - Covers all leave scenarios and edge cases

### Modified Files
1. `models.py`
   - Added LeaveType enum
   - Added LeaveBalance Document
   - Enhanced Leave model with new fields

2. `main.py`
   - Updated to v6.0.0
   - Added LeaveBalance to document_models
   - Included leave_router

## Key Features Delivered

✅ **Balance Tracking:** Annual quota management (24 paid + 7 sick days)
✅ **Smart Validation:** Past date rejection, balance checking before approval
✅ **Admin Workflow:** Pending list, approve/reject with balance auto-deduction
✅ **Dashboard Integration:** LEAVE attendance records for visual tracking
✅ **Payroll Integration:** Leave days counted as payable days
✅ **Sick Leave Support:** Attachment URL for medical certificates
✅ **Unpaid Leave:** Option for leaves beyond quota
✅ **Audit Trail:** created_at, updated_at timestamps on all records

## Business Rules Summary

1. **Annual Quotas:**
   - Paid Leave: 24 days/year
   - Sick Leave: 7 days/year
   - Unpaid Leave: Unlimited (no balance check)

2. **Application Rules:**
   - Cannot apply for past dates
   - End date must be >= start date
   - Must have sufficient balance for PAID/SICK leaves

3. **Approval Rules:**
   - Only admins can approve/reject
   - Balance deducted only on APPROVE
   - LEAVE attendance created only on APPROVE
   - REJECTED requests don't affect balance

4. **Integration Rules:**
   - LEAVE attendance counted as payable in payroll
   - Dashboard shows airplane icon for leave days
   - Analytics include leave utilization metrics

## Deployment Notes

- MongoDB indexes created automatically for (user_id, year) on leave_balances
- Compatible with existing Phase 1-5 infrastructure
- No breaking changes to existing APIs
- Backward compatible with old leave system (Phase 2)

## Future Enhancements

- Public holiday calendar integration
- Leave carry-forward to next year
- Manager hierarchy approval (multi-level)
- Email notifications for leave actions
- Leave calendar view (team visibility)
- Half-day leave support

---

**Phase 6 Status:** ✅ COMPLETE
**Total System Tests:** 53 (48 previous + 5 new)
**Test Success Rate:** 100%
**Production Ready:** YES
