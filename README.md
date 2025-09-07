# Society Management & Digitization Platform

A comprehensive Django REST API backend for managing residential societies with features for billing, visitor management, community engagement, and more.

## 🏗️ Project Overview

This platform digitizes society management operations including:
- **User Management**: Multi-role system (Admin, Sub-Admin, Member, Staff)
- **Billing System**: Maintenance bills and shared expenses
- **Community Features**: Notices, amenity booking, marketplace
- **Security**: Visitor management and complaint tracking
- **Authentication**: JWT-based secure authentication

## 🚀 Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: PostgreSQL (SQLite for development)
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: DRF Spectacular (Swagger)
- **Environment**: Python 3.12+

## 📋 Features

### Core Management
- ✅ Multi-role user system (Admin, Sub-Admin, Member, Staff)
- ✅ Society and flat management
- ✅ Vehicle registration
- ✅ JWT authentication with refresh tokens

### Billing & Payments
- ✅ Monthly maintenance bill generation
- ✅ Common expense management with auto-splitting
- ✅ Payment tracking (online/offline)
- ✅ Transaction history

### Community Engagement
- ✅ Notice board for announcements
- ✅ Amenity booking system
- ✅ Marketplace for member listings
- ✅ Job board for community jobs

### Security & Operations
- ✅ Visitor log management with pass codes
- ✅ Complaint tracking system
- ✅ Staff duty assignment
- ✅ Role-based access control

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (optional, SQLite included for development)
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd society-management-platform
```

2. **Set up virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --phone_number=9999999999 --email=admin@test.com
```

6. **Run the server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **API Schema**: `http://localhost:8000/api/schema/`

### Authentication Endpoints
```
POST /api/auth/register/     - User registration
POST /api/auth/login/        - User login
POST /api/auth/logout/       - User logout
GET  /api/auth/profile/      - Get user profile
POST /api/auth/token/refresh/ - Refresh JWT token
```

### Core Endpoints
```
GET|POST /api/societies/           - Society management
GET|POST /api/flats/              - Flat management
GET|POST /api/vehicles/           - Vehicle registration
GET|POST /api/maintenance-bills/  - Billing system
GET|POST /api/common-expenses/    - Shared expenses
GET|POST /api/notices/            - Notice board
GET|POST /api/amenities/          - Amenity management
GET|POST /api/amenity-bookings/   - Booking system
GET|POST /api/visitors/           - Visitor logs
GET|POST /api/complaints/         - Complaint system
GET|POST /api/marketplace/        - Community marketplace
GET|POST /api/jobs/               - Job listings
```

## 🧪 Testing

### Test Credentials
```bash
# Admin User
Phone: 1111111111, Password: test123

# Sub-Admin User  
Phone: 2222222222, Password: test123

# Member User
Phone: 3333333333, Password: test123

# Staff User
Phone: 4444444444, Password: test123
```

### Sample API Calls

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1111111111", "password": "test123"}'
```

**Create Society:**
```bash
curl -X POST http://localhost:8000/api/societies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Green Valley Apartments",
    "address": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  }'
```

## 🗄️ Database Schema

### Core Tables
- **User**: Multi-role user management
- **Society**: Residential society details
- **Flat**: Individual units within societies
- **Vehicle**: Member vehicle registration

### Billing Tables
- **MaintenanceBill**: Monthly maintenance charges
- **CommonExpense**: Shared society expenses
- **CommonExpenseSplit**: Expense distribution per flat

### Community Tables
- **Notice**: Announcements and notices
- **Amenity**: Bookable facilities
- **AmenityBooking**: Booking requests
- **MarketplaceListing**: Member business listings
- **JobListing**: Community job postings

### Security Tables
- **VisitorLog**: Visitor entry/exit tracking
- **Complaint**: Issue tracking and resolution

## 🔧 Configuration

### Environment Variables
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=society_platform
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# For SQLite development
USE_SQLITE=True

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### Database Migration
```bash
# Switch to PostgreSQL
# 1. Update .env file with PostgreSQL credentials
# 2. Set USE_SQLITE=False
# 3. Run migrations
python manage.py migrate
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for Celery
- [ ] Configure static file serving
- [ ] Set up SSL certificates
- [ ] Configure environment variables
- [ ] Set up monitoring and logging

### Docker Deployment (Coming Soon)
```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Testing Guide

See [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) for detailed testing instructions.

## 📊 Test Results

See [TEST_RESULTS.md](TEST_RESULTS.md) for comprehensive test results.

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Password hashing with Django's built-in system
- CORS protection
- SQL injection prevention through Django ORM
- XSS protection through DRF serializers

## 📈 Future Enhancements

- [ ] Real-time notifications (WebSocket)
- [ ] Payment gateway integration
- [ ] Mobile app support
- [ ] AI-powered visitor recognition
- [ ] IoT device integration
- [ ] Multi-language support
- [ ] Advanced reporting and analytics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Developer**: Naman Doshi
- **Version**: 1.0
- **Date**: August 2025

## 📞 Support

For support and queries:
- Create an issue in the repository
- Email: support@societyplatform.com

---

**Made with ❤️ for better society management**