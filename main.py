from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import User, Attendance, Leave, SalaryStructure
from routes import auth_router, admin_router
from routes_attendance import attendance_router, dashboard_router, leave_router
from routes_salary import salary_router
from routes_admin_salary import admin_salary_router
from routes_profile import profile_router
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
        document_models=[User, Attendance, Leave, SalaryStructure]
    )
    
    print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
    
    yield
    
    # Shutdown: Close MongoDB connection
    client.close()
    print("❌ Closed MongoDB connection")


# Create FastAPI app
app = FastAPI(
    title="Dayflow HRMS",
    description="Complete HRMS API with Authentication, Attendance, Leave Management, Payroll, and Profile Management",
    version="4.0.0",
    lifespan=lifespan,
)


# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(attendance_router)
app.include_router(dashboard_router)
app.include_router(leave_router)
app.include_router(salary_router)
app.include_router(admin_salary_router)
app.include_router(profile_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to Dayflow HRMS API",
        "status": "running",
        "version": "4.0.0",
        "modules": ["Authentication", "Attendance", "Leave Management", "Payroll", "Admin Salary Configuration", "Profile Management"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
