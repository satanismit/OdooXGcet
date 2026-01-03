# 🚀 Dayflow HRMS - Quick Start Guide

Welcome to **Dayflow**, a complete Human Resource Management System built for the Odoo Hackathon!

## 📋 Prerequisites

Before you begin, ensure you have installed:
- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)
- A modern web browser (Chrome, Firefox, Edge, or Safari)

## ⚡ Quick Start

### 1. Install Dependencies

Open your terminal in the project directory and run:

```bash
npm install
```

This will install all required packages including React, TypeScript, Tailwind CSS, and React Router.

### 2. Start Development Server

```bash
npm run dev
```

The application will automatically open in your browser at `http://localhost:3000`

### 3. Login with Demo Credentials

**Admin Account:**
- Email: `admin@dayflow.com`
- Password: `any password` (this is a demo, any password works!)

**Employee Account:**
- Email: `employee@dayflow.com`
- Password: `any password`

## 🎯 What Can You Do?

### As an Employee:
1. ✅ Check in/out for daily attendance
2. 📝 Apply for different types of leaves
3. 💰 View salary breakdown and payroll history
4. 👤 Manage your profile
5. 📊 See attendance statistics and leave balance

### As an Admin/HR:
1. ✅ Approve or reject employee leave requests
2. 📊 View team analytics and attendance overview
3. 💵 Manage payroll for all employees
4. 👥 Monitor team performance

## 🛠️ Available Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

## 📂 Project Structure Overview

```
src/
├── components/    # Reusable UI components
├── pages/        # Page components
├── routes/       # Routing configuration
├── context/      # State management
├── services/     # Mock API services
├── types/        # TypeScript definitions
└── utils/        # Helper functions
```

## 🎨 Key Features Implemented

✅ Role-based authentication (Employee & Admin)  
✅ Protected routes with automatic redirects  
✅ Attendance tracking with check-in/check-out  
✅ Leave management system  
✅ Payroll viewing  
✅ Profile management  
✅ Responsive design for all screen sizes  
✅ Modern UI with Tailwind CSS  
✅ TypeScript for type safety  

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is already in use, Vite will automatically use the next available port (3001, 3002, etc.)

### Dependencies Issues
If you encounter issues with dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors in VS Code
After installation, reload VS Code window:
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "Reload Window" and press Enter

## 📱 Test Different Roles

1. **Login as Employee** → Explore employee features
2. **Logout** → Click logout button in navbar
3. **Login as Admin** → See admin dashboard and features
4. **Try Different Pages** → Navigation sidebar shows role-based menu

## 🎓 Learning Points

This project demonstrates:
- React functional components and hooks
- TypeScript interfaces and type safety
- Context API for state management
- React Router for navigation
- Protected routes and role-based access
- Tailwind CSS utility classes
- Mock service layer architecture
- Clean component organization

## 💡 Tips for Hackathon Presentation

1. **Show Login Flow**: Demo both employee and admin login
2. **Highlight Features**: Show attendance check-in, leave application, salary view
3. **Role Switching**: Demonstrate admin features like leave approvals
4. **Responsive Design**: Resize browser to show mobile responsiveness
5. **Code Quality**: Mention TypeScript, clean architecture, and reusable components

## 🚀 Next Steps (If You Want to Extend)

- Add backend API integration
- Implement real authentication with JWT
- Add database connectivity
- Create PDF reports
- Add email notifications
- Implement dark mode
- Add more detailed analytics

## 📞 Need Help?

- Check the main README.md for detailed documentation
- Review the code comments - every file is well-documented
- All components are in `src/components/`
- All pages are in `src/pages/`

---

**Happy Hacking! 🎉**

Built with ❤️ for Odoo Hackathon 2026
