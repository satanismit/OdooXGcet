# 🚀 Deployment Guide - Dayflow HRMS v5.0.0

## ✅ Pre-Deployment Checklist

All systems verified and ready for deployment:
- ✅ 48/48 tests passing
- ✅ 28 API endpoints loaded
- ✅ All 5 phases integrated
- ✅ Database models verified
- ✅ Security implemented

---

## 🔧 Quick Start (Development)

### 1. Start MongoDB
```bash
# Make sure MongoDB is running on localhost:27017
# Or update MONGODB_URL in .env file
```

### 2. Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 4. Start the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the API
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

---

## 📝 Environment Configuration

### Required Environment Variables (.env)
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=dayflow_hrms

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=true
```

### Production Environment Variables
```env
# MongoDB Configuration (Use production MongoDB)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=dayflow_hrms_prod

# JWT Configuration (Generate strong secret key)
SECRET_KEY=use-strong-random-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
DEBUG=false
```

---

## 🔐 First Time Setup

### 1. Create Admin Account
```bash
POST http://localhost:8000/auth/signup
Content-Type: application/json

{
  "company_name": "Your Company Name",
  "email": "admin@yourcompany.com",
  "password": "SecurePassword123!",
  "first_name": "Admin",
  "last_name": "User"
}
```

### 2. Login and Get Token
```bash
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "login_id_or_email": "admin@yourcompany.com",
  "password": "SecurePassword123!"
}
```

### 3. Create First Employee
```bash
POST http://localhost:8000/admin/create-employee
Authorization: Bearer YOUR_ADMIN_TOKEN
Content-Type: application/json

{
  "email": "employee@yourcompany.com",
  "first_name": "John",
  "last_name": "Doe",
  "joining_date": "2026-01-03T00:00:00"
}
```

---

## 🌐 Production Deployment Options

### Option 1: Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t dayflow-hrms:5.0.0 .
docker run -p 8000:8000 --env-file .env dayflow-hrms:5.0.0
```

### Option 2: Cloud Deployment (Heroku)

**Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Deploy:**
```bash
heroku create dayflow-hrms
heroku config:set MONGODB_URL=your-mongodb-url
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

### Option 3: Cloud Deployment (AWS/DigitalOcean)

1. Set up VM instance
2. Install Python 3.13+
3. Clone repository
4. Install dependencies
5. Configure environment
6. Use systemd or supervisor for process management
7. Set up nginx as reverse proxy

---

## 🧪 Run Tests Before Deployment

```bash
# Run all critical tests
pytest test_phase2.py test_full_system.py test_phase4.py test_phase5_final.py -v

# Expected: 48/48 passing ✅

# Run specific ultimate test
pytest test_phase5_final.py::test_full_payroll_system_integration -v -s
```

---

## 📊 API Documentation

Once server is running, access interactive API documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔒 Security Recommendations

### Production Security
1. **Change SECRET_KEY:** Generate strong random secret
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Use HTTPS:** Enable SSL/TLS in production

3. **Database Security:**
   - Use MongoDB Atlas with authentication
   - Enable IP whitelisting
   - Use strong database passwords

4. **Environment Variables:**
   - Never commit .env file
   - Use environment variable management service

5. **CORS Configuration:** Add CORS middleware if needed
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourfrontend.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## 📈 Monitoring & Logging

### Add Logging (Recommended)
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Health Check Endpoint
Already available at:
- GET `/health` - Returns `{"status": "healthy"}`
- GET `/` - Returns version and modules info

---

## 🛠️ Maintenance Commands

### Database Backup
```bash
# Export MongoDB database
mongodump --uri="mongodb://localhost:27017/dayflow_hrms" --out=backup/

# Restore MongoDB database
mongorestore --uri="mongodb://localhost:27017/dayflow_hrms" backup/dayflow_hrms/
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Run Database Migrations
Currently using Beanie ODM which handles schema automatically.
For custom migrations, create migration scripts as needed.

---

## 📞 API Usage Examples

### Complete Workflow Example

#### 1. Admin Signs Up
```http
POST /auth/signup
{
  "company_name": "TechCorp",
  "email": "admin@techcorp.com",
  "password": "Admin@123",
  "first_name": "Admin",
  "last_name": "User"
}
```

#### 2. Admin Logs In
```http
POST /auth/login
{
  "login_id_or_email": "admin@techcorp.com",
  "password": "Admin@123"
}
Response: { "access_token": "eyJ...", ... }
```

#### 3. Admin Creates Employee
```http
POST /admin/create-employee
Authorization: Bearer eyJ...
{
  "email": "john@techcorp.com",
  "first_name": "John",
  "last_name": "Doe",
  "joining_date": "2026-01-03T00:00:00"
}
Response: { "login_id": "DAJODO20260001", "temporary_password": "...", ... }
```

#### 4. Admin Configures Salary
```http
PUT /admin/salary/DAJODO20260001
Authorization: Bearer eyJ...
{
  "monthly_wage": 60000.0
}
```

#### 5. Employee Logs In
```http
POST /auth/login
{
  "login_id_or_email": "DAJODO20260001",
  "password": "temporary_password_from_step_3"
}
```

#### 6. Employee Checks In
```http
POST /attendance/check-in
Authorization: Bearer employee_token
```

#### 7. Employee Checks Out
```http
POST /attendance/check-out
Authorization: Bearer employee_token
```

#### 8. Employee Views Stats
```http
GET /attendance/stats/me?month=01-2026
Authorization: Bearer employee_token
```

#### 9. Admin Generates Payslip
```http
POST /payroll/generate-slip/DAJODO20260001
Authorization: Bearer admin_token
{
  "month": "01-2026"
}
```

---

## 🎯 Performance Tuning

### Database Indexes
Already configured automatically via Beanie models:
- User: `login_id`, `email`
- Attendance: `user_id`, `date`
- Leave: `user_id`, `status`
- SalaryStructure: `user_id`
- Payslip: `user_id`, `month_year`

### Connection Pooling
MongoDB Motor automatically handles connection pooling.

### Caching (Future Enhancement)
Consider adding Redis caching for:
- Frequently accessed salary data
- User profile information
- Dashboard statistics

---

## 🐛 Troubleshooting

### Common Issues

**1. MongoDB Connection Failed**
- Check if MongoDB is running
- Verify MONGODB_URL in .env
- Check firewall settings

**2. Import Errors**
```bash
pip install --upgrade -r requirements.txt
```

**3. JWT Token Errors**
- Check SECRET_KEY is set
- Verify token hasn't expired
- Check Authorization header format: `Bearer <token>`

**4. Port Already in Use**
```bash
# Change port
uvicorn main:app --port 8001
```

**5. Database Not Found**
- MongoDB will auto-create database
- Check DATABASE_NAME in .env

---

## 📚 Additional Resources

### Documentation Files
- [README.md](README.md) - Project overview
- [PHASE5_COMPLETE.md](PHASE5_COMPLETE.md) - Phase 5 details
- [SYSTEM_TEST_REPORT.md](SYSTEM_TEST_REPORT.md) - Complete test report
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

### API Documentation
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 📞 Support & Contact

For issues or questions:
1. Check documentation files
2. Review test files for usage examples
3. Check API docs at /docs endpoint

---

## 🎉 Success Metrics

After deployment, verify:
- ✅ Health endpoint returns 200
- ✅ API docs accessible
- ✅ Admin can sign up and login
- ✅ Employee creation works
- ✅ Attendance check-in/out functional
- ✅ Payslip generation successful

---

**Deployment Guide Version:** 1.0  
**System Version:** 5.0.0  
**Last Updated:** January 3, 2026  
**Status:** Production Ready ✅
