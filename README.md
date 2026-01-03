# Dayflow HRMS - Authentication & User Onboarding

A FastAPI-based Human Resource Management System with MongoDB backend, implementing secure authentication and user onboarding functionality.

## Features

- ✅ **JWT-based Authentication**
- ✅ **Unique Login ID Generation** (Company-based format)
- ✅ **Role-based Access Control** (Admin & Employee)
- ✅ **Auto-generated Temporary Passwords**
- ✅ **MongoDB with Beanie ODM**
- ✅ **Comprehensive Test Suite**

## Project Structure

```
OdooXGcet/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models and MongoDB documents
├── routes.py            # API route handlers
├── utils.py             # Utility functions (login_id generation, JWT, passwords)
├── config.py            # Configuration settings
├── test_main.py         # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.9+
- MongoDB (running locally or remote)

### Setup Steps

1. **Clone or navigate to the project directory**

```powershell
cd c:\Users\Admin\OneDrive\Desktop\odduBackend\OdooXGcet
```

2. **Create a virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and update the values:

```powershell
copy .env.example .env
```

Edit `.env`:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=dayflow_hrms
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Ensure MongoDB is running**

Make sure MongoDB is running on your system. If using Docker:

```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Running the Application

Start the FastAPI server:

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Authentication

#### 1. Company Admin Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "company_name": "Ode",
  "email": "admin@ode.com",
  "password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "message": "Company admin registered successfully",
  "login_id": "ODJODO20260001",
  "email": "admin@ode.com",
  "role": "ADMIN"
}
```

#### 2. Login
```http
POST /auth/login
Content-Type: application/json

{
  "login_id_or_email": "ODJODO20260001",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "login_id": "ODJODO20260001",
  "email": "admin@ode.com",
  "role": "ADMIN"
}
```

### Admin Operations

#### 3. Create Employee (Admin Only)
```http
POST /admin/create-employee
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@ode.com",
  "joining_date": "2026-01-15T00:00:00"
}
```

**Response:**
```json
{
  "message": "Employee created successfully",
  "login_id": "ODJASM20260001",
  "email": "jane.smith@ode.com",
  "temporary_password": "TempPass123!",
  "role": "EMPLOYEE"
}
```

## Login ID Generation Logic

The system auto-generates unique login IDs with the format:

**[CompanyCode][NameCode][Year][Serial]**

### Components:
- **CompanyCode**: First 2 letters of company name (uppercase)
- **NameCode**: First 2 letters of first name + first 2 letters of last name (uppercase)
- **Year**: 4-digit joining year
- **Serial**: 4-digit incremental number (0001, 0002, etc.)

### Examples:
- Company: "Ode", User: "John Doe", Year: 2022 → `ODJODO20220001`
- Company: "Ode", User: "Jane Smith", Year: 2026 → `ODJASM20260001`

### Edge Cases Handled:
- **Short names** (< 2 chars): Padded with 'X'
  - "O" → "OX"
- **Spaces**: Removed
  - "Jo hn" → "JOHN"
- **Numbers/Special chars**: Removed
  - "John123" → "JOHN"

## Running Tests

Execute the comprehensive test suite:

```powershell
pytest test_main.py -v
```

Run with coverage:

```powershell
pytest test_main.py --cov=. --cov-report=html
```

### Test Coverage

The test suite includes:

✅ **Login ID Generation Tests**
- Normal input validation
- Short name padding
- Space and special character handling
- Serial number incrementing
- Year-based serial reset

✅ **Authentication Flow Tests**
- Signup success/failure
- Login with login_id
- Login with email
- Password validation
- Token generation

✅ **Employee Creation Tests**
- Admin-only access
- Serial number incrementing
- Generated credentials validation
- Employee login verification

✅ **Edge Cases**
- Duplicate email handling
- Invalid authentication attempts
- Role-based access control

## Security Features

- **Password Hashing**: bcrypt algorithm via passlib
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Admin and Employee roles with proper authorization
- **Unique Constraints**: Email and login_id uniqueness enforced

## Database Schema

### User Collection

```javascript
{
  _id: ObjectId,
  login_id: String (unique, indexed),
  email: String (unique, indexed),
  hashed_password: String,
  first_name: String,
  last_name: String,
  company_name: String,
  role: "ADMIN" | "EMPLOYEE",
  joining_date: DateTime,
  created_at: DateTime
}
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings

### Adding New Features
1. Define models in models.py
2. Add utilities in utils.py
3. Create routes in routes.py
4. Write tests in test_main.py

## Troubleshooting

### MongoDB Connection Issues
- Verify MongoDB is running: `mongosh` or check Docker container
- Check connection string in `.env`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Test Failures
- Ensure MongoDB is running
- Check that test database can be created/dropped

## License

MIT License

## Author

Senior Backend Developer - FastAPI & MongoDB Specialist