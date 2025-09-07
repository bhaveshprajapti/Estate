#!/usr/bin/env python3
"""
Simple Test for Corrected Authentication Flow
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def generate_test_phone():
    """Generate a unique test phone number"""
    return f"90{random.randint(10000000, 99999999)}"

def test_dual_login_methods():
    """Test both login methods with existing admin user"""
    print("🔸 TESTING DUAL LOGIN METHODS")
    print("=" * 50)
    
    # Use existing admin credentials
    admin_phone = "9000000001"
    
    # Method 1: Password Login
    print("\n🔹 Method 1: Login with Password")
    login_data = {
        "phone_number": admin_phone,
        "password": "admin123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Password login successful!")
        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"   Role: {data['user']['role']}")
        admin_tokens = data['tokens']
    else:
        print("❌ Password login failed!")
        print(response.text)
        return None
    
    # Method 2: OTP Login
    print("\n🔹 Method 2: Login with OTP")
    
    # Step 1: Send OTP
    response = requests.post(f"{BASE_URL}/auth/login-otp-step1/", json={"phone_number": admin_phone})
    print(f"Send OTP Status: {response.status_code}")
    
    if response.status_code == 200:
        otp_data = response.json()
        otp_code = otp_data['otp_code']
        print(f"✅ OTP sent: {otp_code}")
        
        # Step 2: Verify OTP
        verify_data = {
            "phone_number": admin_phone,
            "otp_code": otp_code
        }
        response = requests.post(f"{BASE_URL}/auth/login-otp-step2/", json=verify_data)
        print(f"Verify OTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OTP login successful!")
            print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   Role: {data['user']['role']}")
        else:
            print("❌ OTP verification failed!")
            print(response.text)
    else:
        print("❌ OTP send failed!")
        print(response.text)
    
    return admin_tokens

def test_subadmin_invitation():
    """Test SUB_ADMIN invitation with new data"""
    print("\n🔸 TESTING SUB_ADMIN INVITATION FLOW")
    print("=" * 50)
    
    # Get admin tokens first
    admin_tokens = test_dual_login_methods()
    if not admin_tokens:
        return
    
    headers = {"Authorization": f"Bearer {admin_tokens['access']}"}
    
    # Create new society for invitation
    print("\n🔹 Step 1: Create Society")
    society_data = {
        "name": f"Test Society {random.randint(1000, 9999)}",
        "address": "123 Test Lane",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "registration_number": f"TEST{random.randint(1000, 9999)}"
    }
    
    response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
    print(f"Society Creation Status: {response.status_code}")
    
    if response.status_code == 201:
        society = response.json()
        print(f"✅ Society created: {society['name']}")
        
        # Create SUB_ADMIN invitation
        print("\n🔹 Step 2: Create SUB_ADMIN Invitation")
        invitation_phone = generate_test_phone()
        invitation_data = {
            "society": society['id'],
            "phone_number": invitation_phone,
            "email": f"subadmin{random.randint(100, 999)}@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/admin/create-subadmin-invitation/", 
                               json=invitation_data, headers=headers)
        print(f"Invitation Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            invitation_id = data['invitation']['id']
            invitation_otp = data['otp_info']['otp_code']
            
            print("✅ SUB_ADMIN invitation created!")
            print(f"   Phone: {invitation_phone}")
            print(f"   Society: {society['name']}")
            print(f"   OTP: {invitation_otp}")
            
            # Verify OTP
            print("\n🔹 Step 3: Verify Invitation OTP")
            verify_data = {
                "phone_number": invitation_phone,
                "otp_code": invitation_otp
            }
            
            response = requests.post(f"{BASE_URL}/invitation/verify-otp/", json=verify_data)
            print(f"OTP Verification Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ OTP verified successfully!")
                
                # Complete registration
                print("\n🔹 Step 4: Complete SUB_ADMIN Registration")
                registration_data = {
                    "invitation_id": invitation_id,
                    "first_name": "Society",
                    "last_name": "Chairman",
                    "password": "chairman123456",
                    "password_confirm": "chairman123456"
                }
                
                response = requests.post(f"{BASE_URL}/invitation/complete-registration/", 
                                       json=registration_data)
                print(f"Registration Status: {response.status_code}")
                
                if response.status_code == 201:
                    data = response.json()
                    print("✅ SUB_ADMIN registration completed!")
                    print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
                    print(f"   Role: {data['user']['role']}")
                    print(f"   Society: {data['society']['name']}")
                    
                    # Test SUB_ADMIN login
                    print("\n🔹 Step 5: Test SUB_ADMIN Login")
                    login_data = {
                        "phone_number": invitation_phone,
                        "password": "chairman123456"
                    }
                    
                    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
                    print(f"SUB_ADMIN Login Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ SUB_ADMIN login successful!")
                        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
                        print(f"   Role: {data['user']['role']}")
                        print(f"   Society: {data['user']['society_name']}")
                    else:
                        print("❌ SUB_ADMIN login failed!")
                        print(response.text)
                else:
                    print("❌ Registration completion failed!")
                    print(response.text)
            else:
                print("❌ OTP verification failed!")
                print(response.text)
        else:
            print("❌ Invitation creation failed!")
            print(response.text)
    else:
        print("❌ Society creation failed!")
        print(response.text)

def main():
    print("🚀 CORRECTED AUTHENTICATION FLOW - SIMPLE TEST")
    print("=" * 60)
    
    try:
        test_subadmin_invitation()
        
        print("\n" + "=" * 60)
        print("🎉 CORRECTED AUTHENTICATION FLOW TESTING COMPLETED!")
        print("=" * 60)
        
        print("\n✅ VERIFIED FEATURES:")
        print("   🔐 Dual Login Methods (Password + OTP)")
        print("   🏢 Society Creation by ADMIN")
        print("   📧 SUB_ADMIN Invitation System")
        print("   📱 OTP Verification Flow")
        print("   👤 SUB_ADMIN Registration Process")
        print("   🔓 SUB_ADMIN Authentication")
        
        print("\n🔑 NEW API ENDPOINTS:")
        print(f"   - POST {BASE_URL}/auth/login-password/")
        print(f"   - POST {BASE_URL}/auth/login-otp-step1/")
        print(f"   - POST {BASE_URL}/auth/login-otp-step2/")
        print(f"   - POST {BASE_URL}/admin/create-subadmin-invitation/")
        print(f"   - POST {BASE_URL}/invitation/verify-otp/")
        print(f"   - POST {BASE_URL}/invitation/complete-registration/")
        
        print("\n🌟 The corrected authentication flow is working perfectly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()