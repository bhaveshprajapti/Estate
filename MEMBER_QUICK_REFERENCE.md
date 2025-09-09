# 🏠 Member Quick Reference Card

## 🔧 What You Can Do (FULL ACCESS)

### 🚗 Vehicle Management
- **Register your vehicles** - Add car/bike details
- **Manage vehicle info** - Update or remove vehicles
- **API**: `POST /api/vehicles/`

### 🏖️ Amenity Booking
- **Book society amenities** - Pool, gym, community hall
- **Manage bookings** - View, update, cancel reservations
- **API**: `POST /api/amenity-bookings/`

### 💰 Bill Management
- **View your bills** - See maintenance charges
- **Track payments** - Check payment history
- **API**: `GET /api/maintenance-bills/`

### 📉 Complaint System
- **Submit complaints** - Report maintenance issues
- **Track resolution** - Follow complaint status
- **API**: `POST /api/complaints/`

### 🛒 Marketplace
- **List items** - Sell your stuff to neighbors
- **Browse listings** - Find what others are selling
- **API**: `POST /api/marketplace/`

### 👥 Directory & Contacts
- **View member directory** - Find neighbor contacts
- **Access helpdesk** - Get service contact info
- **API**: `GET /api/directory/`

## 📞 What You Can Request (THROUGH HELPDESK)

### 👨‍💼 Staff Services
- **Cannot create staff** - Only SUB_ADMIN can
- **Can request services** - Submit through helpdesk
- **Contact existing staff** - Use directory

### 🎫 Visitor Management
- **Cannot create passes** - Only SUB_ADMIN can
- **Can request passes** - Submit through complaints
- **Report visitors** - Inform security

### 🚪 Gate Services
- **Cannot update logs** - Only security staff can
- **Can request services** - Submit through helpdesk
- **Report gate issues** - File complaints

## 🔐 Login & Authentication

### Member Login
```bash
POST /api/auth/login-password/
{
  "phone_number": "YOUR_PHONE",
  "password": "YOUR_PASSWORD"
}
```

### Use Your Token
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 🚀 Quick Start Steps

1. **Login** to the system
2. **Update your profile** with complete information
3. **Register your vehicles** in the vehicle management section
4. **Explore amenities** and make your first booking
5. **Check the marketplace** for items you need
6. **Submit any complaints** for maintenance issues
7. **Connect with neighbors** through the directory

## 📞 Need Help?

### For Restricted Services:
1. Go to **Complaints** section
2. Submit a request with details
3. SUB_ADMIN will process your request

### For Technical Issues:
1. Contact your society's **helpdesk**
2. Use the **directory** to find helpdesk contacts
3. Submit a **service request**

## 🎯 Remember

- ✅ You have **full access** to personal and community services
- ⚠️ Security-sensitive functions require **administrative approval**
- 📞 Always use the **helpdesk system** for special requests
- 📋 Keep your **profile updated** for better service

**Happy Living in Your Society!** 🏘️