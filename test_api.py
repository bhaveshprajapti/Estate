#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Society Management System
Tests all endpoints and workflows
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_DATA = {}

def print_test_result(test_name, response, expected_status=200):
    """Print formatted test results"""
    status = "✅ PASS" if response.status_code == expected_status else "❌ FAIL"
    print(f"{status} {test_name}")
    print(f"   Status: {response.status_code} (Expected: {expected_status})")
    if response.status_code != expected_status:
        print(f"   Error: {response.text}")
    print()

def test_authentication():
    """Test authentication endpoints"""
    print("🔐 TESTING AUTHENTICATION ENDPOINTS")
    print("=" * 50)
    
    # Test user registration
    admin_data = {
        "phone_number": "1111111111",
        "email": "admin@test.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "test123456",
        "password_confirm": "test123456",
        "role": "ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    print_test_result("Admin Registration", response, 201)
    
    if response.status_code == 201:
        TEST_DATA['admin_tokens'] = response.json()['tokens']
    
    # Test login
    login_data = {
        "phone_number": "1111111111",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print_test_result("Admin Login", response, 200)
    
    if response.status_code == 200:
        TEST_DATA['admin_tokens'] = response.json()['tokens']
        TEST_DATA['admin_user'] = response.json()['user']
    
    # Test profile access
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print_test_result("Profile Access", response, 200)

def test_society_management():
    """Test society management endpoints"""
    print("🏢 TESTING SOCIETY MANAGEMENT")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # Create society
    society_data = {
        "name": "Green Valley Apartments",
        "address": "123 Main Street",
        "city": "Mumbai", 
        "state": "Maharashtra",
        "pincode": "400001",
        "registration_number": "REG123456"
    }
    
    response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
    print_test_result("Create Society", response, 201)
    
    if response.status_code == 201:
        TEST_DATA['society'] = response.json()
    
    # Get societies
    response = requests.get(f"{BASE_URL}/societies/", headers=headers)
    print_test_result("List Societies", response, 200)
    
    # Create society settings
    settings_data = {
        "society": TEST_DATA['society']['id'],
        "default_maintenance_amount": "2500.00",
        "maintenance_due_day": 5,
        "late_fee_percentage": "5.00",
        "allow_marketplace": True,
        "visitor_approval_required": True
    }
    
    response = requests.post(f"{BASE_URL}/society-settings/", json=settings_data, headers=headers)
    print_test_result("Create Society Settings", response, 201)

def test_user_management():
    """Test enhanced user management"""
    print("👥 TESTING USER MANAGEMENT")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # Create chairman invitation
    invitation_data = {
        "society": TEST_DATA['society']['id'],
        "email": "chairman@test.com",
        "phone_number": "2222222222",
        "first_name": "Chairman",
        "last_name": "User",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/chairman-invitations/", json=invitation_data, headers=headers)
    print_test_result("Create Chairman Invitation", response, 201)
    
    if response.status_code == 201:
        TEST_DATA['invitation'] = response.json()
    
    # List invitations
    response = requests.get(f"{BASE_URL}/chairman-invitations/", headers=headers)
    print_test_result("List Chairman Invitations", response, 200)
    
    # Register chairman directly for testing
    chairman_data = {
        "phone_number": "2222222222",
        "email": "chairman@test.com",
        "first_name": "Chairman",
        "last_name": "User",
        "password": "test123456",
        "password_confirm": "test123456",
        "role": "SUB_ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=chairman_data)
    print_test_result("Chairman Registration", response, 201)
    
    # Chairman login
    chairman_login = {
        "phone_number": "2222222222",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=chairman_login)
    print_test_result("Chairman Login", response, 200)
    
    if response.status_code == 200:
        TEST_DATA['chairman_tokens'] = response.json()['tokens']
        TEST_DATA['chairman_user'] = response.json()['user']

def test_staff_management():
    """Test staff management"""
    print("👨‍💼 TESTING STAFF MANAGEMENT")
    print("=" * 50)
    
    chairman_headers = {"Authorization": f"Bearer {TEST_DATA['chairman_tokens']['access']}"}
    
    # Create staff category
    category_data = {
        "name": "Security",
        "description": "Security personnel for the society",
        "society": TEST_DATA['society']['id']
    }
    
    response = requests.post(f"{BASE_URL}/staff-categories/", json=category_data, headers=chairman_headers)
    print_test_result("Create Staff Category", response, 201)
    
    if response.status_code == 201:
        TEST_DATA['staff_category'] = response.json()
    
    # Register staff member
    staff_data = {
        "phone_number": "4444444444",
        "email": "staff@test.com",
        "first_name": "Staff",
        "last_name": "Member",
        "password": "test123456",
        "password_confirm": "test123456",
        "role": "STAFF"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=staff_data)
    print_test_result("Staff Registration", response, 201)
    
    # Create staff profile would require additional endpoint
    # List staff categories
    response = requests.get(f"{BASE_URL}/staff-categories/", headers=chairman_headers)
    print_test_result("List Staff Categories", response, 200)

def test_permissions():
    """Test permission system"""
    print("🔒 TESTING PERMISSION SYSTEM")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # List permissions
    response = requests.get(f"{BASE_URL}/permissions/", headers=headers)
    print_test_result("List Permissions", response, 200)
    
    # List role permissions
    response = requests.get(f"{BASE_URL}/role-permissions/", headers=headers)
    print_test_result("List Role Permissions", response, 200)

def test_flat_management():
    """Test flat management"""
    print("🏠 TESTING FLAT MANAGEMENT")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # Create flat
    flat_data = {
        "society": TEST_DATA['society']['id'],
        "block_number": "A",
        "flat_number": "101",
        "type": "2BHK",
        "area_sqft": 1200
    }
    
    response = requests.post(f"{BASE_URL}/flats/", json=flat_data, headers=headers)
    print_test_result("Create Flat", response, 201)
    
    if response.status_code == 201:
        TEST_DATA['flat'] = response.json()
    
    # List flats
    response = requests.get(f"{BASE_URL}/flats/", headers=headers)
    print_test_result("List Flats", response, 200)

def test_billing_system():
    """Test billing and expense management"""
    print("💰 TESTING BILLING SYSTEM")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # Create fee structure
    fee_data = {
        "society": TEST_DATA['society']['id'],
        "flat_type": "2BHK",
        "maintenance_amount": "2500.00",
        "parking_fee": "200.00",
        "amenity_fee": "300.00"
    }
    
    response = requests.post(f"{BASE_URL}/fee-structures/", json=fee_data, headers=headers)
    print_test_result("Create Fee Structure", response, 201)
    
    # Create maintenance bill
    bill_data = {
        "flat": TEST_DATA['flat']['id'],
        "amount": "2500.00",
        "due_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "billing_period_start": datetime.now().strftime('%Y-%m-%d'),
        "billing_period_end": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    response = requests.post(f"{BASE_URL}/maintenance-bills/", json=bill_data, headers=headers)
    print_test_result("Create Maintenance Bill", response, 201)
    
    # Create common expense
    expense_data = {
        "society": TEST_DATA['society']['id'],
        "title": "Diwali Decoration",
        "total_amount": "5000.00"
    }
    
    response = requests.post(f"{BASE_URL}/common-expenses/", json=expense_data, headers=headers)
    print_test_result("Create Common Expense", response, 201)

def test_community_features():
    """Test community features"""
    print("🏘️ TESTING COMMUNITY FEATURES")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    
    # Create notice
    notice_data = {
        "title": "Important Announcement",
        "content": "Please note the new visiting hours.",
        "society": TEST_DATA['society']['id']
    }
    
    response = requests.post(f"{BASE_URL}/notices/", json=notice_data, headers=headers)
    print_test_result("Create Notice", response, 201)
    
    # Create amenity
    amenity_data = {
        "society": TEST_DATA['society']['id'],
        "name": "Clubhouse",
        "booking_rules": "Advance booking required"
    }
    
    response = requests.post(f"{BASE_URL}/amenities/", json=amenity_data, headers=headers)
    print_test_result("Create Amenity", response, 201)

def test_dashboard_stats():
    """Test dashboard statistics"""
    print("📊 TESTING DASHBOARD STATISTICS")
    print("=" * 50)
    
    # Admin dashboard
    admin_headers = {"Authorization": f"Bearer {TEST_DATA['admin_tokens']['access']}"}
    response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=admin_headers)
    print_test_result("Admin Dashboard Stats", response, 200)
    
    if response.status_code == 200:
        print(f"   Admin Stats: {response.json()}")
    
    # Chairman dashboard
    chairman_headers = {"Authorization": f"Bearer {TEST_DATA['chairman_tokens']['access']}"}
    response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=chairman_headers)
    print_test_result("Chairman Dashboard Stats", response, 200)
    
    if response.status_code == 200:
        print(f"   Chairman Stats: {response.json()}")

def main():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE API TESTING")
    print("=" * 50)
    print()
    
    try:
        test_authentication()
        test_society_management()
        test_user_management()
        test_staff_management()
        test_permissions()
        test_flat_management()
        test_billing_system()
        test_community_features()
        test_dashboard_stats()
        
        print("🎉 ALL TESTS COMPLETED!")
        print("Check the results above for any failures.")
        
    except KeyError as e:
        print(f"❌ Test failed due to missing data: {e}")
        print("This might be due to a previous test failure.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()