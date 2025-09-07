#!/usr/bin/env python3
"""
Simple OTP Authentication Test
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration with OTP"""
    print("🔐 Testing User Registration with OTP")
    print("-" * 40)
    
    user_data = {
        "phone_number": "8888888888",
        "email": "newotp@test.com", 
        "first_name": "OTP",
        "last_name": "User",
        "password": "test123456",
        "password_confirm": "test123456",
        "role": "MEMBER"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Registration successful!")
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"Role: {data['user']['role']}")
        if 'otp_info' in data:
            print(f"OTP: {data['otp_info']['otp_code']}")
            print(f"Purpose: {data['otp_info']['purpose']}")
    else:
        print("❌ Registration failed!")
        print(response.text)

def test_login():
    """Test user login with OTP"""
    print("\n🔑 Testing User Login with OTP")
    print("-" * 40)
    
    login_data = {
        "phone_number": "9999999999",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"Role: {data['user']['role']}")
        if 'otp_info' in data:
            print(f"OTP: {data['otp_info']['otp_code']}")
            print(f"Purpose: {data['otp_info']['purpose']}")
        return data
    else:
        print("❌ Login failed!")
        print(response.text)
        return None

def test_forgot_password():
    """Test forgot password flow"""
    print("\n🔓 Testing Forgot Password Flow")
    print("-" * 40)
    
    # Step 1: Request forgot password OTP
    forgot_data = {"phone_number": "9999999999"}
    response = requests.post(f"{BASE_URL}/auth/forgot-password/", json=forgot_data)
    print(f"Forgot Password Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        otp_code = data['otp_code']
        print(f"✅ OTP sent: {otp_code}")
        
        # Step 2: Reset password using OTP
        reset_data = {
            "phone_number": "9999999999",
            "otp_code": otp_code,
            "new_password": "newtestpass123",
            "confirm_password": "newtestpass123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/reset-password/", json=reset_data)
        print(f"Password Reset Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Password reset successful!")
            print(f"New tokens generated")
            
            # Step 3: Test login with new password
            login_data = {
                "phone_number": "9999999999",
                "password": "newtestpass123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
            print(f"Login with new password: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Login with new password successful!")
            else:
                print("❌ Login with new password failed!")
        else:
            print("❌ Password reset failed!")
            print(response.text)
    else:
        print("❌ Forgot password request failed!")
        print(response.text)

def main():
    print("🚀 Simple OTP Authentication Test")
    print("=" * 50)
    
    test_registration()
    test_login()
    test_forgot_password()
    
    print("\n" + "=" * 50)
    print("✅ OTP Authentication test completed!")

if __name__ == "__main__":
    main()