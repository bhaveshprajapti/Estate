# 🏘️ Member Capabilities Complete Guide

This document provides a comprehensive overview of all the capabilities available to members in the Society Management System, addressing your request for members to be able to perform all society-related activities.

## 📋 Overview

Members in the Society Management System have access to a wide range of features that allow them to participate fully in society activities. All member actions are society-specific, meaning members can only access data and perform actions related to their assigned society.

## 🔧 Member Capabilities Breakdown

### 1. Staff Registration and Management
**Can members add their own staff?**
- ❌ **Members cannot directly create staff accounts** - This is restricted to SUB_ADMIN (Chairman) for security reasons
- ✅ **Members can request staff services** through the helpdesk system
- ✅ **Members can view staff directory** to contact existing staff

### 2. Vehicle Management
**Can members add details of vehicles?**
- ✅ **Yes, members can register their vehicles** through the vehicle management system
- Members can add, view, and manage their own vehicles
- All vehicle registrations are society-specific

### 3. Amenity Booking
**Can members book amenities?**
- ✅ **Yes, members can book society amenities** like swimming pools, gyms, community halls
- Members can view available amenities and make bookings
- Members can view their own booking history

### 4. Visitor Pass Application
**Can members apply for visitor passes?**
- ❌ **Members cannot directly create visitor passes** - This is managed by SUB_ADMIN for security
- ✅ **Members can request visitor passes** through the helpdesk system
- ✅ **Members can view visitor logs** for their flat

### 5. Bill Payment
**Can members pay bills?**
- ✅ **Yes, members can view their maintenance bills** and payment history
- Members can see bills assigned to their flat(s)
- Members can track payment status
- SUB_ADMIN handles actual payment processing and status updates

### 6. Complaint Submission
**Can members file complaints?**
- ✅ **Yes, members can submit complaints** about maintenance issues, security concerns, etc.
- Members can track complaint status and resolution
- Members can view their complaint history

### 7. Service Requests
**Can members request services?**
- ✅ **Yes, members can submit service requests** through the helpdesk system
- Members can request maintenance, repairs, or other services
- Members can track request status

### 8. Gate Updates
**Can members request gate updates?**
- ❌ **Members cannot directly update gate logs** - This is handled by security staff
- ✅ **Members can request gate-related services** through the helpdesk system

## 🎯 Detailed Member Functionality

### Authentication & Profile Management
- ✅ **Self-registration** with society search and selection
- ✅ **Profile management** - Update personal information
- ✅ **Password management** - Change password, reset forgotten passwords
- ✅ **View own profile details** including assigned flats

### Society Directory Access
- ✅ **View society member directory** with contact information
- ✅ **Search directory** by name, flat number, or building
- ✅ **Access helpdesk contacts** for society services

### Vehicle Management
**API Endpoints:**
- `GET /api/vehicles/` - List vehicles (members see only their own)
- `POST /api/vehicles/` - Register a new vehicle
- `GET /api/vehicles/{id}/` - View vehicle details
- `PUT /api/vehicles/{id}/` - Update vehicle information
- `DELETE /api/vehicles/{id}/` - Remove a vehicle

### Amenity Booking
**API Endpoints:**
- `GET /api/amenities/` - View available society amenities
- `GET /api/amenity-bookings/` - View own bookings
- `POST /api/amenity-bookings/` - Create a new booking
- `GET /api/amenity-bookings/{id}/` - View booking details
- `PUT /api/amenity-bookings/{id}/` - Update booking (if allowed)
- `DELETE /api/amenity-bookings/{id}/` - Cancel booking

### Billing & Payments
**API Endpoints:**
- `GET /api/maintenance-bills/` - View bills for own flats
- `GET /api/common-expenses/` - View common expenses
- `GET /api/expense-splits/` - View expense distribution

### Complaint Management
**API Endpoints:**
- `GET /api/complaints/` - View own complaints
- `POST /api/complaints/` - Submit a new complaint
- `GET /api/complaints/{id}/` - View complaint details
- `PUT /api/complaints/{id}/` - Update complaint (if allowed)

### Marketplace & Community
**API Endpoints:**
- `GET /api/marketplace/` - View marketplace listings
- `POST /api/marketplace/` - Create a listing
- `GET /api/marketplace/{id}/` - View listing details
- `PUT /api/marketplace/{id}/` - Update own listing
- `DELETE /api/marketplace/{id}/` - Remove own listing

### Notices & Announcements
**API Endpoints:**
- `GET /api/notices/` - View society notices
- `GET /api/notices/{id}/` - View notice details

### Helpdesk Services
**API Endpoints:**
- `GET /api/helpdesk-contacts/` - View helpdesk contacts
- `GET /api/helpdesk-designations/` - View service categories

## 🔐 Security Model

### Member Permissions Summary
Members have limited but comprehensive access to society services:

| Feature | Access Level | Notes |
|---------|--------------|-------|
| **Profile Management** | ✅ Full | Can update own profile |
| **Vehicle Management** | ✅ Full | Can manage own vehicles |
| **Amenity Booking** | ✅ Full | Can book society amenities |
| **Complaint Submission** | ✅ Full | Can submit and track complaints |
| **Bill Viewing** | ✅ Read-only | Can view own bills |
| **Directory Access** | ✅ Read-only | Can view society directory |
| **Marketplace** | ✅ Full | Can list and browse items |
| **Staff Creation** | ❌ None | Restricted to SUB_ADMIN |
| **Visitor Pass Creation** | ❌ None | Restricted to SUB_ADMIN |
| **Gate Log Management** | ❌ None | Restricted to STAFF |

## 🔄 Member Workflow Examples

### 1. Vehicle Registration Workflow
1. Member logs in to the system
2. Navigates to Vehicle Management section
3. Clicks "Add Vehicle"
4. Enters vehicle details (number, type, brand, etc.)
5. Vehicle is registered to member's flat
6. Member can now view/manage this vehicle

### 2. Amenity Booking Workflow
1. Member logs in to the system
2. Views available amenities in their society
3. Selects desired amenity and date/time
4. Submits booking request
5. Booking is created (may require approval)
6. Member receives confirmation
7. Member can view/cancel booking as needed

### 3. Complaint Submission Workflow
1. Member logs in to the system
2. Navigates to Complaints section
3. Clicks "New Complaint"
4. Fills complaint form with details
5. Submits complaint
6. Complaint is assigned tracking number
7. Member can track status and add updates

## 🛠️ Technical Implementation Details

### Member Access Control
- Members can only access data related to their society
- Members can only view/modify their own records
- All member actions are logged for audit purposes
- Society isolation ensures data privacy

### API Security
- JWT token-based authentication
- Role-based access control (RBAC)
- Society-scoped data filtering
- Input validation and sanitization

## 📱 User Experience

### Dashboard View
Members have access to a personalized dashboard showing:
- Assigned flats
- Pending bills
- Open complaints
- Upcoming amenity bookings
- Recent society notices

### Notifications
Members receive notifications for:
- Complaint status updates
- Booking confirmations/cancellations
- Bill generation
- Society announcements

## 🎯 Conclusion

The Society Management System provides members with comprehensive access to all essential society services while maintaining appropriate security boundaries. Members can:

1. ✅ Manage their personal information and vehicles
2. ✅ Book society amenities and track reservations
3. ✅ Submit and track complaints and service requests
4. ✅ View bills and payment history
5. ✅ Access society directory and announcements
6. ✅ Participate in the community marketplace

All member capabilities are designed with security and usability in mind, ensuring that members have the tools they need to be active participants in their society while maintaining proper access controls for sensitive operations like staff management and visitor passes.