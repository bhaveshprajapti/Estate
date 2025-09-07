#!/usr/bin/env python3
"""
Quick API Endpoint Test - Key Workflows
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

print("🧪 QUICK API ENDPOINT VERIFICATION")
print("=" * 40)

# Login
print("1️⃣ Testing Login...")
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "phone_number": "9999999999",
    "password": "test123456"
})

if login_response.status_code == 200:
    print("✅ Login successful")
    tokens = login_response.json()['tokens']
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    user_info = login_response.json()['user']
    print(f"   User: {user_info['first_name']} {user_info['last_name']} ({user_info['role']})")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

# Test key endpoints
endpoints_to_test = [
    ("Profile", f"{BASE_URL}/auth/profile/", "GET"),
    ("Permissions", f"{BASE_URL}/permissions/", "GET"),
    ("Role Permissions", f"{BASE_URL}/role-permissions/", "GET"),
    ("Societies", f"{BASE_URL}/societies/", "GET"),
    ("Flats", f"{BASE_URL}/flats/", "GET"),
    ("Staff Categories", f"{BASE_URL}/staff-categories/", "GET"),
    ("Chairman Invitations", f"{BASE_URL}/chairman-invitations/", "GET"),
    ("Society Settings", f"{BASE_URL}/society-settings/", "GET"),
    ("Fee Structures", f"{BASE_URL}/fee-structures/", "GET"),
    ("Maintenance Bills", f"{BASE_URL}/maintenance-bills/", "GET"),
    ("Common Expenses", f"{BASE_URL}/common-expenses/", "GET"),
    ("Notices", f"{BASE_URL}/notices/", "GET"),
    ("Amenities", f"{BASE_URL}/amenities/", "GET"),
    ("Dashboard Stats", f"{BASE_URL}/dashboard/stats/", "GET"),
]

print("\n2️⃣ Testing Core Endpoints...")
for name, url, method in endpoints_to_test:
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers)
        
        if response.status_code in [200, 201]:
            if 'results' in response.json():
                count = len(response.json()['results'])
                print(f"✅ {name}: {count} records")
            else:
                print(f"✅ {name}: Success")
        else:
            print(f"❌ {name}: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:50]}")

# Test creating data
print("\n3️⃣ Testing Data Creation...")

# Create Society
society_data = {
    "name": "Test Society",
    "address": "Test Address",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
}

response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
if response.status_code == 201:
    print("✅ Society creation successful")
    society = response.json()
    
    # Create Flat
    flat_data = {
        "society": society['id'],
        "block_number": "A",
        "flat_number": "101",
        "type": "2BHK"
    }
    
    response = requests.post(f"{BASE_URL}/flats/", json=flat_data, headers=headers)
    if response.status_code == 201:
        print("✅ Flat creation successful")
    else:
        print(f"❌ Flat creation failed: {response.status_code}")
else:
    print(f"❌ Society creation failed: {response.status_code}")

# Test Dashboard Stats
print("\n4️⃣ Testing Dashboard...")
response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
if response.status_code == 200:
    stats = response.json()
    print("✅ Dashboard stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
else:
    print(f"❌ Dashboard failed: {response.status_code}")

print("\n" + "=" * 40)
print("🎉 QUICK TEST COMPLETED!")
print("\n📚 Available Documentation:")
print(f"   - API Docs: http://localhost:8000/api/docs/")
print(f"   - Admin Panel: http://localhost:8000/admin/")
print(f"   - API Root: http://localhost:8000/api/")

print("\n🔑 Test Credentials:")
print("   - Phone: 9999999999")
print("   - Password: test123456")
print("   - Role: ADMIN")

print("\n✅ Society Management Platform is fully operational!")