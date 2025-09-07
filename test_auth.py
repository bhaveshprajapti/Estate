#!/usr/bin/env python3
"""
Test Django authentication manually
"""

import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'society_platform.settings')
django.setup()

from django.contrib.auth import authenticate
from society_management.models import User

print("=== Testing Django Authentication ===")

# Check existing users
users = User.objects.all()
print(f"Total users in system: {users.count()}")

for user in users:
    print(f"User: {user.phone_number} | {user.email} | {user.role} | Active: {user.is_active}")

# Test authentication
print("\n=== Testing Authentication ===")

# Try to authenticate with the existing user
phone_number = "9999999999"
passwords_to_try = ["test123", "test123456", "admin123", "admin", "password"]

for password in passwords_to_try:
    print(f"Trying password: {password}")
    user = authenticate(username=phone_number, password=password)
    if user:
        print(f"✅ Authentication successful with password: {password}")
        print(f"User: {user.get_full_name()} ({user.role})")
        break
    else:
        print(f"❌ Authentication failed")

# Let's reset the password for testing
print("\n=== Resetting Password ===")
try:
    user = User.objects.get(phone_number="9999999999")
    user.set_password("test123456")
    user.save()
    print("✅ Password reset to 'test123456'")
    
    # Test authentication again
    auth_user = authenticate(username="9999999999", password="test123456")
    if auth_user:
        print("✅ Authentication works after password reset")
    else:
        print("❌ Authentication still fails")
        
except User.DoesNotExist:
    print("❌ User not found")

print("\n=== Creating New Test User ===")
try:
    # Create a fresh test user
    test_user = User.objects.create_user(
        username="8888888888",
        phone_number="8888888888",
        email="test@example.com",
        password="test123456",
        first_name="Test",
        last_name="User",
        role="ADMIN"
    )
    print(f"✅ Created new user: {test_user.phone_number}")
    
    # Test authentication with new user
    auth_test = authenticate(username="8888888888", password="test123456")
    if auth_test:
        print("✅ New user authentication works")
    else:
        print("❌ New user authentication fails")
        
except Exception as e:
    print(f"❌ Error creating user: {e}")

print("\n=== Testing API Login ===")

import requests

BASE_URL = "http://localhost:8000/api"

# Test with reset password
login_data = {
    "phone_number": "9999999999",
    "password": "test123456"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"API Login Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API Login successful")
        data = response.json()
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
    else:
        print(f"❌ API Login failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")