from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import User, Attendance, Leave, LeaveBalance, SalaryStructure, Payslip
from routes import auth_router, admin_router
from routes_attendance import attendance_router, dashboard_router  # Removed phase2 leave_router
from routes_salary import salary_router
from routes_admin_salary import admin_salary_router
from routes_profile import profile_router, frontend_profile_router
from routes_analytics import analytics_router
from routes_payroll import payroll_router
from routes_leaves import leave_router  # Phase 6: Complete Leave Management
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup: Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize Beanie with all document models
    await init_beanie(
        database=database, 
        document_models=[User, Attendance, Leave, LeaveBalance, SalaryStructure, Payslip]
    )
    
    print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
    
    yield
    
    # Shutdown: Close MongoDB connection
    client.close()
    print("❌ Closed MongoDB connection")


# Create FastAPI app
app = FastAPI(
    title="Dayflow HRMS",
    description="Complete HRMS API with Authentication, Attendance, Leave Management with Balances, Payroll, Analytics, and Profile Management",
    version="6.0.0",
    lifespan=lifespan,
)


# ========================================
# CORS CONFIGURATION - Frontend Integration
# ========================================
# Allow React frontend to communicate with FastAPI backend
origins = [
    "http://localhost:3000",      # React Dev Server (Create React App)
    "http://localhost:3001",      # React Dev Server (fallback)
    "http://localhost:5173",      # Vite Dev Server
    "http://127.0.0.1:3000",      # Alternative localhost
    "http://127.0.0.1:3001",      # Alternative localhost (fallback)
    "http://127.0.0.1:5173",      # Alternative Vite
    "http://localhost:4173",      # Vite Preview
    # Add your production domain here when deploying
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Allowed origins
    allow_credentials=True,        # Allow cookies/auth headers
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allow all headers (Authorization, Content-Type, etc.)
)


# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(attendance_router)
app.include_router(dashboard_router)
# Removed phase2_leave_router to avoid conflicts with comprehensive leave_router
app.include_router(salary_router)
app.include_router(admin_salary_router)
app.include_router(profile_router)
app.include_router(frontend_profile_router)  # Frontend-compatible profile routes
app.include_router(analytics_router)
app.include_router(payroll_router)
app.include_router(leave_router)  # Phase 6: Complete Leave Management


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to Dayflow HRMS API",
        "status": "running",
        "version": "6.0.0",
        "modules": ["Authentication", "Attendance", "Leave Management with Balances", "Payroll", "Admin Salary Configuration", "Profile Management", "Attendance Analytics", "Payslip Generation"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
