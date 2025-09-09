# Member Management System

## Overview

The Member Management System is a comprehensive CRUD (Create, Read, Update, Delete) implementation for managing residential society members. It includes features for member registration, approval workflows, profile management, and role-based access control.

## Key Features

### 1. Member Registration Methods

#### Self-Registration (Pending Approval)
- Members can register themselves through the public endpoint
- Registration creates a pending account requiring SUB_ADMIN approval
- Members cannot login until approved
- Login attempts show chairman contact information

#### Direct Addition by SUB_ADMIN
- SUB_ADMIN can directly add members without approval
- Members are immediately approved and can login
- Temporary password is generated and provided

### 2. CRUD Operations

#### Create
- **Self-Registration**: Public endpoint for prospective members
- **Direct Addition**: SUB_ADMIN endpoint for immediate member creation

#### Read
- **List Members**: Filterable member listing with search capabilities
- **Member Details**: Detailed member profile information
- **Member Requests**: View pending registration requests

#### Update
- **Profile Updates**: Members can update their own profiles
- **Administrative Updates**: SUB_ADMIN/ADMIN can update any member's profile

#### Delete (Deactivate)
- **Soft Deletion**: Members are deactivated rather than deleted
- **Permission Control**: Only SUB_ADMIN/ADMIN can deactivate members
- **Self-Protection**: Members cannot deactivate themselves

### 3. Approval Workflow

1. Member self-registers (pending status)
2. SUB_ADMIN reviews registration request
3. SUB_ADMIN approves or rejects the request
4. Upon approval, member account is activated
5. Member can now login to the system

### 4. Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **MEMBER** | View own profile, update own profile |
| **SUB_ADMIN** | List all members, create members (direct add), update any member, deactivate members |
| **ADMIN** | Same as SUB_ADMIN plus multi-society access |
| **SUPER_ADMIN** | System-wide access |

## API Endpoints

### Authentication
- `POST /auth/register/` - Member self-registration
- `POST /auth/login-password/` - Member login
- `POST /members/direct-add/` - SUB_ADMIN direct member addition

### Member Management
- `GET /members/` - List members
- `GET /members/{id}/` - Get member details
- `PATCH /members/{id}/` - Update member profile
- `DELETE /members/{id}/` - Deactivate member

### Registration Requests
- `GET /member-requests/` - List registration requests
- `GET /member-requests/{id}/` - Get request details
- `POST /member-requests/{id}/approve_request/` - Approve request
- `POST /member-requests/{id}/reject_request/` - Reject request

### Profile Management
- `GET /auth/profile/` - Get own profile
- `PATCH /auth/profile/` - Update own profile

## Security Features

1. **Role-Based Access Control**: Strict permission checking for all operations
2. **Approval Workflow**: Prevents unauthorized access
3. **Member Deactivation**: Soft deletion maintains data integrity
4. **Password Security**: Temporary passwords for direct additions
5. **Society Isolation**: Members can only access their society's data

## Postman Collection

A complete Postman collection is provided:
- **File**: `Member_Management_CRUD.postman_collection.json`
- **Features**: 
  - Complete CRUD operations testing
  - Authentication workflows
  - Approval process testing
  - Environment variables for easy testing

## Testing

Run the provided test scripts:
- `test_member_approval_workflow.py` - Complete workflow test
- `member_crud_test.py` - CRUD operations verification

## Implementation Details

### ViewSet: MemberViewSet
Located in `backend/society_management/views.py`

Key features:
- **QuerySet Filtering**: Members filtered by society based on user role
- **Permission System**: Custom permission logic for different actions
- **Serializer Selection**: Different serializers for different operations
- **Custom Update**: Profile update with permission checking
- **Soft Delete**: Deactivation instead of actual deletion

### Serializers
- `UserProfileSerializer`: Basic member profile information
- `EnhancedUserProfileSerializer`: Detailed member profile with additional information

### Models
- `User`: Extended Django user model with society-specific fields

## Usage Examples

### 1. Member Self-Registration
```bash
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

### 2. SUB_ADMIN Direct Member Addition
```bash
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

### 3. List Members (SUB_ADMIN)
```bash
GET /api/members/
Authorization: Bearer <SUB_ADMIN_TOKEN>
```

### 4. Update Member Profile (Member)
```bash
PATCH /api/members/{member_id}/
Authorization: Bearer <MEMBER_TOKEN>
{
    "first_name": "Updated Name"
}
```

## Error Handling

The system provides clear error messages for various scenarios:
- **Pending Approval**: Members attempting to login before approval
- **Permission Denied**: Unauthorized access attempts
- **Validation Errors**: Invalid data submissions
- **Not Found**: Non-existent resources

## Future Enhancements

1. **Bulk Operations**: Import/export members via CSV
2. **Advanced Filtering**: More sophisticated search and filter options
3. **Notification System**: Email/SMS notifications for approval status
4. **Activity Logging**: Track member profile changes
5. **Multi-Factor Authentication**: Enhanced security options