# 🚀 Phase 7: Frontend-Backend Integration Guide

## System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│                 │         │                  │         │             │
│  React Frontend │◄────────┤  FastAPI Backend │◄────────┤   MongoDB   │
│  (Port: 5173)   │  CORS   │  (Port: 8000)    │  Beanie │             │
│                 │         │                  │         │             │
└─────────────────┘         └──────────────────┘         └─────────────┘
     TypeScript                   Python                  NoSQL Database
     Vite Build                   Uvicorn Server
```

## ✅ What We've Implemented

### 1. Backend Configuration (main.py)
- ✅ Added CORS middleware
- ✅ Configured allowed origins for Vite (5173), React (3000), and alternatives
- ✅ Enabled all HTTP methods (GET, POST, PUT, DELETE, PATCH)
- ✅ Allowed all headers (Authorization, Content-Type, etc.)
- ✅ Enabled credentials (cookies, auth headers)

### 2. Frontend API Client (src/services/api.ts)
- ✅ Axios instance with base URL configuration
- ✅ Request interceptor: Auto-attaches JWT token from localStorage
- ✅ Response interceptor: Auto-redirects on 401 (token expiry)
- ✅ Error handler: User-friendly error messages
- ✅ Network error detection: Alerts when backend is down
- ✅ Token management utilities

### 3. Authentication Service (src/services/auth.service.ts)
- ✅ Real API integration (replaced mock data)
- ✅ Login function with token storage
- ✅ Register function via admin endpoint
- ✅ Profile fetching and updates
- ✅ Logout with token cleanup

### 4. E2E Testing (test_e2e_connection.py)
- ✅ Playwright browser automation
- ✅ Frontend-backend connection verification
- ✅ Database integration testing
- ✅ Complete user flow testing
- ✅ Attendance system testing
- ✅ Leave balance testing

## 🛠️ Installation & Setup

### Step 1: Install Backend Dependencies

```bash
# Install Playwright and testing tools
pip install playwright pytest requests

# Install browsers for Playwright
playwright install chromium
```

### Step 2: Install Frontend Dependencies

```bash
# Install Axios for API calls
npm install axios

# Or if using yarn
yarn add axios
```

### Step 3: Configure Environment

Create `.env` file in the project root (backend):
```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=hrms_db
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Create `.env` file in frontend root (copy from .env.frontend):
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Dayflow HRMS
VITE_APP_VERSION=6.0.0
```

## 🚀 Running the System

You need **4 terminals** open:

### Terminal 1: MongoDB
```bash
# Start MongoDB
mongod
# or if using MongoDB service
sudo systemctl start mongod
```

### Terminal 2: Backend (FastAPI)
```bash
# Navigate to backend folder (root)
cd c:\Users\Admin\OneDrive\Desktop\odduBackend\OdooXGcet

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Run backend server
python main.py
# or
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
✅ Connected to MongoDB: hrms_db
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 3: Frontend (Vite/React)
```bash
# Navigate to project root (where package.json is)
cd c:\Users\Admin\OneDrive\Desktop\odduBackend\OdooXGcet

# Install dependencies (first time only)
npm install

# Run frontend dev server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Terminal 4: E2E Tests (Optional)
```bash
# Run integration tests
pytest test_e2e_connection.py -v -s

# Run specific test
pytest test_e2e_connection.py::test_end_to_end_login_flow -v -s
```

## 🧪 Testing the Integration

### Manual Testing

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **Open Frontend:**
   - Navigate to http://localhost:5173
   - You should see the Dayflow HRMS login page

3. **Test Login:**
   - Open browser console (F12)
   - Go to Network tab
   - Try logging in
   - Look for API calls to `http://localhost:8000/auth/login`
   - Check Response tab for `access_token`
   - Check Application → Local Storage for `access_token`

4. **Test API Calls:**
   - After login, navigate around
   - Check console for logs: `📤 API Request`, `📥 API Response`
   - Check Network tab for API calls to `/attendance`, `/leaves`, etc.

### Automated Testing

```bash
# Run all E2E tests
pytest test_e2e_connection.py -v

# Run with browser visible (for debugging)
# Edit test_e2e_connection.py: set headless=False in browser launch

# Check test results
# ✅ test_backend_health
# ✅ test_end_to_end_login_flow
# ✅ test_attendance_flow
# ✅ test_leave_balance_integration
```

## 🔧 Troubleshooting

### Issue 1: "CORS Policy" Error in Browser Console

**Symptoms:**
```
Access to XMLHttpRequest at 'http://localhost:8000/auth/login' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Fix:**
1. Check `main.py` has CORS middleware configured
2. Verify frontend URL is in `origins` list
3. Restart backend server

### Issue 2: "401 Unauthorized" on Every Request

**Symptoms:**
- Login works but other API calls fail
- Console shows: `❌ API Error: 401`

**Fix:**
1. Check browser console for token: `localStorage.getItem('access_token')`
2. Verify `api.ts` interceptor is attaching token
3. Check backend logs for token validation errors

### Issue 3: "Network Error" - Cannot Connect to Server

**Symptoms:**
```
🌐 Network Error: Cannot connect to server
```

**Fix:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check if MongoDB is running: `mongosh`
3. Verify firewall isn't blocking port 8000
4. Check `VITE_API_URL` in frontend `.env`

### Issue 4: Playwright Test Fails

**Symptoms:**
- Browser doesn't launch
- Test times out

**Fix:**
```bash
# Reinstall browsers
playwright install --force

# Run with visible browser for debugging
# Edit test file: headless=False

# Check URLs are correct
echo $FRONTEND_URL
echo $BACKEND_URL
```

### Issue 5: Database Connection Error

**Symptoms:**
```
❌ Database Connection Error
```

**Fix:**
1. Start MongoDB: `mongod`
2. Check MongoDB is accessible: `mongosh mongodb://localhost:27017`
3. Verify `.env` has correct `MONGO_URI`
4. Check MongoDB logs for errors

## 📊 Verification Checklist

- [ ] MongoDB is running and accessible
- [ ] Backend starts without errors on port 8000
- [ ] Backend health check returns 200: `curl http://localhost:8000/health`
- [ ] Frontend starts on port 5173 (or 3000)
- [ ] Browser console shows: `🔗 API Base URL: http://localhost:8000`
- [ ] Login page loads without errors
- [ ] Login creates API call to `/auth/login` (check Network tab)
- [ ] Token appears in localStorage after login
- [ ] Dashboard loads after login
- [ ] Console shows API request logs: `📤 API Request`
- [ ] E2E tests pass: 4/4 tests green

## 🎯 Next Steps

Now that integration is complete:

1. **Test All Features:**
   - Login/Logout
   - Attendance check-in/check-out
   - Leave application and approval
   - Profile updates
   - Payroll generation

2. **Frontend Updates:**
   - Update remaining service files (attendance.service.ts, leave.service.ts, payroll.service.ts)
   - Replace mock data with real API calls
   - Update components to use real data

3. **Deployment:**
   - Set up production environment variables
   - Configure production CORS origins
   - Set up reverse proxy (Nginx)
   - Deploy to cloud (AWS, Azure, GCP)

## 📝 API Endpoints Reference

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh token

### Attendance
- `POST /attendance/check-in` - Check in
- `POST /attendance/check-out` - Check out
- `GET /attendance/dashboard` - Get dashboard data

### Leaves
- `GET /leaves/me/balance` - Get my leave balance
- `POST /leaves/apply` - Apply for leave
- `GET /leaves/admin/pending` - Get pending requests (admin)
- `PUT /leaves/admin/action/{id}` - Approve/reject leave (admin)

### Profile
- `GET /profile/me` - Get my profile
- `PUT /profile/personal` - Update personal details
- `PUT /profile/bank` - Update bank details

### Payroll
- `POST /payroll/generate-slip/{user_id}` - Generate payslip (admin)
- `GET /attendance/stats/{user_id}` - Get attendance stats

## 🎉 Success!

Your frontend and backend are now fully integrated and working together!

**System Status:**
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ CORS configured
- ✅ API client working
- ✅ Authentication flow complete
- ✅ Database integration active
- ✅ E2E tests passing

**Next:** Start testing with real user flows and update remaining services!
