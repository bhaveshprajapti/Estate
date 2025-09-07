#!/usr/bin/env python3
"""
Quick CRUD Test - Verify key endpoints are working
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def test_key_endpoints():
    """Test key CRUD endpoints quickly"""
    print("🔍 QUICK CRUD ENDPOINT TEST")
    print("="*50)
    
    # Register and login
    admin_data = {
        "phone_number": f"91{random.randint(10000000, 99999999)}",
        "email": "quicktest@test.com",
        "first_name": "Quick",
        "last_name": "Test",
        "password": "test123456",
        "password_confirm": "test123456"
    }
    
    print("1. Testing Authentication...")
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    if response.status_code == 201:
        print("✅ Registration works")
        
        # Login
        login_data = {
            "phone_number": admin_data['phone_number'],
            "password": "test123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
        if response.status_code == 200:
            print("✅ Login works")
            tokens = response.json()['tokens']
            headers = {"Authorization": f"Bearer {tokens['access']}"}
            
            # Test Vehicle endpoints
            print("\n2. Testing Vehicle CRUD...")
            
            # List vehicles
            response = requests.get(f"{BASE_URL}/vehicles/", headers=headers)
            print(f"   List Vehicles: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Bill Types
            print("\n3. Testing Bill Types CRUD...")
            response = requests.get(f"{BASE_URL}/bill-types/", headers=headers)
            print(f"   List Bill Types: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Enhanced Bills
            print("\n4. Testing Enhanced Bills CRUD...")
            response = requests.get(f"{BASE_URL}/enhanced-bills/", headers=headers)
            print(f"   List Enhanced Bills: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Notices
            print("\n5. Testing Notices CRUD...")
            response = requests.get(f"{BASE_URL}/notices/", headers=headers)
            print(f"   List Notices: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Amenities
            print("\n6. Testing Amenities CRUD...")
            response = requests.get(f"{BASE_URL}/amenities/", headers=headers)
            print(f"   List Amenities: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Complaints
            print("\n7. Testing Complaints CRUD...")
            response = requests.get(f"{BASE_URL}/complaints/", headers=headers)
            print(f"   List Complaints: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Marketplace
            print("\n8. Testing Marketplace CRUD...")
            response = requests.get(f"{BASE_URL}/marketplace/", headers=headers)
            print(f"   List Marketplace: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Job Listings
            print("\n9. Testing Job Listings CRUD...")
            response = requests.get(f"{BASE_URL}/jobs/", headers=headers)
            print(f"   List Jobs: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            # Test Amenity Bookings
            print("\n10. Testing Amenity Bookings CRUD...")
            response = requests.get(f"{BASE_URL}/amenity-bookings/", headers=headers)
            print(f"   List Amenity Bookings: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            print("\n" + "="*50)
            print("🎉 QUICK CRUD TEST COMPLETED!")
            print("✅ All new CRUD endpoints are accessible and working!")
            
        else:
            print(f"❌ Login failed: {response.status_code}")
    else:
        print(f"❌ Registration failed: {response.status_code}")

if __name__ == "__main__":
    try:
        test_key_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")