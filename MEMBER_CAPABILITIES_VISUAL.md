# 🏠 Member Capabilities - Visual Guide

## 🎯 Member Role Overview

Members are residents of a society who have been approved by the SUB_ADMIN (Chairman). They have comprehensive access to society services while maintaining appropriate security boundaries.

```mermaid
graph TD
    A[MEMBER] --> B[Personal Management]
    A --> C[Community Services]
    A --> D[Communication]
    A --> E[Information Access]
    
    B --> B1[Profile Management]
    B --> B2[Vehicle Registration]
    
    C --> C1[Amenity Booking]
    C --> C2[Marketplace]
    C --> C3[Billing]
    
    D --> D1[Complaints]
    D --> D2[Service Requests]
    D --> D3[Helpdesk]
    
    E --> E1[Directory]
    E --> E2[Notices]
    E --> E3[Dashboard]
    
    style A fill:#4CAF50,color:white
    style B fill:#2196F3,color:white
    style C fill:#2196F3,color:white
    style D fill:#2196F3,color:white
    style E fill:#2196F3,color:white
```

## ✅ FULL ACCESS Capabilities

### 🚗 Vehicle Management
```mermaid
graph LR
    A[Member] --> B[Register Vehicle]
    A --> C[View Vehicles]
    A --> D[Update Vehicle]
    A --> E[Delete Vehicle]
    
    style A fill:#4CAF50,color:white
    style B fill:#8BC34A,color:white
    style C fill:#8BC34A,color:white
    style D fill:#8BC34A,color:white
    style E fill:#8BC34A,color:white
```

### 🏖️ Amenity Booking
```mermaid
graph LR
    A[Member] --> B[View Amenities]
    A --> C[Book Amenity]
    A --> D[View Bookings]
    A --> E[Cancel Booking]
    
    style A fill:#4CAF50,color:white
    style B fill:#8BC34A,color:white
    style C fill:#8BC34A,color:white
    style D fill:#8BC34A,color:white
    style E fill:#8BC34A,color:white
```

### 📉 Complaint Management
```mermaid
graph LR
    A[Member] --> B[Submit Complaint]
    A --> C[View Complaints]
    A --> D[Update Complaint]
    A --> E[Track Status]
    
    style A fill:#4CAF50,color:white
    style B fill:#8BC34A,color:white
    style C fill:#8BC34A,color:white
    style D fill:#8BC34A,color:white
    style E fill:#8BC34A,color:white
```

### 🛒 Marketplace
```mermaid
graph LR
    A[Member] --> B[Post Item]
    A --> C[Browse Items]
    A --> D[Update Listing]
    A --> E[Remove Listing]
    
    style A fill:#4CAF50,color:white
    style B fill:#8BC34A,color:white
    style C fill:#8BC34A,color:white
    style D fill:#8BC34A,color:white
    style E fill:#8BC34A,color:white
```

## 👁️ READ-ONLY Access

### 📚 Directory Access
```mermaid
graph LR
    A[Member] --> B[View Member Directory]
    A --> C[View Staff Directory]
    A --> D[Search Contacts]
    
    style A fill:#4CAF50,color:white
    style B fill:#FFC107,color:black
    style C fill:#FFC107,color:black
    style D fill:#FFC107,color:black
```

### 📰 Notices & Announcements
```mermaid
graph LR
    A[Member] --> B[View Society Notices]
    A --> C[Read Notice Details]
    
    style A fill:#4CAF50,color:white
    style B fill:#FFC107,color:black
    style C fill:#FFC107,color:black
```

### 💰 Billing Information
```mermaid
graph LR
    A[Member] --> B[View Own Bills]
    A --> C[Payment History]
    A --> D[Expense Tracking]
    
    style A fill:#4CAF50,color:white
    style B fill:#FFC107,color:black
    style C fill:#FFC107,color:black
    style D fill:#FFC107,color:black
```

## 🚫 RESTRICTED Functions (Security)

### 👨‍💼 Staff Management
```mermaid
graph LR
    A[Member] -->|REQUEST ONLY| B[Staff Services]
    A -->|DENIED| C[Create Staff]
    A -->|DENIED| D[Manage Staff]
    
    style A fill:#4CAF50,color:white
    style B fill:#FF9800,color:white
    style C fill:#F44336,color:white
    style D fill:#F44336,color:white
```

### 🎫 Visitor Management
```mermaid
graph LR
    A[Member] -->|REQUEST ONLY| B[Visitor Pass]
    A -->|DENIED| C[Create Pass]
    A -->|DENIED| D[Manage Passes]
    
    style A fill:#4CAF50,color:white
    style B fill:#FF9800,color:white
    style C fill:#F44336,color:white
    style D fill:#F44336,color:white
```

### 🚪 Gate Management
```mermaid
graph LR
    A[Member] -->|REQUEST ONLY| B[Gate Services]
    A -->|DENIED| C[Update Logs]
    A -->|DENIED| D[Manage Gates]
    
    style A fill:#4CAF50,color:white
    style B fill:#FF9800,color:white
    style C fill:#F44336,color:white
    style D fill:#F44336,color:white
```

## 🔐 Security Boundaries

### Role-Based Access Control
```mermaid
graph TD
    ADMIN[ADMIN<br/>👑 Full System Access] -->|Creates| SUB_ADMIN[SUB_ADMIN<br/>🎭 Society Chairman]
    SUB_ADMIN -->|Approves| MEMBER[MEMBER<br/>🏠 Resident]
    SUB_ADMIN -->|Creates| STAFF[STAFF<br/>👮 Security/Service]
    
    MEMBER -->|Can Request| SUB_ADMIN
    MEMBER -->|Can Request| STAFF
    STAFF -->|Reports to| SUB_ADMIN
    
    style ADMIN fill:#F44336,color:white
    style SUB_ADMIN fill:#FF9800,color:white
    style MEMBER fill:#4CAF50,color:white
    style STAFF fill:#2196F3,color:white
```

## 📊 Member Dashboard Overview

Members have access to a personalized dashboard showing:

```mermaid
graph TD
    A[Member Dashboard] --> B[Assigned Flats<br/>🏠 2]
    A --> C[Pending Bills<br/>💰 3]
    A --> D[Open Complaints<br/>📝 1]
    A --> E[Upcoming Bookings<br/>📅 2]
    A --> F[Recent Notices<br/>📢 5]
    
    style A fill:#9C27B0,color:white
    style B fill:#E91E63,color:white
    style C fill:#E91E63,color:white
    style D fill:#E91E63,color:white
    style E fill:#E91E63,color:white
    style F fill:#E91E63,color:white
```

## 🔄 Request Workflow for Restricted Services

```mermaid
graph LR
    A[Member] --> B[Submit Request<br/>via Helpdesk/Complaints]
    B --> C[SUB_ADMIN Review]
    C --> D[Action Taken]
    D --> E[Member Notified]
    
    style A fill:#4CAF50,color:white
    style B fill:#FF9800,color:white
    style C fill:#FF9800,color:white
    style D fill:#FF9800,color:white
    style E fill:#4CAF50,color:white
```

## 📋 Summary Table

| Capability | Access Level | Through API | Notes |
|------------|--------------|-------------|-------|
| **Profile Management** | ✅ FULL | `PATCH /auth/profile/` | Update personal info |
| **Vehicle Registration** | ✅ FULL | `POST /vehicles/` | Add/Manage vehicles |
| **Amenity Booking** | ✅ FULL | `POST /amenity-bookings/` | Book society amenities |
| **Complaint Submission** | ✅ FULL | `POST /complaints/` | Report issues |
| **Marketplace Listing** | ✅ FULL | `POST /marketplace/` | Buy/Sell items |
| **Directory Access** | 👁️ READ-ONLY | `GET /directory/` | View contacts |
| **Notices Access** | 👁️ READ-ONLY | `GET /notices/` | View announcements |
| **Billing Info** | 👁️ READ-ONLY | `GET /maintenance-bills/` | View own bills |
| **Staff Creation** | 🚫 DENIED | N/A | Restricted to SUB_ADMIN |
| **Visitor Passes** | 🚫 DENIED | N/A | Restricted to SUB_ADMIN |
| **Gate Management** | 🚫 DENIED | N/A | Restricted to STAFF |

## 🎯 Key Benefits for Members

1. **✅ Comprehensive Access**: Full control over personal services
2. **✅ Community Participation**: Active role in society activities
3. **✅ Transparent Communication**: Clear channels for requests and issues
4. **✅ Security Assured**: Proper access controls for sensitive operations
5. **✅ Self-Service**: Most needs can be addressed independently

## 🔒 Security Benefits

1. **🔐 Role Isolation**: Members can only access their society's data
2. **🔐 Action Logging**: All member actions are recorded for audit
3. **🔐 Request Workflow**: Restricted functions follow approval process
4. **🔐 Data Privacy**: Member information protected from unauthorized access

This visual guide demonstrates that members have extensive capabilities in the Society Management System while maintaining appropriate security boundaries for sensitive operations.