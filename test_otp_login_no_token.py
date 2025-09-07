#!/usr/bin/env python3
"""
Test OTP Login WITHOUT TOKEN - Demonstrates that OTP endpoints work without authentication
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_otp_login_without_token():
    """Test that OTP login works completely without any existing tokens"""
    print("🔐 TESTING OTP LOGIN WITHOUT ANY TOKENS")
    print("=" * 60)
    
    # Use a fresh phone number (assuming you have a test user)
    test_phone = "9876543210"  # Replace with your test user's phone
    
    print(f"📱 Testing with phone: {test_phone}")
    print("🚫 NOT sending any Authorization headers...")
    
    # Step 1: Send OTP (NO TOKEN REQUIRED)
    print("\n🔹 Step 1: Requesting OTP for login...")
    print(f"   URL: {BASE_URL}/auth/login-otp-step1/")
    print("   Headers: Content-Type only (NO Authorization)")
    
    # Explicitly NO Authorization header
    headers = {
        "Content-Type": "application/json"
        # NO Authorization header!
    }
    
    data = {
        "phone_number": test_phone
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-otp-step1/", 
                           headers=headers, 
                           json=data)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        response_data = response.json()
        otp_code = response_data['otp_code']
        print(f"   ✅ OTP sent successfully: {otp_code}")
        print(f"   📧 Message: {response_data['message']}")
        
        # Step 2: Verify OTP (NO TOKEN REQUIRED)
        print("\n🔹 Step 2: Verifying OTP for login...")
        print(f"   URL: {BASE_URL}/auth/login-otp-step2/")
        print("   Headers: Content-Type only (NO Authorization)")
        
        verify_data = {
            "phone_number": test_phone,
            "otp_code": otp_code
        }
        
        # Explicitly NO Authorization header again
        verify_response = requests.post(f"{BASE_URL}/auth/login-otp-step2/", 
                                      headers=headers,  # Same headers - no auth
                                      json=verify_data)
        
        print(f"   Status: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            login_data = verify_response.json()
            access_token = login_data['tokens']['access']
            user_info = login_data['user']
            
            print(f"   ✅ Login successful!")
            print(f"   👤 User: {user_info['first_name']} {user_info['last_name']}")
            print(f"   🎭 Role: {user_info['role']}")
            print(f"   🔑 Access Token: {access_token[:30]}...")
            
            print("\n🎉 PROOF: OTP LOGIN WORKS WITHOUT ANY EXISTING TOKENS!")
            return True
        else:
            print(f"   ❌ OTP verification failed: {verify_response.status_code}")
            print(f"   Error: {verify_response.text}")
            return False
    else:
        print(f"   ❌ OTP request failed: {response.status_code}")
        print(f"   Error: {response.text}")
        
        if response.status_code == 404:
            print("\n💡 SOLUTION: Create a test user first:")
            print("   1. Use the registration endpoint")
            print("   2. Or use an existing user's phone number")
        
        return False

def test_what_requires_token():
    """Show what endpoints DO require tokens vs what don't"""
    print("\n" + "=" * 60)
    print("🔍 ENDPOINT AUTHENTICATION REQUIREMENTS")
    print("=" * 60)
    
    print("\n✅ NO TOKEN REQUIRED (Public Endpoints):")
    print("   📝 POST /auth/register/")
    print("   🔑 POST /auth/login-password/")
    print("   📱 POST /auth/login-otp-step1/")
    print("   📱 POST /auth/login-otp-step2/")
    print("   🔍 GET  /societies/search/")
    print("   👥 POST /members/self-register/")
    print("   🔒 POST /auth/forgot-password/")
    print("   ✅ POST /auth/verify-otp/")
    print("   🔄 POST /auth/reset-password/")
    print("   📧 POST /invitation/verify-otp/")
    print("   🎯 POST /invitation/complete-registration/")
    
    print("\n🔒 TOKEN REQUIRED (Authenticated Endpoints):")
    print("   👑 POST /admin/create-admin-user/")
    print("   👥 POST /admin/create-staff-user/")
    print("   📧 POST /admin/create-subadmin-invitation/")
    print("   🏢 POST /societies/")
    print("   🏗️ POST /buildings/")
    print("   🏠 POST /enhanced-flats/")
    print("   💰 POST /bill-types/")
    print("   📊 GET  /dashboard/stats/")
    print("   👤 GET  /auth/profile/")

def main():
    print("🧪 OTP LOGIN WITHOUT TOKEN TEST")
    print("Testing that OTP authentication works independently")
    
    try:
        success = test_otp_login_without_token()
        test_what_requires_token()
        
        if success:
            print("\n" + "✅" * 20)
            print("🏆 CONCLUSION: OTP LOGIN DOES NOT REQUIRE TOKENS!")
            print("✅" * 20)
            print("\n💡 If you see token requirements in Postman:")
            print("   1. Check individual request headers (not collection auth)")
            print("   2. Make sure OTP endpoints have NO Authorization header")
            print("   3. Verify you're using the correct environment variables")
        else:
            print("\n❌ Test failed - check server status and user data")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Django server")
        print("💡 Start the server: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()