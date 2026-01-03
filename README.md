# 🚀 Dayflow - HRMS Application

**Every workday, perfectly aligned**

A modern, production-ready Human Resource Management System (HRMS) built for the Odoo Hackathon. This is a complete frontend application with role-based access control, featuring Employee and Admin dashboards.

## ✨ Features

### 🔐 Authentication
- Login & Register functionality
- Email-based authentication
- Role-based access control (Employee & Admin)
- Protected routes with automatic redirects

### 👤 Employee Features
- **Dashboard**: Quick overview of attendance, leave balance, and stats
- **Profile Management**: View and edit personal information
- **Attendance**: Daily check-in/check-out with work hour tracking
- **Leave Management**: Apply for leaves and track status
- **Payroll**: View salary breakdown and payment history

### 👨‍💼 Admin/HR Features
- **Admin Dashboard**: Team overview and pending approvals
- **Leave Approvals**: Review and approve/reject employee leave requests
- **Payroll Management**: View all employee payroll records
- **Team Analytics**: Monitor team attendance and performance

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **React Router v6** - Routing
- **Context API** - State management

## 📁 Project Structure

```
src/
├── assets/           # Images and icons
├── components/       # Reusable components
│   ├── common/      # Button, Input, Modal, Loader
│   ├── layout/      # Navbar, Sidebar, Layout
│   ├── attendance/  # Attendance components
│   ├── leave/       # Leave management components
│   └── payroll/     # Payroll components
├── pages/           # Page components
│   ├── auth/        # Login, Register, VerifyEmail
│   ├── dashboard/   # Employee & Admin dashboards
│   ├── profile/     # View & Edit profile
│   ├── attendance/  # Attendance page
│   ├── leave/       # Leave pages
│   └── payroll/     # Payroll pages
├── routes/          # Routing configuration
├── context/         # Auth & User context
├── services/        # Mock API services
├── types/           # TypeScript interfaces
└── utils/           # Helper functions & constants
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   ```
   http://localhost:3000
   ```

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 🔑 Demo Credentials

### Admin Account
- **Email:** `admin@dayflow.com`
- **Password:** `any password` (demo mode)

### Employee Account
- **Email:** `employee@dayflow.com`
- **Password:** `any password` (demo mode)

> **Note:** This is a frontend-only demo. Any password will work for existing accounts.

## 🎯 Key Functionalities

### For Employees
1. **Check In/Out** - Track daily attendance with automatic work hour calculation
2. **Apply for Leave** - Submit leave requests with type selection (Paid, Sick, Casual, Unpaid)
3. **View Leave Balance** - Monitor remaining leave days
4. **View Salary** - Access salary breakdown and payroll history
5. **Manage Profile** - Update personal information

### For Admin/HR
1. **Approve/Reject Leaves** - Review and process employee leave requests
2. **View Team Analytics** - Monitor team attendance and leave statistics
3. **Manage Payroll** - Access all employee payroll records
4. **Full Profile Access** - Edit all employee information

## 📱 Pages Overview

| Page | Route | Access |
|------|-------|--------|
| Login | `/login` | Public |
| Register | `/register` | Public |
| Employee Dashboard | `/dashboard` | Employee |
| Admin Dashboard | `/admin/dashboard` | Admin |
| Profile | `/profile` | All Users |
| Attendance | `/attendance` | All Users |
| My Leaves | `/leaves` | All Users |
| Leave Approvals | `/admin/leave-approvals` | Admin |
| My Salary | `/payroll` | All Users |
| Payroll Admin | `/admin/payroll` | Admin |

## 🎨 Design Features

- **Responsive Design** - Works on desktop, tablet, and mobile
- **Modern UI** - Clean and professional interface
- **Role-Based Navigation** - Dynamic sidebar based on user role
- **Color-Coded Status** - Easy-to-understand visual indicators
- **Gradient Cards** - Beautiful stat cards with gradients
- **Loading States** - Smooth loading indicators
- **Error Handling** - User-friendly error messages

## 🔒 Security Features

- Protected routes with authentication checks
- Role-based access control
- Automatic redirection for unauthorized access
- Secure context-based state management

## 📦 Mock Data

The application uses mock/dummy data stored in:
- `src/services/*.service.ts` - Mock API services
- Data persists in browser localStorage
- Pre-populated with sample data for demo

## 🚧 Future Enhancements

This is a frontend demo. In a production environment, you would add:
- Real backend API integration
- Database connectivity
- Email notifications
- File upload for documents
- Advanced reporting and analytics
- Multi-language support
- Dark mode toggle
- Export to PDF/Excel

## 👥 Contributing

This project was built for the Odoo Hackathon. Feel free to fork and enhance!

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

Built with ❤️ for the Odoo Hackathon
- React Team for the amazing library
- Tailwind CSS for the utility-first framework
- Vite for the lightning-fast build tool

---

**Made for Odoo Hackathon 2026** 🏆