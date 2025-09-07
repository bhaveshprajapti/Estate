import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test API root
try:
    response = requests.get(BASE_URL + "/")
    print(f"API Root Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API is accessible")
    else:
        print("❌ API access failed")
        print(response.text[:500])
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test authentication endpoints
try:
    # Check if there are any existing users
    print("\n=== Testing User Creation ===")
    
    # Try to register a test user
    user_data = {
        "phone_number": "9999999999",
        "email": "test@test.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "test123456",
        "password_confirm": "test123456",
        "role": "ADMIN"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    print(f"Registration Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
    if response.status_code in [200, 201]:
        print("✅ Registration successful")
        
        # Try login
        login_data = {
            "phone_number": "9999999999", 
            "password": "test123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login successful")
            data = response.json()
            print(f"Tokens received: {list(data.get('tokens', {}).keys())}")
        else:
            print("❌ Login failed")
            print(response.text)
    else:
        print("❌ Registration failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== Testing Other Endpoints ===")
# Test some basic endpoints
endpoints = [
    "/societies/",
    "/permissions/", 
    "/auth/profile/"
]

for endpoint in endpoints:
    try:
        response = requests.get(BASE_URL + endpoint)
        print(f"{endpoint}: {response.status_code}")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")