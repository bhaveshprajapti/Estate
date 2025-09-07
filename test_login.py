import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test different login combinations
login_attempts = [
    {"phone_number": "9999999999", "password": "test123456"},
    {"phone_number": "9999999999", "password": "test123"},
    {"phone_number": "1111111111", "password": "test123456"},
    {"phone_number": "1111111111", "password": "test123"},
]

print("=== Testing Login with Different Credentials ===")

for i, login_data in enumerate(login_attempts):
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Attempt {i+1}: {login_data['phone_number']} - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Role: {data['user']['role']}")
            
            # Test authenticated endpoint
            headers = {"Authorization": f"Bearer {data['tokens']['access']}"}
            test_response = requests.get(f"{BASE_URL}/societies/", headers=headers)
            print(f"Societies endpoint: {test_response.status_code}")
            
            # Test profile
            profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
            print(f"Profile endpoint: {profile_response.status_code}")
            
            # Test dashboard stats
            stats_response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
            print(f"Dashboard stats: {stats_response.status_code}")
            if stats_response.status_code == 200:
                print(f"Stats: {stats_response.json()}")
            
            break
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n=== Testing New User Registration ===")
# Try with a completely new phone number
new_user_data = {
    "phone_number": "8888888888",
    "email": "newuser@test.com", 
    "first_name": "New",
    "last_name": "User",
    "password": "test123456",
    "password_confirm": "test123456",
    "role": "ADMIN"
}

response = requests.post(f"{BASE_URL}/auth/register/", json=new_user_data)
print(f"New registration: {response.status_code}")
if response.status_code in [200, 201]:
    print("✅ New user created successfully")
    data = response.json()
    print(f"New user ID: {data['user']['id']}")
else:
    print(f"❌ Failed: {response.text}")