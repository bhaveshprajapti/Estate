#!/usr/bin/env python3
"""
Quick Vehicle Test - Test just the vehicle endpoint
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def test_vehicle_creation():
    """Test vehicle creation with correct fields"""
    print("🔍 QUICK VEHICLE CREATION TEST")
    print("="*50)
    
    # Register and login
    admin_data = {
        "phone_number": f"95{random.randint(10000000, 99999999)}",
        "email": "vehicletest@test.com",
        "first_name": "Vehicle",
        "last_name": "Test",
        "password": "test123456",
        "password_confirm": "test123456"
    }
    
    print("1. Testing Authentication...")
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    if response.status_code == 201:
        print("✅ Registration works")
        
        # Login
        login_data = {
            "phone_number": admin_data['phone_number'],
            "password": "test123456"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
        if response.status_code == 200:
            print("✅ Login works")
            tokens = response.json()['tokens']
            user_id = response.json()['user']['id']
            headers = {"Authorization": f"Bearer {tokens['access']}"}
            
            # Create society first
            print("\n2. Creating Society...")
            society_data = {
                "name": f"Vehicle Test Society {random.randint(1000, 9999)}",
                "address": "123 Test Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "registration_number": f"VTS{random.randint(1000, 9999)}"
            }
            
            response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
            if response.status_code == 201:
                society_id = response.json()['id']
                print(f"✅ Society created: {response.json()['name']}")
                
                # Create building
                print("\n3. Creating Building...")
                building_data = {
                    "society": society_id,
                    "name": "Test Tower",
                    "description": "Test building",
                    "total_floors": 5,
                    "flats_per_floor": 4,
                    "total_units": 20
                }
                
                response = requests.post(f"{BASE_URL}/buildings/", json=building_data, headers=headers)
                if response.status_code == 201:
                    building_id = response.json()['id']
                    print(f"✅ Building created: {response.json()['name']}")
                    
                    # Create flat (use regular flats, not enhanced-flats)
                    print("\n4. Creating Flat...")
                    flat_data = {
                        "society": society_id,
                        "block_number": "A",
                        "flat_number": "101",
                        "type": "2BHK",
                        "area_sqft": 1200,
                        "owner": user_id
                    }
                    
                    response = requests.post(f"{BASE_URL}/flats/", json=flat_data, headers=headers)
                    if response.status_code == 201:
                        flat_id = response.json()['id']
                        print(f"✅ Flat created: {response.json()['flat_number']}")
                        
                        # Now test vehicle creation with correct fields
                        print("\n5. Testing Vehicle Creation...")
                        
                        # First, let's verify the flat exists by retrieving it
                        print(f"\n5a. Verifying flat exists...")
                        flat_check_response = requests.get(f"{BASE_URL}/enhanced-flats/{flat_id}/", headers=headers)
                        if flat_check_response.status_code == 200:
                            print(f"✅ Flat verified: {flat_check_response.json()}")
                        else:
                            print(f"❌ Flat verification failed: {flat_check_response.status_code}")
                            print(f"Response: {flat_check_response.text}")
                        
                        # Also check if we need to use the regular 'flats' endpoint instead
                        print(f"\n5b. Checking regular flats endpoint...")
                        flats_response = requests.get(f"{BASE_URL}/flats/", headers=headers)
                        if flats_response.status_code == 200:
                            flats_data = flats_response.json()
                            print(f"Regular flats available: {len(flats_data)} flats")
                            print(f"Flats data structure: {flats_data}")
                            
                            # Handle different response structures
                            flats_list = flats_data
                            if isinstance(flats_data, dict) and 'results' in flats_data:
                                flats_list = flats_data['results']
                            
                            if len(flats_list) > 0:
                                print(f"First flat: {flats_list[0]}")
                                # Use the regular flat ID if available
                                regular_flat_id = flats_list[0].get('id')
                                if regular_flat_id:
                                    flat_id = regular_flat_id
                                    print(f"Using regular flat ID: {flat_id}")
                        
                        # Test with minimal required fields based on Vehicle model
                        vehicle_data = {
                            "vehicle_number": "MH01TEST123",
                            "type": "CAR",
                            "owner": user_id,
                            "flat": flat_id
                        }
                        
                        print(f"\nVehicle data: {json.dumps(vehicle_data, indent=2)}")
                        
                        response = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data, headers=headers)
                        print(f"\nVehicle creation response: {response.status_code}")
                        
                        if response.status_code == 201:
                            print("✅ Vehicle created successfully!")
                            vehicle = response.json()
                            print(f"Vehicle details: {json.dumps(vehicle, indent=2)}")
                        else:
                            print(f"❌ Vehicle creation failed: {response.status_code}")
                            print(f"Response: {response.text}")
                            
                            # Try to get validation errors
                            try:
                                error_data = response.json()
                                print(f"Error details: {json.dumps(error_data, indent=2)}")
                            except:
                                print("Could not parse error response")
                    else:
                        print(f"❌ Flat creation failed: {response.status_code}")
                        print(f"Response: {response.text}")
                else:
                    print(f"❌ Building creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print(f"❌ Society creation failed: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    try:
        test_vehicle_creation()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")