#!/usr/bin/env python3
"""
Debug Vehicle Test - Test vehicle creation with proper debugging
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def debug_vehicle_test():
    """Debug vehicle creation step by step"""
    print("🔍 DEBUG VEHICLE CREATION")
    print("="*50)
    
    # Use existing data from previous tests to avoid recreation
    print("1. Quick Authentication...")
    admin_data = {
        "phone_number": f"94{random.randint(10000000, 99999999)}",
        "email": "debug@test.com",
        "first_name": "Debug",
        "last_name": "Test",
        "password": "test123456",
        "password_confirm": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    if response.status_code == 201:
        user_id = response.json()['user']['id']
        
        # Login
        login_data = {
            "phone_number": admin_data['phone_number'],
            "password": "test123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
        if response.status_code == 200:
            tokens = response.json()['tokens']
            headers = {"Authorization": f"Bearer {tokens['access']}"}
            
            print("✅ Authenticated successfully")
            
            # Get existing flats instead of creating new ones
            print("\n2. Getting existing flats...")
            response = requests.get(f"{BASE_URL}/flats/", headers=headers)
            if response.status_code == 200:
                flats_data = response.json()
                print(f"Flats response structure: {type(flats_data)}")
                print(f"Flats data: {flats_data}")
                
                # Handle different response structures (paginated vs direct list)
                flats = flats_data
                if isinstance(flats_data, dict) and 'results' in flats_data:
                    flats = flats_data['results']
                elif isinstance(flats_data, dict) and 'count' in flats_data:
                    # Handle pagination structure
                    flats = flats_data.get('results', [])
                
                print(f"Found {len(flats)} existing flats")
                
                if len(flats) > 0:
                    # Use the first available flat
                    flat = flats[0]
                    flat_id = flat['id']
                    print(f"Using flat: {json.dumps(flat, indent=2)}")
                    
                    # Test minimal vehicle creation
                    print(f"\n3. Testing Vehicle Creation...")
                    vehicle_data = {
                        "vehicle_number": f"TEST{random.randint(1000, 9999)}",
                        "type": "CAR",
                        "owner": user_id,
                        "flat": flat_id
                    }
                    
                    print(f"Vehicle data: {json.dumps(vehicle_data, indent=2)}")
                    print(f"User ID: {user_id}")
                    print(f"Flat ID: {flat_id}")
                    
                    response = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data, headers=headers)
                    print(f"\nVehicle creation response: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                    print(f"Response text: {response.text}")
                    
                    if response.status_code == 201:
                        print("✅ Vehicle created successfully!")
                        vehicle = response.json()
                        print(f"Vehicle details: {json.dumps(vehicle, indent=2)}")
                    else:
                        print(f"❌ Vehicle creation failed: {response.status_code}")
                        try:
                            error_data = response.json()
                            print(f"Error details: {json.dumps(error_data, indent=2)}")
                        except:
                            print("Could not parse error response")
                            
                        # Let's also check if the user and flat actually exist
                        print(f"\n4. Verifying user exists...")
                        user_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
                        print(f"User profile status: {user_response.status_code}")
                        if user_response.status_code == 200:
                            user_profile = user_response.json()
                            print(f"User profile: {json.dumps(user_profile, indent=2)}")
                        
                        print(f"\n5. Verifying flat exists...")
                        flat_response = requests.get(f"{BASE_URL}/flats/{flat_id}/", headers=headers)
                        print(f"Flat detail status: {flat_response.status_code}")
                        if flat_response.status_code == 200:
                            flat_detail = flat_response.json()
                            print(f"Flat detail: {json.dumps(flat_detail, indent=2)}")
                        else:
                            print(f"Flat detail error: {flat_response.text}")
                else:
                    print("❌ No flats available, need to create one first")
            else:
                print(f"❌ Failed to get flats: {response.status_code}")
        else:
            print(f"❌ Login failed: {response.status_code}")
    else:
        print(f"❌ Registration failed: {response.status_code}")

if __name__ == "__main__":
    try:
        debug_vehicle_test()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")