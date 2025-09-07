# Society Management Platform - API Testing Guide

## Base URL
```
http://localhost:8000/api/
```

## Authentication Endpoints

### 1. User Registration
**POST** `/api/auth/register/`

```json
{
    "phone_number": "9876543210",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "MEMBER"
}
```

### 2. User Login
**POST** `/api/auth/login/`

```json
{
    "phone_number": "9876543210",
    "password": "securepassword123"
}
```

Response includes access and refresh tokens:
```json
{
    "message": "Login successful",
    "user": {...},
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 3. Get User Profile
**GET** `/api/auth/profile/`

Headers:
```
Authorization: Bearer <access_token>
```

### 4. Logout
**POST** `/api/auth/logout/`

```json
{
    "refresh": "<refresh_token>"
}
```

## Core Management Endpoints

### Societies
**GET** `/api/societies/` - List all societies
**POST** `/api/societies/` - Create new society
**GET** `/api/societies/{id}/` - Get society details
**PUT** `/api/societies/{id}/` - Update society
**DELETE** `/api/societies/{id}/` - Delete society

Sample Society Creation:
```json
{
    "name": "Green Valley Apartments",
    "address": "123 Main Street, Green Valley",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "registration_number": "REG123456"
}
```

### Flats
**GET** `/api/flats/` - List all flats
**POST** `/api/flats/` - Create new flat

Sample Flat Creation:
```json
{
    "society": 1,
    "block_number": "A",
    "flat_number": "101",
    "type": "2BHK",
    "area_sqft": 1200,
    "owner": 2,
    "tenant": null
}
```

### Vehicles
**GET** `/api/vehicles/` - List vehicles
**POST** `/api/vehicles/` - Register vehicle

```json
{
    "owner": 2,
    "flat": 1,
    "vehicle_number": "MH01AB1234",
    "type": "CAR"
}
```

## Billing Endpoints

### Maintenance Bills
**GET** `/api/maintenance-bills/` - List bills
**POST** `/api/maintenance-bills/` - Create bill

```json
{
    "flat": 1,
    "amount": "5000.00",
    "due_date": "2025-09-30",
    "billing_period_start": "2025-09-01",
    "billing_period_end": "2025-09-30"
}
```

### Common Expenses
**GET** `/api/common-expenses/` - List expenses
**POST** `/api/common-expenses/` - Create expense
**POST** `/api/common-expenses/{id}/split_expense/` - Split expense among flats

```json
{
    "society": 1,
    "title": "Diwali Celebration",
    "total_amount": "10000.00",
    "invoice_attachment": "http://example.com/invoice.pdf"
}
```

## Community Endpoints

### Notices
**GET** `/api/notices/` - List notices
**POST** `/api/notices/` - Create notice

```json
{
    "title": "Water Supply Maintenance",
    "content": "Water supply will be interrupted tomorrow from 10 AM to 2 PM",
    "society": 1
}
```

### Amenities
**GET** `/api/amenities/` - List amenities
**POST** `/api/amenities/` - Create amenity

```json
{
    "society": 1,
    "name": "Clubhouse",
    "booking_rules": "Maximum 4 hours booking. Advance booking required."
}
```

### Amenity Bookings
**GET** `/api/amenity-bookings/` - List bookings
**POST** `/api/amenity-bookings/` - Create booking

```json
{
    "amenity": 1,
    "start_time": "2025-09-15T18:00:00Z",
    "end_time": "2025-09-15T22:00:00Z"
}
```

## Security Endpoints

### Visitor Logs
**GET** `/api/visitors/` - List visitors
**POST** `/api/visitors/` - Log visitor

```json
{
    "name": "Delivery Person",
    "phone_number": "9876543210",
    "flat_to_visit": 1,
    "pass_code": "ABC123"
}
```

### Complaints
**GET** `/api/complaints/` - List complaints
**POST** `/api/complaints/` - Create complaint

```json
{
    "flat": 1,
    "title": "Plumbing Issue",
    "description": "Kitchen sink is leaking"
}
```

## Marketplace Endpoints

### Marketplace Listings
**GET** `/api/marketplace/` - List marketplace items
**POST** `/api/marketplace/` - Create listing

```json
{
    "title": "Home Tutoring Services",
    "description": "Mathematics and Science tutoring for grades 6-10"
}
```

### Job Listings
**GET** `/api/jobs/` - List job postings
**POST** `/api/jobs/` - Create job posting

```json
{
    "title": "Part-time Cook Required",
    "description": "Looking for a cook for evening meals, 3 days a week"
}
```

## Testing with cURL

### Login Example:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "9999999999",
    "password": "admin123"
  }'
```

### Create Society Example:
```bash
curl -X POST http://localhost:8000/api/societies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "name": "Test Society",
    "address": "Test Address",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  }'
```

## Testing with Postman

1. Import the collection by creating requests for each endpoint
2. Set up environment variables:
   - `base_url`: http://localhost:8000/api
   - `access_token`: (set after login)
3. Use Bearer Token authentication for protected endpoints
4. Test the complete workflow:
   - Register/Login user
   - Create society
   - Create flats
   - Create maintenance bills
   - Create notices
   - Book amenities

## API Documentation

Visit `http://localhost:8000/api/docs/` for interactive Swagger documentation once the server is running.

## Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error