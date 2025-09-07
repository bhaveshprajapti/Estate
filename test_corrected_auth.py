#!/usr/bin/env python3
"""
Test Script for Corrected Authentication Flow
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def test_corrected_authentication():
    """Test the corrected authentication system"""
    print("🚀 TESTING CORRECTED AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Test 1: ADMIN Registration
    print("\n🔸 Step 1: Register ADMIN")
    admin_data = {
        "phone_number": f"90{random.randint(10000000, 99999999)}",
        "email": "admin@test.com",
        "first_name": "Super",
        "last_name": "Admin",
        "password": "admin123456",
        "password_confirm": "admin123456",
        "role": "ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    print(f"Registration Status: {response.status_code}")
    
    if response.status_code == 201:
        admin_phone = admin_data["phone_number"]
        print(f"✅ ADMIN registered: {admin_phone}")
        
        # Test 2: Login with Password
        print("\n🔸 Step 2: Login with Password")
        login_data = {
            "phone_number": admin_phone,
            "password": "admin123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
        print(f"Password Login Status: {response.status_code}")
        
        if response.status_code == 200:
            admin_tokens = response.json()["tokens"]
            print("✅ Password login successful!")
            
            # Test 3: Login with OTP
            print("\n🔸 Step 3: Login with OTP")
            
            # Step 3a: Send OTP
            response = requests.post(f"{BASE_URL}/auth/login-otp-step1/", 
                                   json={"phone_number": admin_phone})
            print(f"Send OTP Status: {response.status_code}")
            
            if response.status_code == 200:
                otp_code = response.json()["otp_code"]
                print(f"✅ OTP sent: {otp_code}")
                
                # Step 3b: Verify OTP
                verify_data = {
                    "phone_number": admin_phone,
                    "otp_code": otp_code
                }
                response = requests.post(f"{BASE_URL}/auth/login-otp-step2/", 
                                       json=verify_data)
                print(f"OTP Login Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ OTP login successful!")
                    
                    # Test 4: Create Society
                    print("\n🔸 Step 4: Create Society")
                    headers = {"Authorization": f"Bearer {admin_tokens['access']}"}
                    society_data = {
                        "name": "Test Society",
                        "address": "123 Test Street",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001",
                        "registration_number": "TEST123"
                    }
                    
                    response = requests.post(f"{BASE_URL}/societies/", 
                                           json=society_data, headers=headers)
                    print(f"Society Creation Status: {response.status_code}")
                    
                    if response.status_code == 201:
                        society_id = response.json()["id"]
                        print(f"✅ Society created: ID {society_id}")
                        
                        # Test 5: SUB_ADMIN Invitation
                        print("\n🔸 Step 5: Create SUB_ADMIN Invitation")
                        invitation_data = {
                            "society": society_id,
                            "phone_number": f"91{random.randint(10000000, 99999999)}",
                            "email": "subadmin@test.com"
                        }
                        
                        response = requests.post(f"{BASE_URL}/admin/create-subadmin-invitation/", 
                                               json=invitation_data, headers=headers)
                        print(f"Invitation Status: {response.status_code}")
                        
                        if response.status_code == 201:
                            invitation_data_response = response.json()
                            invitation_otp = invitation_data_response["otp_info"]["otp_code"]
                            invitation_id = invitation_data_response["invitation"]["id"]
                            subadmin_phone = invitation_data["phone_number"]
                            
                            print(f"✅ Invitation created with OTP: {invitation_otp}")
                            
                            # Test 6: Complete SUB_ADMIN Registration
                            print("\n🔸 Step 6: Complete SUB_ADMIN Registration")
                            
                            # Verify OTP first
                            verify_data = {
                                "phone_number": subadmin_phone,
                                "otp_code": invitation_otp
                            }
                            response = requests.post(f"{BASE_URL}/invitation/verify-otp/", 
                                                   json=verify_data)
                            print(f"OTP Verification Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                print("✅ Invitation OTP verified!")
                                
                                # Complete registration
                                registration_data = {
                                    "invitation_id": invitation_id,
                                    "first_name": "Society",
                                    "last_name": "Chairman",
                                    "password": "chairman123456",
                                    "password_confirm": "chairman123456"
                                }
                                
                                response = requests.post(f"{BASE_URL}/invitation/complete-registration/", 
                                                       json=registration_data)
                                print(f"SUB_ADMIN Registration Status: {response.status_code}")
                                
                                if response.status_code == 201:
                                    print("✅ SUB_ADMIN registration completed!")
                                    
                                    # Test 7: SUB_ADMIN Login
                                    print("\n🔸 Step 7: Test SUB_ADMIN Login")
                                    subadmin_login_data = {
                                        "phone_number": subadmin_phone,
                                        "password": "chairman123456"
                                    }
                                    
                                    response = requests.post(f"{BASE_URL}/auth/login-password/", 
                                                           json=subadmin_login_data)
                                    print(f"SUB_ADMIN Login Status: {response.status_code}")
                                    
                                    if response.status_code == 200:
                                        print("✅ SUB_ADMIN login successful!")
                                        
                                        print("\n🎉 ALL TESTS PASSED!")
                                        print("✅ Dual Authentication Methods Working")
                                        print("✅ SUB_ADMIN Invitation Flow Working")
                                        print("✅ Role-based Authentication Working")
                                        return True

    return False

def main():
    try:
        success = test_corrected_authentication()
        if success:
            print("\n" + "=" * 60)
            print("🌟 CORRECTED AUTHENTICATION SYSTEM IS WORKING!")
            print("=" * 60)
            print("\n📋 VERIFIED ENDPOINTS:")
            print(f"   - POST {BASE_URL}/auth/register/")
            print(f"   - POST {BASE_URL}/auth/login-password/")
            print(f"   - POST {BASE_URL}/auth/login-otp-step1/")
            print(f"   - POST {BASE_URL}/auth/login-otp-step2/")
            print(f"   - POST {BASE_URL}/admin/create-subadmin-invitation/")
            print(f"   - POST {BASE_URL}/invitation/verify-otp/")
            print(f"   - POST {BASE_URL}/invitation/complete-registration/")
        else:
            print("\n❌ Some tests failed. Check the server logs.")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()