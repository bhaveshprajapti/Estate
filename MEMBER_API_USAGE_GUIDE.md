# 📱 Member API Usage Guide

This guide provides step-by-step instructions for members to use the Society Management System API endpoints to perform all the activities you requested.

## 📋 Prerequisites

1. **Member Account**: Must be registered and approved by SUB_ADMIN
2. **API Access**: Server running at `http://localhost:8000`
3. **Authentication Token**: JWT token obtained after login

## 🔐 Authentication

### 1. Member Login
```bash
curl -X POST http://localhost:8000/api/auth/login-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "9876543210",
    "password": "member_password"
  }'
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "id": 123,
    "phone_number": "9876543210",
    "email": "member@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "MEMBER",
    "society": 1
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

**Save the access token** for subsequent requests:
```bash
ACCESS_TOKEN="your_access_token_here"
```

## 🚗 Vehicle Management

### 1. Register a New Vehicle
```bash
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "vehicle_number": "MH01AB1234",
    "type": "CAR",
    "brand": "Honda",
    "model": "City",
    "color": "White",
    "owner": 123,
    "flat": 456
  }'
```

### 2. List My Vehicles
```bash
curl -X GET http://localhost:8000/api/vehicles/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 3. Update Vehicle Details
```bash
curl -X PUT http://localhost:8000/api/vehicles/789/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "color": "Black",
    "model": "Civic"
  }'
```

### 4. Delete a Vehicle
```bash
curl -X DELETE http://localhost:8000/api/vehicles/789/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 🏖️ Amenity Booking

### 1. View Available Amenities
```bash
curl -X GET http://localhost:8000/api/amenities/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2. Book an Amenity
```bash
curl -X POST http://localhost:8000/api/amenity-bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "amenity": 12,
    "booked_by": 123,
    "booking_date": "2025-01-15",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "purpose": "Family swimming"
  }'
```

### 3. View My Bookings
```bash
curl -X GET http://localhost:8000/api/amenity-bookings/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4. Cancel a Booking
```bash
curl -X DELETE http://localhost:8000/api/amenity-bookings/45/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 📉 Bill Management

### 1. View My Bills
```bash
curl -X GET http://localhost:8000/api/maintenance-bills/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2. View Common Expenses
```bash
curl -X GET http://localhost:8000/api/common-expenses/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 📢 Complaint Management

### 1. Submit a Complaint
```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Water Leakage in Flat",
    "description": "There is water leakage in the bathroom ceiling",
    "flat": 456,
    "raised_by": 123,
    "priority": "HIGH",
    "category": "MAINTENANCE"
  }'
```

### 2. View My Complaints
```bash
curl -X GET http://localhost:8000/api/complaints/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 3. Update a Complaint
```bash
curl -X PUT http://localhost:8000/api/complaints/78/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "status": "IN_PROGRESS",
    "notes": "Issue has been acknowledged by maintenance team"
  }'
```

## 🛒 Marketplace

### 1. List Marketplace Items
```bash
curl -X GET http://localhost:8000/api/marketplace/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2. Post an Item for Sale
```bash
curl -X POST http://localhost:8000/api/marketplace/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Used Bicycle",
    "description": "Well-maintained bicycle for sale",
    "price": 5000.00,
    "category": "SPORTS",
    "posted_by": 123,
    "status": "ACTIVE"
  }'
```

### 3. Update My Listing
```bash
curl -X PUT http://localhost:8000/api/marketplace/123/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "price": 4500.00,
    "description": "Well-maintained bicycle for sale - slightly negotiable"
  }'
```

## 📞 Helpdesk Services

### 1. View Helpdesk Contacts
```bash
curl -X GET http://localhost:8000/api/helpdesk-contacts/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2. View Service Categories
```bash
curl -X GET http://localhost:8000/api/helpdesk-designations/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 👥 Directory Access

### 1. View Society Directory
```bash
curl -X GET http://localhost:8000/api/directory/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 📰 Notices & Announcements

### 1. View Society Notices
```bash
curl -X GET http://localhost:8000/api/notices/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## 👤 Profile Management

### 1. View Own Profile
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2. Update Profile
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "first_name": "Jonathan",
    "occupation": "Software Engineer",
    "emergency_contact_name": "Jane Smith",
    "emergency_contact_phone": "9876543211"
  }'
```

## 📊 Dashboard Statistics

### 1. View Personal Dashboard Stats
```bash
curl -X GET http://localhost:8000/api/dashboard/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "my_flats": 1,
  "pending_bills": 2,
  "my_complaints": 1,
  "my_bookings": 3
}
```

## 🚫 Restricted Actions (Managed by SUB_ADMIN)

The following actions are restricted and can only be performed by SUB_ADMIN (Chairman) for security reasons:

### Staff Management
- Creating staff accounts
- Assigning staff duties
- Managing staff schedules

### Visitor Management
- Creating visitor passes
- Managing gate logs

### Society Administration
- Creating amenities
- Managing society settings
- Approving member registrations

## 📞 Requesting Restricted Services

For services that require SUB_ADMIN approval, members can:

### 1. Submit Helpdesk Request
```bash
curl -X POST http://localhost:8000/api/complaints/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Visitor Pass Request",
    "description": "Need visitor pass for family visit on 2025-01-20",
    "flat": 456,
    "raised_by": 123,
    "category": "VISITOR",
    "priority": "MEDIUM"
  }'
```

## 🛠️ Error Handling

Common error responses:

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

## 🎯 Best Practices

1. **Always use HTTPS** in production environments
2. **Store tokens securely** and refresh them when needed
3. **Handle errors gracefully** in your applications
4. **Validate data** before sending requests
5. **Use appropriate HTTP methods** for each operation
6. **Check response status codes** before processing data

## 📞 Support

For issues with the API or to request additional features:
1. Submit a complaint through the system
2. Contact your society's helpdesk
3. Reach out to your SUB_ADMIN (Chairman)

## 🔄 API Version Information

- **API Version**: v1
- **Base URL**: http://localhost:8000/api/
- **Authentication**: JWT Bearer Tokens
- **Response Format**: JSON

This guide covers all the capabilities available to members in the Society Management System. Members have comprehensive access to manage their personal information, vehicles, bookings, complaints, and other society services while maintaining appropriate security boundaries.