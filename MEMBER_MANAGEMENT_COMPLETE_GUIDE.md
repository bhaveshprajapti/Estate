# Complete Member Management System Guide

## Overview

This document provides a comprehensive guide to the Member Management System implemented in the Society Management Platform. The system includes full CRUD operations for member management with proper role-based access control, approval workflows, and security features.

## System Components

### 1. Core Implementation Files

- **ViewSet**: `MemberViewSet` in `backend/society_management/views.py`
- **Serializers**: `UserProfileSerializer` and `EnhancedUserProfileSerializer` in `backend/society_management/serializers.py`
- **URLs**: Registered as `/members/` in `backend/society_management/urls.py`
- **Models**: Extended `User` model in `backend/society_management/models.py`

### 2. Key Features Implemented

#### ✅ Complete CRUD Operations
- **Create**: Member registration (self-registration and direct addition)
- **Read**: List members with filtering and search capabilities
- **Update**: Profile updates with role-based permissions
- **Delete**: Soft deletion (deactivation) with permission controls

#### ✅ Role-Based Access Control
- **MEMBER**: Can view and update their own profile
- **SUB_ADMIN**: Full member management within their society
- **ADMIN**: Member management across all managed societies
- **SUPER_ADMIN**: System-wide access

#### ✅ Approval Workflow
- Self-registered members require SUB_ADMIN approval
- Direct addition by SUB_ADMIN creates immediately active accounts
- Clear error messages with chairman contact information for pending members

## API Endpoints

### Authentication Endpoints
```
POST /api/auth/register/              # Member self-registration
POST /api/auth/login-password/        # Member login
POST /api/members/direct-add/         # SUB_ADMIN direct member addition
```

### Member Management Endpoints
```
GET    /api/members/                  # List members
GET    /api/members/{id}/             # Get member details
PATCH  /api/members/{id}/             # Update member profile
DELETE /api/members/{id}/             # Deactivate member
```

### Registration Request Endpoints
```
GET  /api/member-requests/            # List registration requests
GET  /api/member-requests/{id}/       # Get request details
POST /api/member-requests/{id}/approve_request/  # Approve request
POST /api/member-requests/{id}/reject_request/   # Reject request
```

### Profile Management Endpoints
```
GET  /api/auth/profile/               # Get own profile
PATCH /api/auth/profile/              # Update own profile
```

## Role-Based Permissions

### MEMBER Role Permissions
- **Read**: Own profile only
- **Update**: Own profile only
- **Delete**: None (cannot deactivate themselves)

### SUB_ADMIN Role Permissions
- **Read**: All members in their society
- **Create**: Direct member addition
- **Update**: Any member in their society
- **Delete**: Deactivate any member in their society

### ADMIN Role Permissions
- **Read**: All members in all managed societies
- **Create**: Direct member addition in any managed society
- **Update**: Any member in any managed society
- **Delete**: Deactivate any member in any managed society

## Security Features

### 1. Member Approval System
- Self-registered members are inactive until approved
- Login attempts by pending members show chairman contact info
- SUB_ADMIN can approve or reject registration requests

### 2. Society Data Isolation
- Members can only access data from their assigned society
- SUB_ADMIN can only manage members in their society
- ADMIN can manage members in all societies they manage

### 3. Soft Deletion
- Members are deactivated rather than deleted
- Data integrity is maintained
- Deactivation requires appropriate permissions

### 4. Password Security
- Temporary passwords for direct member additions
- Password validation and confirmation
- Secure password storage

## Testing Resources

### 1. Postman Collection
**File**: `Member_Management_CRUD.postman_collection.json`

Includes comprehensive tests for:
- Member registration workflows
- Authentication scenarios
- CRUD operations
- Approval processes
- Error handling

### 2. Environment Variables
**File**: `Society_Management_Environment.postman_environment.json`

Pre-configured variables for testing:
- User credentials for all roles
- Phone numbers and emails
- Test data for various scenarios

### 3. Test Scripts
- `test_member_approval_workflow.py`: Complete workflow testing
- `member_crud_test.py`: CRUD operations verification

## Implementation Details

### MemberViewSet Class
Located in `backend/society_management/views.py`

Key methods:
- `get_queryset()`: Role-based member filtering
- `get_permissions()`: Action-specific permission logic
- `get_serializer_class()`: Dynamic serializer selection
- `update()`: Profile update with permission checking
- `destroy()`: Member deactivation with validation

### Serializers
1. **UserProfileSerializer**: Basic member information
2. **EnhancedUserProfileSerializer**: Detailed member information with additional fields

### QuerySet Filtering
- SUB_ADMIN: Members from their assigned society only
- ADMIN: Members from all managed societies
- MEMBER: Only their own profile

## Usage Examples

### 1. Member Self-Registration
```json
POST /api/auth/register/
{
    "phone_number": "9876543210",
    "email": "member@test.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword",
    "password_confirm": "securepassword"
}
```

Response for pending member:
```json
{
    "message": "User registered successfully. Account requires admin approval.",
    "user": { /* user data */ },
    "otp_info": { /* OTP for testing */ }
}
```

### 2. SUB_ADMIN Direct Member Addition
```json
POST /api/members/direct-add/
Authorization: Bearer <SUB_ADMIN_TOKEN>
{
    "phone_number": "9876543211",
    "email": "direct@test.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "memberpass",
    "password_confirm": "memberpass",
    "ownership_type": "OWNER",
    "date_of_birth": "1985-05-15",
    "occupation": "Engineer",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "9876543210",
    "permanent_address": "123 Main Street"
}
```

Response:
```json
{
    "message": "Member added successfully",
    "user": { /* user data */ },
    "temp_password": "temp_3211",
    "note": "Temporary password provided. User should change it on first login."
}
```

### 3. List Members (SUB_ADMIN)
```bash
GET /api/members/?is_approved=true
Authorization: Bearer <SUB_ADMIN_TOKEN>
```

### 4. Update Member Profile
```json
PATCH /api/members/{member_id}/
Authorization: Bearer <MEMBER_OR_SUB_ADMIN_TOKEN>
{
    "first_name": "Updated Name",
    "last_name": "Updated Last Name"
}
```

### 5. Deactivate Member (SUB_ADMIN)
```bash
DELETE /api/members/{member_id}/
Authorization: Bearer <SUB_ADMIN_TOKEN>
```

Response:
```json
{
    "message": "Member John Doe has been deactivated"
}
```

## Error Handling

### Common Error Scenarios

1. **Pending Member Login Attempt**
   - Status: 400 Bad Request
   - Message: "Your account is pending approval. Please contact your society's chairman: [Chairman Name] ([Phone Number])"

2. **Unauthorized Access**
   - Status: 403 Forbidden
   - Message: "You do not have permission to perform this action."

3. **Permission Violation**
   - Status: 403 Forbidden
   - Message: "Members can only update their own profile" or "Only SUB_ADMIN and ADMIN can deactivate members"

4. **Self-Deactivation Attempt**
   - Status: 400 Bad Request
   - Message: "You cannot deactivate your own account"

## Setup and Testing Instructions

### 1. Server Setup
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create super admin
python manage.py runserver
```

### 2. Postman Testing
1. Import `Society_Management_Environment.postman_environment.json`
2. Import `Member_Management_CRUD.postman_collection.json`
3. Update environment variables as needed
4. Run collection requests in order

### 3. Python Script Testing
```bash
python test_member_approval_workflow.py
python member_crud_test.py
```

## Future Enhancements

### Planned Features
1. **Bulk Member Operations**: Import/export via CSV
2. **Advanced Search**: More sophisticated filtering options
3. **Notification System**: Email/SMS notifications for approvals
4. **Activity Logging**: Track member profile changes
5. **Multi-Factor Authentication**: Enhanced security options

### API Improvements
1. **Pagination**: For large member lists
2. **Sorting**: Customizable member list ordering
3. **Export**: Member data export in various formats
4. **Audit Trail**: Comprehensive member activity tracking

## Conclusion

The Member Management System provides a robust, secure, and comprehensive solution for managing residential society members. With full CRUD operations, proper role-based access control, and security features, it ensures data integrity while providing a smooth user experience for all roles.

The system is production-ready with comprehensive testing resources and can be easily extended with additional features as needed.