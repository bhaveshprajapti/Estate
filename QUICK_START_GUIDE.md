# 🚀 Quick Start Guide - Society Management API

Get up and running with the Society Management API in minutes!

## 📋 Prerequisites

1. **Postman** installed
2. **Django server** running (`python manage.py runserver`)
3. **Super Admin** account created (`python manage.py createsuperuser`)

## 🚀 5-Minute Setup

### Step 1: Import Collection & Environment

1. Open Postman
2. Click "Import"
3. Select these files:
   - `Society_Management_Full_API.postman_collection.json`
   - `Society_Management_Full_Environment.postman_environment.json`
4. Select "Society Management Environment - FULL"

### Step 2: Test Member Capabilities (Fastest Start)

1. **Open the Collection**: Expand "Society Management - FULL API Collection"
2. **Member Login**: 
   - Navigate to "🔐 Authentication System" → "👥 MEMBER Login"
   - Click "Send"
   - ✅ Success: Token auto-saved as `member_access_token`

3. **Test Member Features** (all use the member token automatically):
   - Profile Management: View and update your profile
   - Vehicle Management: Register and manage vehicles
   - Amenity Booking: Book society amenities
   - Complaint Submission: Submit maintenance requests
   - Marketplace: Post items and browse listings

### Step 3: Run Complete Member Workflow

Execute these requests IN ORDER:

1. `🔐 Authentication System` → `👥 MEMBER Login`
2. `🚗 Vehicle Management` → `🚗 Register Vehicle`
3. `🏖️ Amenity Management` → `📅 Book Amenity`
4. `📢 Complaint Management` → `📢 Submit Complaint`
5. `🛒 Marketplace` → `🛒 Create Marketplace Listing`

✅ **All IDs auto-populate** as you go!

## 🎯 Key Member Features (No Setup Required)

Just login as member and use these:

| Feature | Request Path | What It Does |
|---------|--------------|--------------|
| 🚗 Vehicle Registration | `/vehicles/` | Register your car/bike |
| 🏖️ Amenity Booking | `/amenity-bookings/` | Book swimming pool, gym, etc. |
| 📢 Submit Complaint | `/complaints/` | Report maintenance issues |
| 🛒 Marketplace Listing | `/marketplace/` | Sell items to neighbors |
| 👤 Profile Update | `/auth/profile/` | Update your information |
| 📊 Dashboard Stats | `/dashboard/stats/` | View your society stats |

## 🔧 Quick Admin Setup (10 Minutes)

Need full system access? Run these in order:

1. `🔐 Authentication System` → `👑 Super Admin Login`
2. `🔐 Authentication System` → `🔑 ADMIN Login`
3. `🏢 Society Management` → `🏗️ Create Society`
4. `🎭 SUB_ADMIN Invitation Flow` → `📧 Create SUB_ADMIN Invitation`
5. `🎭 SUB_ADMIN Invitation Flow` → `✅ Verify Invitation OTP`
6. `🎭 SUB_ADMIN Invitation Flow` → `🎯 Complete SUB_ADMIN Registration`

## 📱 Member Capabilities at a Glance

✅ **FULL Access**:
- Vehicle Management
- Amenity Booking
- Complaint Submission
- Marketplace Participation
- Profile Management
- Directory Access
- Notice Board
- Dashboard Statistics

❌ **RESTRICTED** (Security):
- Staff Management
- Visitor Pass Creation
- Gate Log Management
- Society Administration

## 🛠️ Environment Variables (Pre-set)

All test data is pre-configured:

- **Member**: `9876543210` / `member123456`
- **Admin**: `9000000001` / `admin123456`
- **Sub-Admin**: `9200000001` / `chairman123456`
- **Staff**: `9100000002` / `staff123456`

## 🎉 You're Ready!

Start with Member Login and explore the capabilities. Everything is designed to work out-of-the-box with automatic token management and ID population.

**Questions?** Check `FULL_API_COLLECTION_GUIDE.md` for complete documentation.

Happy testing! 🚀