# Quick Start Guide - Dayflow HRMS

## Fast Setup (5 minutes)

### 1. Install Dependencies

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Environment

```powershell
# Create .env file
copy .env.example .env

# Edit .env with your MongoDB connection (if not using defaults)
```

### 3. Start MongoDB (if not already running)

**Using Docker:**
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Or install MongoDB locally from:** https://www.mongodb.com/try/download/community

### 4. Run the Application

```powershell
python main.py
```

Visit: http://localhost:8000/docs

---

## Testing the API (Step by Step)

### Step 1: Register a Company Admin

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "email": "admin@techcorp.com",
    "password": "SecurePass123",
    "first_name": "Alice",
    "last_name": "Johnson"
  }'
```

**Expected Response:**
```json
{
  "message": "Company admin registered successfully",
  "login_id": "TEALJO20260001",
  "email": "admin@techcorp.com",
  "role": "ADMIN"
}
```

### Step 2: Login as Admin

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id_or_email": "TEALJO20260001",
    "password": "SecurePass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "login_id": "TEALJO20260001",
  "email": "admin@techcorp.com",
  "role": "ADMIN"
}
```

**Save the `access_token` for next step!**

### Step 3: Create an Employee (as Admin)

```bash
curl -X POST "http://localhost:8000/admin/create-employee" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob.smith@techcorp.com",
    "joining_date": "2026-01-15T00:00:00"
  }'
```

**Expected Response:**
```json
{
  "message": "Employee created successfully",
  "login_id": "TEBOSM20260001",
  "email": "bob.smith@techcorp.com",
  "temporary_password": "Xy4$kL9p!2Qz",
  "role": "EMPLOYEE"
}
```

### Step 4: Login as Employee

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id_or_email": "TEBOSM20260001",
    "password": "Xy4$kL9p!2Qz"
  }'
```

---

## Running Tests

```powershell
# Run all tests
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestLoginIDGeneration -v

# Run with output
pytest test_main.py -v -s
```

---

## Using Swagger UI (Recommended for Testing)

1. Start the server: `python main.py`
2. Open browser: http://localhost:8000/docs
3. Use the interactive UI to test all endpoints
4. Click "Authorize" button to add your JWT token

---

## Project File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, MongoDB setup, route registration |
| `models.py` | Pydantic models for request/response and Beanie documents |
| `routes.py` | API endpoint handlers (signup, login, create employee) |
| `utils.py` | Login ID generation, password hashing, JWT utilities |
| `config.py` | Environment configuration using pydantic-settings |
| `test_main.py` | Comprehensive pytest test suite |

---

## Key Features Implemented

✅ **Unique Login ID Generation**
   - Format: `[CompanyCode][NameCode][Year][Serial]`
   - Example: `TEALJO20260001`
   - Handles edge cases (short names, special chars, etc.)

✅ **Role-Based Access Control**
   - Admin can create employees
   - Employees cannot create other employees

✅ **Auto-generated Temporary Passwords**
   - Secure random passwords for new employees
   - Returned to admin for distribution

✅ **Flexible Login**
   - Login with either login_id OR email
   - JWT-based authentication

✅ **Comprehensive Tests**
   - 25+ test cases covering all scenarios
   - Edge cases and error handling

---

## Common Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Run server
python main.py

# Run tests
pytest test_main.py -v

# Check MongoDB connection
mongosh

# Deactivate virtual environment
deactivate
```

---

## Next Steps

1. **Add Password Reset**: Implement forgot password functionality
2. **Email Integration**: Send welcome emails with credentials
3. **Employee Profile**: Add endpoints to update user profiles
4. **Attendance System**: Expand to include check-in/check-out
5. **Leave Management**: Add leave request/approval system

---

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review test cases in [test_main.py](test_main.py)
- Inspect API documentation at http://localhost:8000/docs

---

**Happy Coding! 🚀**
