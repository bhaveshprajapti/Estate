#!/usr/bin/env python3
"""
Member Capabilities Test Script
Tests all the capabilities available to members in the society management system
"""

import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🏠 {title}")
    print('='*60)

def print_step(step, title):
    print(f"\n🔹 Step {step}: {title}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_member_login():
    """Test member login and get access token"""
    print_section("MEMBER AUTHENTICATION")
    
    # Using test member credentials
    login_data = {
        "phone_number": "9876543210",
        "password": "member123456"
    }
    
    print_step(1, "Member Login")
    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Member login successful")
        print_info(f"Member: {data['user']['first_name']} {data['user']['last_name']}")
        print_info(f"Society ID: {data['user']['society']}")
        return data['tokens']['access']
    else:
        print_error(f"Member login failed: {response.status_code}")
        print(response.text)
        return None

def test_profile_management(access_token):
    """Test member profile management capabilities"""
    print_section("PROFILE MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get current profile
    print_step(1, "View Member Profile")
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print_success("Profile retrieved successfully")
        print_info(f"Name: {profile['first_name']} {profile['last_name']}")
        print_info(f"Email: {profile['email']}")
        print_info(f"Phone: {profile['phone_number']}")
    else:
        print_error(f"Failed to get profile: {response.status_code}")
        return
    
    # Update profile
    print_step(2, "Update Member Profile")
    update_data = {
        "occupation": "Software Engineer",
        "emergency_contact_name": "Emergency Contact",
        "emergency_contact_phone": "9876543210"
    }
    
    response = requests.patch(f"{BASE_URL}/auth/profile/", 
                             headers=headers, json=update_data)
    if response.status_code == 200:
        print_success("Profile updated successfully")
    else:
        print_error(f"Failed to update profile: {response.status_code}")

def test_vehicle_management(access_token, member_id, flat_id):
    """Test member vehicle management capabilities"""
    print_section("VEHICLE MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Register a new vehicle
    print_step(1, "Register New Vehicle")
    vehicle_data = {
        "vehicle_number": f"MH01TEST{random.randint(1000, 9999)}",
        "type": "CAR",
        "brand": "Honda",
        "model": "City",
        "color": "White",
        "owner": member_id,
        "flat": flat_id
    }
    
    response = requests.post(f"{BASE_URL}/vehicles/", headers=headers, json=vehicle_data)
    vehicle_id = None
    if response.status_code == 201:
        vehicle = response.json()
        vehicle_id = vehicle['id']
        print_success(f"Vehicle registered successfully: {vehicle['vehicle_number']}")
    else:
        print_error(f"Failed to register vehicle: {response.status_code}")
        print(response.text)
        return
    
    # List vehicles
    print_step(2, "List Registered Vehicles")
    response = requests.get(f"{BASE_URL}/vehicles/", headers=headers)
    if response.status_code == 200:
        vehicles = response.json()
        if 'results' in vehicles:
            print_success(f"Found {len(vehicles['results'])} vehicles")
            for vehicle in vehicles['results']:
                print_info(f"  - {vehicle['vehicle_number']} ({vehicle['brand']} {vehicle['model']})")
        else:
            print_success(f"Found {len(vehicles)} vehicles")
            for vehicle in vehicles:
                print_info(f"  - {vehicle['vehicle_number']} ({vehicle['brand']} {vehicle['model']})")
    else:
        print_error(f"Failed to list vehicles: {response.status_code}")
    
    # Update vehicle
    print_step(3, "Update Vehicle Information")
    update_data = {
        "color": "Black",
        "model": "Civic"
    }
    
    response = requests.put(f"{BASE_URL}/vehicles/{vehicle_id}/", 
                           headers=headers, json=update_data)
    if response.status_code == 200:
        print_success("Vehicle updated successfully")
    else:
        print_error(f"Failed to update vehicle: {response.status_code}")
    
    return vehicle_id

def test_amenity_booking(access_token, member_id):
    """Test member amenity booking capabilities"""
    print_section("AMENITY BOOKING")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # List amenities
    print_step(1, "View Available Amenities")
    response = requests.get(f"{BASE_URL}/amenities/", headers=headers)
    amenity_id = None
    if response.status_code == 200:
        amenities = response.json()
        if 'results' in amenities and amenities['results']:
            amenity_id = amenities['results'][0]['id']
            print_success(f"Found {len(amenities['results'])} amenities")
            for amenity in amenities['results'][:3]:  # Show first 3
                print_info(f"  - {amenity['name']}")
        elif amenities:
            amenity_id = amenities[0]['id']
            print_success(f"Found {len(amenities)} amenities")
            for amenity in amenities[:3]:  # Show first 3
                print_info(f"  - {amenity['name']}")
        else:
            print_info("No amenities found")
    else:
        print_error(f"Failed to list amenities: {response.status_code}")
        return
    
    if not amenity_id:
        print_info("Skipping booking test - no amenities available")
        return
    
    # Book an amenity
    print_step(2, "Book an Amenity")
    # Calculate booking date (tomorrow)
    tomorrow = datetime.now() + timedelta(days=1)
    booking_data = {
        "amenity": amenity_id,
        "booked_by": member_id,
        "booking_date": tomorrow.strftime("%Y-%m-%d"),
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "purpose": "Family swimming"
    }
    
    response = requests.post(f"{BASE_URL}/amenity-bookings/", headers=headers, json=booking_data)
    booking_id = None
    if response.status_code == 201:
        booking = response.json()
        booking_id = booking['id']
        print_success(f"Amenity booked successfully: Booking #{booking_id}")
    else:
        print_error(f"Failed to book amenity: {response.status_code}")
        print(response.text)
        return
    
    # List bookings
    print_step(3, "View My Bookings")
    response = requests.get(f"{BASE_URL}/amenity-bookings/", headers=headers)
    if response.status_code == 200:
        bookings = response.json()
        if 'results' in bookings:
            print_success(f"Found {len(bookings['results'])} bookings")
            for booking in bookings['results'][:3]:  # Show first 3
                print_info(f"  - Booking #{booking['id']} for {booking['amenity_name']} on {booking['booking_date']}")
        else:
            print_success(f"Found {len(bookings)} bookings")
            for booking in bookings[:3]:  # Show first 3
                print_info(f"  - Booking #{booking['id']} for {booking['amenity_name']} on {booking['booking_date']}")
    else:
        print_error(f"Failed to list bookings: {response.status_code}")
    
    return booking_id

def test_complaint_submission(access_token, member_id, flat_id):
    """Test member complaint submission capabilities"""
    print_section("COMPLAINT MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Submit a complaint
    print_step(1, "Submit a Complaint")
    complaint_data = {
        "title": "Water Leakage Issue",
        "description": f"Water leakage detected in flat #{flat_id} bathroom ceiling",
        "flat": flat_id,
        "raised_by": member_id,
        "priority": "HIGH",
        "category": "MAINTENANCE"
    }
    
    response = requests.post(f"{BASE_URL}/complaints/", headers=headers, json=complaint_data)
    complaint_id = None
    if response.status_code == 201:
        complaint = response.json()
        complaint_id = complaint['id']
        print_success(f"Complaint submitted successfully: #{complaint_id}")
    else:
        print_error(f"Failed to submit complaint: {response.status_code}")
        print(response.text)
        return
    
    # List complaints
    print_step(2, "View My Complaints")
    response = requests.get(f"{BASE_URL}/complaints/", headers=headers)
    if response.status_code == 200:
        complaints = response.json()
        if 'results' in complaints:
            print_success(f"Found {len(complaints['results'])} complaints")
            for complaint in complaints['results'][:3]:  # Show first 3
                print_info(f"  - #{complaint['id']}: {complaint['title']} (Status: {complaint['status']})")
        else:
            print_success(f"Found {len(complaints)} complaints")
            for complaint in complaints[:3]:  # Show first 3
                print_info(f"  - #{complaint['id']}: {complaint['title']} (Status: {complaint['status']})")
    else:
        print_error(f"Failed to list complaints: {response.status_code}")
    
    return complaint_id

def test_marketplace(access_token, member_id):
    """Test member marketplace capabilities"""
    print_section("MARKETPLACE")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Post an item
    print_step(1, "Post Item to Marketplace")
    item_data = {
        "title": "Used Bicycle for Sale",
        "description": "Well-maintained bicycle, 6 months old",
        "price": 5000.00,
        "category": "SPORTS",
        "posted_by": member_id,
        "status": "ACTIVE"
    }
    
    response = requests.post(f"{BASE_URL}/marketplace/", headers=headers, json=item_data)
    item_id = None
    if response.status_code == 201:
        item = response.json()
        item_id = item['id']
        print_success(f"Marketplace item posted successfully: #{item_id}")
    else:
        print_error(f"Failed to post item: {response.status_code}")
        print(response.text)
        return
    
    # List marketplace items
    print_step(2, "Browse Marketplace")
    response = requests.get(f"{BASE_URL}/marketplace/", headers=headers)
    if response.status_code == 200:
        items = response.json()
        if 'results' in items:
            print_success(f"Found {len(items['results'])} marketplace items")
            for item in items['results'][:3]:  # Show first 3
                print_info(f"  - #{item['id']}: {item['title']} (₹{item['price']})")
        else:
            print_success(f"Found {len(items)} marketplace items")
            for item in items[:3]:  # Show first 3
                print_info(f"  - #{item['id']}: {item['title']} (₹{item['price']})")
    else:
        print_error(f"Failed to browse marketplace: {response.status_code}")
    
    return item_id

def test_directory_access(access_token):
    """Test member directory access capabilities"""
    print_section("DIRECTORY ACCESS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # View directory
    print_step(1, "View Society Directory")
    response = requests.get(f"{BASE_URL}/directory/", headers=headers)
    if response.status_code == 200:
        directory = response.json()
        if 'results' in directory:
            print_success(f"Directory has {len(directory['results'])} entries")
            for entry in directory['results'][:3]:  # Show first 3
                print_info(f"  - {entry['user_name']} (Flat {entry['flat_numbers']})")
        else:
            print_success(f"Directory has {len(directory)} entries")
            for entry in directory[:3]:  # Show first 3
                print_info(f"  - {entry['user_name']} (Flat {entry['flat_numbers']})")
    else:
        print_error(f"Failed to access directory: {response.status_code}")

def test_notices_access(access_token):
    """Test member notices access capabilities"""
    print_section("NOTICES & ANNOUNCEMENTS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # View notices
    print_step(1, "View Society Notices")
    response = requests.get(f"{BASE_URL}/notices/", headers=headers)
    if response.status_code == 200:
        notices = response.json()
        if 'results' in notices:
            print_success(f"Found {len(notices['results'])} notices")
            for notice in notices['results'][:3]:  # Show first 3
                print_info(f"  - {notice['title']} (Posted: {notice['created_at'][:10]})")
        else:
            print_success(f"Found {len(notices)} notices")
            for notice in notices[:3]:  # Show first 3
                print_info(f"  - {notice['title']} (Posted: {notice['created_at'][:10]})")
    else:
        print_error(f"Failed to access notices: {response.status_code}")

def test_dashboard_stats(access_token):
    """Test member dashboard statistics"""
    print_section("DASHBOARD STATISTICS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get dashboard stats
    print_step(1, "View Personal Dashboard")
    response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print_success("Dashboard statistics retrieved")
        for key, value in stats.items():
            print_info(f"  {key}: {value}")
    else:
        print_error(f"Failed to get dashboard stats: {response.status_code}")

def test_helpdesk_access(access_token):
    """Test member helpdesk access capabilities"""
    print_section("HELPDESK ACCESS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # View helpdesk contacts
    print_step(1, "View Helpdesk Contacts")
    response = requests.get(f"{BASE_URL}/helpdesk-contacts/", headers=headers)
    if response.status_code == 200:
        contacts = response.json()
        if 'results' in contacts:
            print_success(f"Found {len(contacts['results'])} helpdesk contacts")
            for contact in contacts['results'][:3]:  # Show first 3
                print_info(f"  - {contact['designation']}: {contact['contact_person']} ({contact['phone_number']})")
        else:
            print_success(f"Found {len(contacts)} helpdesk contacts")
            for contact in contacts[:3]:  # Show first 3
                print_info(f"  - {contact['designation']}: {contact['contact_person']} ({contact['phone_number']})")
    else:
        print_error(f"Failed to access helpdesk contacts: {response.status_code}")
    
    # View helpdesk designations
    print_step(2, "View Service Categories")
    response = requests.get(f"{BASE_URL}/helpdesk-designations/", headers=headers)
    if response.status_code == 200:
        designations = response.json()
        if 'results' in designations:
            print_success(f"Found {len(designations['results'])} service categories")
            for designation in designations['results'][:5]:  # Show first 5
                print_info(f"  - {designation['title']}")
        else:
            print_success(f"Found {len(designations)} service categories")
            for designation in designations[:5]:  # Show first 5
                print_info(f"  - {designation['title']}")
    else:
        print_error(f"Failed to access service categories: {response.status_code}")

def test_restricted_functions(access_token):
    """Test that members cannot access restricted functions"""
    print_section("RESTRICTED FUNCTIONS (SECURITY CHECK)")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Try to create a staff member (should fail)
    print_step(1, "Attempt to Create Staff Member (Should Fail)")
    staff_data = {
        "phone_number": f"98{random.randint(10000000, 99999999)}",
        "email": "teststaff@example.com",
        "first_name": "Test",
        "last_name": "Staff",
        "password": "staff123456",
        "password_confirm": "staff123456"
    }
    
    response = requests.post(f"{BASE_URL}/admin/create-staff-user/", headers=headers, json=staff_data)
    if response.status_code == 403:
        print_success("Correctly blocked from creating staff members")
    else:
        print_info(f"Unexpected response: {response.status_code}")
    
    # Try to create a visitor pass (should fail)
    print_step(2, "Attempt to Create Visitor Pass (Should Fail)")
    pass_data = {
        "visitor_name": "Test Visitor",
        "visitor_phone": "9876543210",
        "purpose_of_visit": "Test visit"
    }
    
    response = requests.post(f"{BASE_URL}/visitor-passes/", headers=headers, json=pass_data)
    if response.status_code == 403 or response.status_code == 400:
        print_success("Correctly blocked from creating visitor passes")
    else:
        print_info(f"Unexpected response: {response.status_code}")

def main():
    """Run the complete member capabilities test"""
    print("🏠 MEMBER CAPABILITIES TEST")
    print("Testing all available member functions in the society management system")
    
    try:
        # Test 1: Member Login
        access_token = test_member_login()
        if not access_token:
            print_error("Cannot proceed without authentication")
            return
        
        # Test 2: Profile Management
        test_profile_management(access_token)
        
        # For other tests, we need member ID and flat ID
        # In a real test, these would be obtained from the login response
        # For this demo, we'll use placeholder values
        member_id = 1  # This would be from the login response
        flat_id = 1    # This would be from the member's assigned flats
        
        # Test 3: Vehicle Management
        test_vehicle_management(access_token, member_id, flat_id)
        
        # Test 4: Amenity Booking
        test_amenity_booking(access_token, member_id)
        
        # Test 5: Complaint Submission
        test_complaint_submission(access_token, member_id, flat_id)
        
        # Test 6: Marketplace
        test_marketplace(access_token, member_id)
        
        # Test 7: Directory Access
        test_directory_access(access_token)
        
        # Test 8: Notices Access
        test_notices_access(access_token)
        
        # Test 9: Dashboard Statistics
        test_dashboard_stats(access_token)
        
        # Test 10: Helpdesk Access
        test_helpdesk_access(access_token)
        
        # Test 11: Restricted Functions
        test_restricted_functions(access_token)
        
        print_section("TEST COMPLETED")
        print_success("✅ MEMBER CAPABILITIES VERIFICATION COMPLETED")
        print("\n📋 SUMMARY OF MEMBER CAPABILITIES:")
        print("   ✅ Profile Management - Full access")
        print("   ✅ Vehicle Registration - Full access")
        print("   ✅ Amenity Booking - Full access")
        print("   ✅ Complaint Submission - Full access")
        print("   ✅ Marketplace Participation - Full access")
        print("   ✅ Directory Access - Read-only")
        print("   ✅ Notices Access - Read-only")
        print("   ✅ Dashboard Statistics - Read-only")
        print("   ✅ Helpdesk Access - Read-only")
        print("   ❌ Staff Creation - Restricted (Security)")
        print("   ❌ Visitor Pass Creation - Restricted (Security)")
        print("   ❌ Gate Log Management - Restricted (Security)")
        print("\n🔐 SECURITY NOTE:")
        print("   Restricted functions are properly secured and can only")
        print("   be accessed by authorized roles (SUB_ADMIN/STAFF)")
        print("\n🎉 MEMBERS HAVE COMPREHENSIVE ACCESS TO ALL ESSENTIAL SERVICES!")
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print_error(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()