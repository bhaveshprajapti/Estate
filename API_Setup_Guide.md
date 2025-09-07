# Society Management API - Corrected Authentication Flow Guide

## 📋 Overview
This Postman collection contains the **corrected authentication system** for the Society Management Platform with proper **dual login methods** and **SUB_ADMIN invitation flow**.

## 🔄 **CORRECTED AUTHENTICATION FLOW**

### **Key Changes Made:**
1. **ADMIN** is the super admin who creates societies and invites SUB_ADMINs
2. **SUB_ADMIN** is the society-specific admin (replaces "Chairman" concept)
3. **Dual Login Methods**: Both username/password AND mobile+OTP
4. **Proper SUB_ADMIN Invitation Flow**: Invitation → OTP → Registration → Account Creation

## 🏗️ **CORRECTED FLOW ARCHITECTURE**

### **Role Hierarchy:**
- **🔴 ADMIN**: Creates societies, invites SUB_ADMINs, system-wide management
- **🟡 SUB_ADMIN**: Society-specific management (handles that society's operations)
- **🟢 MEMBER**: Residential society members
- **🔵 STAFF**: Operational staff with limited access

### **Authentication Methods:**
1. **Method 1**: Phone Number + Password (Traditional)
2. **Method 2**: Phone Number + OTP (Secure)
3. **Legacy**: Backward compatibility login

## 🔧 **SUB_ADMIN Invitation Process**

### **Step-by-Step Flow:**
1. **ADMIN creates society** with basic details (name, address, etc.)
2. **ADMIN sends invitation** to SUB_ADMIN with phone number and email
3. **OTP is sent** to invited phone number automatically
4. **Invited person verifies OTP** to confirm phone number ownership
5. **Complete registration** with personal details and password
6. **SUB_ADMIN account created** with society assigned
7. **SUB_ADMIN can now login** and manage their assigned society

## 📁 Files Included
1. **Society_Management_API.postman_collection.json** - Complete API collection
2. **Society_Management_Environment.postman_environment.json** - Environment variables
3. **API_Setup_Guide.md** - This setup guide

## 🚀 Quick Setup Instructions

### Step 1: Import Collection & Environment
1. Open Postman
2. Click **Import** button
3. Import `Society_Management_API.postman_collection.json`
4. Import `Society_Management_Environment.postman_environment.json`
5. Select the "Society Management Environment" from environment dropdown

### Step 2: Start Django Server
Ensure your Django development server is running:
```bash
cd /path/to/society-management-main/backend
python manage.py runserver
```

### Step 3: Test Authentication Flow
1. **Register User**: Use "Register User" endpoint
2. **Login User**: Use "Login User" endpoint (auto-saves tokens)
3. **Test OTP Features**: Use OTP endpoints to test authentication

## 📖 Collection Structure

### 🔐 Authentication
- **Register User** - Creates new user with OTP
- **Login User** - Authenticates user and generates OTP
- **Get User Profile** - Retrieves authenticated user info
- **Logout User** - Invalidates tokens
- **Refresh Token** - Refreshes access token

### 📱 OTP & Password Reset
- **Send OTP** - Sends OTP for various purposes
- **Verify OTP** - Verifies OTP codes
- **Forgot Password** - Initiates password reset flow
- **Reset Password** - Completes password reset with OTP

### 🏢 Society Management
- **List/Create/Update/Delete Societies**
- **Get Society Details**
- Complete CRUD operations for society management

### 🏠 Flat Management
- **List/Create/Update/Delete Flats**
- **Get Flat Details**
- Flat assignment and management

### 📧 Chairman Invitations
- **List/Create Chairman Invitations**
- **Accept Chairman Invitation**
- Invitation management system

### 🚗 Vehicle Management
- **List/Add/Update/Delete Vehicles**
- **Get Vehicle Details**
- Vehicle registration and tracking

### 💳 Billing System
- **List/Create Maintenance Bills**
- **List/Create Common Expenses**
- **List Expense Splits**
- Comprehensive billing management

### 📢 Community Features
- **List/Create Notices**
- **List/Create/Book Amenities**
- **List Amenity Bookings**
- Community engagement features

### 🛡️ Security & Complaints
- **List/Add Visitors**
- **List/Submit Complaints**
- **Update Visitor/Complaint Status**
- Security and complaint management

## 🔧 Environment Variables

### 🌐 Server Configuration
- `base_url`: API base URL (default: http://localhost:8000/api)

### 🔑 Authentication Variables (Auto-populated)
- `access_token`: JWT access token
- `refresh_token`: JWT refresh token
- `user_id`: Current user ID
- `user_role`: Current user role
- `last_otp`: Last generated OTP
- `forgot_password_otp`: Password reset OTP

### 👤 Test User Data
- `test_phone`: 9999999999
- `test_email`: test@society.com
- `test_first_name`: Test
- `test_last_name`: User
- `test_password`: test123456
- `test_role`: MEMBER (Options: ADMIN, SUB_ADMIN, MEMBER, STAFF)

### 🏢 Test Society Data
- `society_name`: Test Society
- `society_address`: 123 Test Street
- `society_city`: Mumbai
- `society_state`: Maharashtra
- `society_pincode`: 400001
- `society_reg_number`: TEST123

### 🏠 Test Flat Data
- `flat_number`: A-101
- `flat_floor`: 1
- `flat_type`: 2BHK
- `flat_area`: 1000

### 🚗 Test Vehicle Data
- `vehicle_number`: MH12AB1234
- `vehicle_type`: CAR
- `vehicle_brand`: Honda
- `vehicle_model`: City
- `vehicle_color`: White

## 🧪 Testing Workflows

### Basic Authentication Flow
1. **Register** → **Login** → **Get Profile** → **Logout**
2. Test with different roles: ADMIN, SUB_ADMIN, MEMBER, STAFF

### OTP Authentication Flow
1. **Send OTP** → **Verify OTP**
2. **Forgot Password** → **Reset Password**
3. Test different OTP purposes: LOGIN, REGISTRATION, FORGOT_PASSWORD

### Society Management Flow
1. **Login as ADMIN** → **Create Society** → **Get Society Details**
2. **Create Flat** → **Add Vehicle** → **Create Chairman Invitation**

### Billing & Community Flow
1. **Create Maintenance Bill** → **Create Common Expense**
2. **Create Notice** → **Create Amenity** → **Book Amenity**

### Security & Complaints Flow
1. **Add Visitor** → **Submit Complaint**
2. **Update Visitor Status** → **Update Complaint Status**

## 🔄 Auto-Generated Variables
The collection automatically populates these variables during API calls:
- **IDs**: society_id, flat_id, vehicle_id, etc.
- **Tokens**: access_token, refresh_token
- **OTPs**: last_otp, forgot_password_otp

## ⚙️ Pre-request Scripts & Tests
Each endpoint includes:
- **Pre-request scripts** for authentication headers
- **Test scripts** to auto-populate environment variables
- **Response validation** and console logging

## 🔒 Security Features
- **JWT Authentication** with automatic token management
- **OTP Verification** for enhanced security
- **Role-based Access Control** (RBAC)
- **Session Management** with logout functionality

## 📊 User Roles & Permissions

### 🔴 ADMIN
- Full system access
- Can manage all societies
- Can invite SUB_ADMINs
- System-wide operations

### 🟡 SUB_ADMIN (Chairman)
- Society-specific management
- Can manage flats, vehicles, staff
- Can create notices and manage amenities
- Billing and expense management

### 🟢 MEMBER
- Personal profile management
- View notices and book amenities
- Submit complaints
- Pay bills and view expenses

### 🔵 STAFF
- Limited operational access
- Visitor management
- Basic reporting functions
- Assigned duty operations

## 🐛 Troubleshooting

### Common Issues:
1. **401 Unauthorized**: Check if access_token is set
2. **404 Not Found**: Verify Django server is running
3. **400 Bad Request**: Check request body format
4. **403 Forbidden**: Verify user role permissions

### Solutions:
1. **Re-login** to refresh tokens
2. **Check environment** variables are set correctly
3. **Verify server** is running on localhost:8000
4. **Update base_url** if server is on different port

## 📝 Sample Test Scenarios

### Scenario 1: New User Registration
1. Set `test_phone` to unique number
2. Run "Register User"
3. Check OTP in response
4. Run "Login User" with same credentials

### Scenario 2: Society Setup
1. Login as ADMIN
2. Create Society
3. Create Flats
4. Invite Chairman
5. Setup amenities and notices

### Scenario 3: Member Activities
1. Login as MEMBER
2. View notices
3. Book amenity
4. Submit complaint
5. Check maintenance bills

## 🎯 Success Indicators
- ✅ All requests return 200/201 status codes
- ✅ Tokens are auto-populated in environment
- ✅ OTPs are generated and displayed in console
- ✅ Resource IDs are automatically captured
- ✅ Role-based access works correctly

## 📞 Support
For issues or questions:
1. Check Django server logs
2. Verify database migrations are applied
3. Ensure all environment variables are set
4. Test with different user roles

---

🎉 **The Society Management Platform API collection is ready for comprehensive testing!**

All endpoints support the complete OTP authentication flow with automatic token management and role-based access control.