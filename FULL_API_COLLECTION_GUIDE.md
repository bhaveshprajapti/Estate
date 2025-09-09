# 🏢 Society Management System - FULL API Collection Guide

This guide provides comprehensive instructions for using the complete Postman collection for the Society Management System. The collection includes ALL endpoints for every role (ADMIN, SUB_ADMIN, MEMBER, STAFF) and covers all CRUD operations for every feature.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Files Included](#files-included)
3. [Environment Setup](#environment-setup)
4. [Collection Structure](#collection-structure)
5. [Role-Based Testing](#role-based-testing)
6. [Complete Workflow](#complete-workflow)
7. [Member Capabilities](#member-capabilities)
8. [Best Practices](#best-practices)

## 📖 Overview

The Society Management System is a comprehensive platform for managing residential societies with features including:
- Member management and registration
- Vehicle registration and management
- Amenity booking system
- Complaint management
- Marketplace for residents
- Billing and expense tracking
- Security and visitor management
- Helpdesk services
- Directory and notice board
- Dashboard analytics

## 📁 Files Included

1. **Society_Management_Full_API.postman_collection.json** - Complete API collection with all endpoints
2. **Society_Management_Full_Environment.postman_environment.json** - Environment variables for all roles
3. **FULL_API_COLLECTION_GUIDE.md** - This documentation

## ⚙️ Environment Setup

### Import Files into Postman

1. Open Postman
2. Click "Import" button
3. Select both JSON files:
   - `Society_Management_Full_API.postman_collection.json`
   - `Society_Management_Full_Environment.postman_environment.json`
4. Select the "Society Management Environment - FULL" environment

### Environment Variables

The environment includes variables for all roles and entities:

**Authentication Tokens:**
- `access_token` - Current user token
- `admin_access_token` - ADMIN role token
- `subadmin_access_token` - SUB_ADMIN role token
- `member_access_token` - MEMBER role token
- `staff_access_token` - STAFF role token

**User Information:**
- `user_id` - Current user ID
- `admin_user_id` - ADMIN user ID
- `subadmin_user_id` - SUB_ADMIN user ID

**Entity IDs (auto-populated):**
- `society_id` - Society ID
- `building_id` - Building ID
- `flat_id` - Flat ID
- `vehicle_id` - Vehicle ID
- And many more...

**Pre-configured Test Data:**
- Phone numbers and passwords for all roles
- Sample data for societies, buildings, flats, etc.

## 🗂️ Collection Structure

The collection is organized into logical folders:

### 🔐 Authentication System
- Super Admin login
- ADMIN login
- SUB_ADMIN login
- MEMBER login
- STAFF login
- Member registration
- OTP authentication
- Token refresh
- Profile management

### 🏢 Society Management
- Create, list, get, update, delete societies
- Public society search

### 🎭 SUB_ADMIN Invitation Flow
- Create invitation
- Verify OTP
- Complete registration

### 👥 Member Management
- Direct member addition
- List and manage members
- Approve/reject member requests

### 🏗️ Building & Flat Management
- Create, list, get, update, delete buildings
- Create, list, get, update, delete flats
- Enhanced flat management

### 🚗 Vehicle Management
- Register, list, get, update, delete vehicles

### 🏖️ Amenity Management
- Create, list, get, update, delete amenities
- Book, list, get, update, cancel amenity bookings

### 📢 Notice Management
- Create, list, get, update, delete notices

### 🛒 Marketplace
- Create, list, get, update, delete marketplace listings

### 📢 Complaint Management
- Submit, list, get, update, delete complaints

### 💰 Billing System
- Create, list, get, update, delete bill types
- View bills and expenses

### 🛡️ Security & Visitors
- Create, list, get, update visitor passes
- Create and list gate logs

### 🛠️ Helpdesk Management
- Create, list, get, update, delete helpdesk designations
- List helpdesk contacts

### 👥 Staff Management
- Create, list, get, update, delete staff categories
- Create staff users
- List staff members

### 📊 Dashboard & Analytics
- Dashboard statistics
- Directory listing

## 👥 Role-Based Testing

### 1. Super Admin (System Administrator)
- **Purpose**: System-level administration
- **Capabilities**: Create ADMIN users, system-wide management
- **Login**: Use `super_admin_phone` and `super_admin_password`

### 2. ADMIN (Society Administrator)
- **Purpose**: Manage multiple societies
- **Capabilities**: Create societies, assign SUB_ADMINs
- **Login**: Use `admin_phone` and `admin_password`

### 3. SUB_ADMIN (Chairman/Secretary)
- **Purpose**: Manage a specific society
- **Capabilities**: Member approval, staff management, amenity creation
- **Login**: Use `subadmin_phone` and `subadmin_password`

### 4. MEMBER (Resident)
- **Purpose**: Daily society activities
- **Capabilities**: Vehicle registration, amenity booking, complaint submission
- **Login**: Use `member_phone` and `member_password`

### 5. STAFF (Security/Service Providers)
- **Purpose**: Security and maintenance services
- **Capabilities**: Gate log management, visitor pass verification
- **Login**: Use `staff_phone` and `staff_password`

## 🔄 Complete Workflow

### Phase 1: System Setup
1. Super Admin Login
2. Create ADMIN User
3. ADMIN Login
4. Create Society

### Phase 2: Society Configuration
1. SUB_ADMIN Invitation
2. SUB_ADMIN Registration
3. Create Buildings and Flats
4. Create Amenities
5. Create Staff Categories
6. Create Helpdesk Designations

### Phase 3: Member Onboarding
1. Member Registration (Pending Approval)
2. Member Approval by SUB_ADMIN
3. OR Direct Member Addition by SUB_ADMIN

### Phase 4: Daily Operations
1. Member Activities (Vehicles, Bookings, Complaints)
2. Staff Activities (Gate Logs, Visitor Management)
3. Admin Activities (Analytics, Directory)

## 🏠 Member Capabilities

Members have comprehensive access to all essential services:

### ✅ Available to Members:
1. **Profile Management**
   - View and update personal information
   - Emergency contact management

2. **Vehicle Management**
   - Register vehicles
   - Update vehicle details
   - Delete vehicles

3. **Amenity Booking**
   - View available amenities
   - Book amenities
   - View and cancel bookings

4. **Complaint Management**
   - Submit complaints
   - View complaint status
   - Update complaints

5. **Marketplace Participation**
   - Post items for sale
   - Browse marketplace
   - Update listings

6. **Directory Access**
   - View society directory

7. **Notices Access**
   - View society notices

8. **Dashboard Statistics**
   - View personal dashboard

9. **Helpdesk Access**
   - View helpdesk contacts
   - View service categories

### ❌ Restricted from Members:
1. **Staff Management**
   - Creating staff accounts
   - Managing staff schedules

2. **Visitor Management**
   - Creating visitor passes
   - Managing gate logs

3. **Society Administration**
   - Creating amenities
   - Managing society settings
   - Approving member registrations

## 🎯 Best Practices

### 1. Execution Order
Follow the recommended workflow to ensure dependencies are met:
1. Authentication → Society Setup → Configuration → Member Onboarding → Daily Operations

### 2. Token Management
- Always login first to populate tokens
- Use role-specific tokens for appropriate endpoints
- Refresh tokens when needed

### 3. Entity Dependencies
- Create societies before creating buildings
- Create buildings before creating flats
- Create flats before registering vehicles

### 4. Testing Strategy
- Test with clean database for consistent results
- Run complete workflow for each role
- Verify data persistence and relationships

### 5. Error Handling
- Check response status codes
- Validate error messages
- Test edge cases and invalid inputs

## 🛠️ Troubleshooting

### Common Issues:
1. **401 Unauthorized**: Login first to get tokens
2. **403 Forbidden**: Check role permissions
3. **400 Bad Request**: Validate request data
4. **404 Not Found**: Check entity IDs

### Reset Process:
1. Clear environment variables
2. Start with fresh login
3. Recreate dependent entities

## 📞 Support

For issues with the API or collection:
1. Verify server is running (`python manage.py runserver`)
2. Check environment variables
3. Validate request data formats
4. Review role permissions

## 🔄 API Version Information

- **API Version**: v1
- **Base URL**: `http://localhost:8000/api/`
- **Authentication**: JWT Bearer Tokens
- **Response Format**: JSON

This complete collection enables comprehensive testing of all society management features with proper role-based access control and data relationships.