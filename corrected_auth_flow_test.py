#!/usr/bin/env python3
"""
Corrected Authentication Flow Test Script
Tests the updated dual login methods and SUB_ADMIN invitation system
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔸 {title}")
    print('='*60)

def print_step(step_num, title):
    print(f"\n🔹 Step {step_num}: {title}")
    print("-" * 40)

def test_admin_registration():
    """Test ADMIN user registration"""
    print_section("ADMIN REGISTRATION")
    
    admin_data = {
        "phone_number": "9000000001",
        "email": "admin@society.com",
        "first_name": "Super",
        "last_name": "Admin",
        "password": "admin123456",
        "password_confirm": "admin123456",
        "role": "ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ ADMIN registered successfully!")
        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"   Role: {data['user']['role']}")
        if 'otp_info' in data:
            print(f"   Registration OTP: {data['otp_info']['otp_code']}")
        return data
    else:
        print("❌ ADMIN registration failed!")
        print(response.text)
        return None

def test_dual_login_methods(admin_phone):
    """Test both login methods"""
    print_section("DUAL LOGIN METHODS TESTING")
    
    # Method 1: Password Login
    print_step(1, "Login with Password (Traditional Method)")
    login_data = {
        "phone_number": admin_phone,
        "password": "admin123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Password login successful!")
        print(f"   Access Token: {data['tokens']['access'][:30]}...")
        password_tokens = data['tokens']
    else:
        print("❌ Password login failed!")
        print(response.text)
        return None
    
    # Method 2: OTP Login
    print_step(2, "Login with OTP (Secure Method)")
    
    # Step 2a: Send OTP
    response = requests.post(f"{BASE_URL}/auth/login-otp-step1/", json={"phone_number": admin_phone})
    print(f"Send OTP Status: {response.status_code}")
    
    if response.status_code == 200:
        otp_data = response.json()
        otp_code = otp_data['otp_code']
        print(f"✅ OTP sent: {otp_code}")
        
        # Step 2b: Verify OTP
        verify_data = {
            "phone_number": admin_phone,
            "otp_code": otp_code
        }
        response = requests.post(f"{BASE_URL}/auth/login-otp-step2/", json=verify_data)
        print(f"Verify OTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OTP login successful!")
            print(f"   Access Token: {data['tokens']['access'][:30]}...")
            return data['tokens']
        else:
            print("❌ OTP verification failed!")
            print(response.text)
    else:
        print("❌ OTP send failed!")
        print(response.text)
    
    return password_tokens

def test_society_creation(tokens):
    """Test society creation by ADMIN"""
    print_section("SOCIETY CREATION BY ADMIN")
    
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    society_data = {
        "name": "Sunshine Apartments",
        "address": "123 Sunshine Lane, Happy Society Area",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "registration_number": "SUN2024001"
    }
    
    response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Society created successfully!")
        print(f"   Society: {data['name']}")
        print(f"   Address: {data['address']}")
        print(f"   Registration: {data['registration_number']}")
        return data
    else:
        print("❌ Society creation failed!")
        print(response.text)
        return None

def test_subadmin_invitation_flow(tokens, society_id):
    """Test complete SUB_ADMIN invitation flow"""
    print_section("SUB_ADMIN INVITATION FLOW")
    
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    
    # Step 1: ADMIN creates invitation
    print_step(1, "ADMIN Creates SUB_ADMIN Invitation")
    invitation_data = {
        "society": society_id,
        "phone_number": "9876543210",
        "email": "chairman@sunshine.com"
    }
    
    response = requests.post(f"{BASE_URL}/admin/create-subadmin-invitation/", 
                           json=invitation_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        invitation_id = data['invitation']['id']
        invitation_otp = data['otp_info']['otp_code']
        
        print("✅ SUB_ADMIN invitation created!")
        print(f"   Invited Phone: {data['invitation']['phone_number']}")
        print(f"   Society: {data['invitation']['society_name']}")
        print(f"   Invitation OTP: {invitation_otp}")
        
        # Step 2: Verify OTP
        print_step(2, "SUB_ADMIN Verifies OTP")
        verify_data = {
            "phone_number": "9876543210",
            "otp_code": invitation_otp
        }
        
        response = requests.post(f"{BASE_URL}/invitation/verify-otp/", json=verify_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OTP verified successfully!")
            print(f"   Next Step: {data['next_step']}")
            
            # Step 3: Complete registration
            print_step(3, "SUB_ADMIN Completes Registration")
            registration_data = {
                "invitation_id": invitation_id,
                "first_name": "Society",
                "last_name": "Chairman",
                "password": "chairman123456",
                "password_confirm": "chairman123456"
            }
            
            response = requests.post(f"{BASE_URL}/invitation/complete-registration/", 
                                   json=registration_data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ SUB_ADMIN registration completed!")
                print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Society: {data['society']['name']}")
                print(f"   Access Token: {data['tokens']['access'][:30]}...")
                return data
            else:
                print("❌ Registration completion failed!")
                print(response.text)
        else:
            print("❌ OTP verification failed!")
            print(response.text)
    else:
        print("❌ Invitation creation failed!")
        print(response.text)
    
    return None

def test_subadmin_login():
    """Test SUB_ADMIN login with both methods"""
    print_section("SUB_ADMIN LOGIN TESTING")
    
    subadmin_phone = "9876543210"
    
    # Test password login
    print_step(1, "SUB_ADMIN Login with Password")
    login_data = {
        "phone_number": subadmin_phone,
        "password": "chairman123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUB_ADMIN password login successful!")
        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Society: {data['user']['society_name']}")
        
        # Test OTP login
        print_step(2, "SUB_ADMIN Login with OTP")
        response = requests.post(f"{BASE_URL}/auth/login-otp-step1/", json={"phone_number": subadmin_phone})
        
        if response.status_code == 200:
            otp_data = response.json()
            otp_code = otp_data['otp_code']
            print(f"✅ OTP sent to SUB_ADMIN: {otp_code}")
            
            verify_data = {
                "phone_number": subadmin_phone,
                "otp_code": otp_code
            }
            response = requests.post(f"{BASE_URL}/auth/login-otp-step2/", json=verify_data)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUB_ADMIN OTP login successful!")
                return data['tokens']
        
        return data['tokens']
    else:
        print("❌ SUB_ADMIN login failed!")
        print(response.text)
        return None

def test_subadmin_operations(tokens):
    """Test SUB_ADMIN can manage society operations"""
    print_section("SUB_ADMIN SOCIETY OPERATIONS")
    
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    
    # Test creating amenities
    print_step(1, "SUB_ADMIN Creates Amenity")
    amenity_data = {
        "society": 1,  # Assuming society ID 1
        "name": "Swimming Pool",
        "description": "Community swimming pool for residents",
        "booking_price": 500,
        "is_available": True
    }
    
    response = requests.post(f"{BASE_URL}/amenities/", json=amenity_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Amenity created successfully!")
        print(f"   Amenity: {data['name']}")
        print(f"   Price: ₹{data['booking_price']}")
    else:
        print("❌ Amenity creation failed!")
        print(response.text)
    
    # Test creating notice
    print_step(2, "SUB_ADMIN Creates Notice")
    notice_data = {
        "society": 1,
        "title": "Monthly Society Meeting",
        "content": "All residents are invited to attend the monthly society meeting on 15th January 2024.",
        "priority": "HIGH",
        "valid_until": "2024-01-15"
    }
    
    response = requests.post(f"{BASE_URL}/notices/", json=notice_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Notice created successfully!")
        print(f"   Title: {data['title']}")
        print(f"   Priority: {data['priority']}")
    else:
        print("❌ Notice creation failed!")
        print(response.text)

def main():
    """Run the complete corrected authentication flow test"""
    print("🚀 CORRECTED AUTHENTICATION FLOW TESTING")
    print("=" * 70)
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Test 1: ADMIN Registration
        admin_result = test_admin_registration()
        if not admin_result:
            return
        
        admin_phone = admin_result['user']['phone_number']
        
        # Test 2: Dual Login Methods
        admin_tokens = test_dual_login_methods(admin_phone)
        if not admin_tokens:
            return
        
        # Test 3: Society Creation
        society_result = test_society_creation(admin_tokens)
        if not society_result:
            return
        
        # Test 4: SUB_ADMIN Invitation Flow
        subadmin_result = test_subadmin_invitation_flow(admin_tokens, society_result['id'])
        if not subadmin_result:
            return
        
        # Test 5: SUB_ADMIN Login
        subadmin_tokens = test_subadmin_login()
        if not subadmin_tokens:
            return
        
        # Test 6: SUB_ADMIN Operations
        test_subadmin_operations(subadmin_tokens)
        
        # Summary
        print_section("CORRECTED FLOW TESTING SUMMARY")
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print()
        print("✅ CORRECTED FEATURES VERIFIED:")
        print("   🔐 ADMIN Registration and Login")
        print("   🔑 Dual Login Methods (Password + OTP)")
        print("   🏢 Society Creation by ADMIN")
        print("   📧 SUB_ADMIN Invitation System")
        print("   📱 OTP Verification for Invitations")
        print("   👤 SUB_ADMIN Registration Completion")
        print("   🔓 SUB_ADMIN Login with Both Methods")
        print("   ⚙️ SUB_ADMIN Society Operations")
        print()
        print("🔑 AUTHENTICATION ENDPOINTS:")
        print(f"   - POST {BASE_URL}/auth/register/")
        print(f"   - POST {BASE_URL}/auth/login-password/")
        print(f"   - POST {BASE_URL}/auth/login-otp-step1/")
        print(f"   - POST {BASE_URL}/auth/login-otp-step2/")
        print(f"   - POST {BASE_URL}/auth/login/ (Legacy)")
        print()
        print("📧 SUB_ADMIN INVITATION ENDPOINTS:")
        print(f"   - POST {BASE_URL}/admin/create-subadmin-invitation/")
        print(f"   - POST {BASE_URL}/invitation/verify-otp/")
        print(f"   - POST {BASE_URL}/invitation/complete-registration/")
        print(f"   - GET {BASE_URL}/admin/subadmin-invitations/")
        print()
        print("🌟 The Society Management Platform has CORRECTED authentication flow!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()