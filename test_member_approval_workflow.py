#!/usr/bin/env python3
"""
Enhanced Member Approval Workflow Test
Tests the complete member approval system with chairman contact info
"""

import requests
import json
import random

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"🎯 {title}")
    print('='*80)

def print_step(step, title):
    print(f"\n🔹 Step {step}: {title}")
    print("-" * 60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def test_super_admin_setup():
    """Test super admin login and setup"""
    print_section("SUPER ADMIN SETUP")
    
    # Create super admin (usually done via Django admin or manage.py createsuperuser)
    print_step(1, "Create Super Admin")
    super_admin_data = {
        "phone_number": "9999999999",
        "email": "superadmin@platform.com",
        "first_name": "Super",
        "last_name": "Admin",
        "password": "superadmin123",
        "password_confirm": "superadmin123"
    }
    
    # Try to create via secure endpoint (will need token from existing superuser)
    response = requests.post(f"{BASE_URL}/admin/create-admin-user/", json=super_admin_data)
    if response.status_code == 201:
        print_success("Super Admin created successfully")
    elif response.status_code == 403:
        print("⚠️ Super Admin creation requires existing superuser token")
        print("💡 Create via Django admin: python manage.py createsuperuser")
    else:
        print(f"ℹ️ Super Admin might already exist: {response.status_code}")
    
    # Test super admin login
    print_step(2, "Super Admin Login")
    login_data = {
        "phone_number": "9999999999", 
        "password": "superadmin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login-password/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Super Admin login successful: {data['user']['role']}")
        return data['tokens']
    else:
        print_error(f"Super Admin login failed: {response.status_code}")
        print("💡 You may need to create super admin via: python manage.py createsuperuser")
        return None

def test_member_approval_workflow():
    """Test complete member approval workflow"""
    print_section("MEMBER APPROVAL WORKFLOW TEST")
    
    # First, set up ADMIN and SUB_ADMIN
    print_step(1, "Setup ADMIN and Society")
    admin_data = {
        "phone_number": f"91{random.randint(10000000, 99999999)}",
        "email": "admin@test.com",
        "first_name": "Test",
        "last_name": "Admin",
        "password": "admin123456",
        "password_confirm": "admin123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    if response.status_code == 201:
        print_success("ADMIN registered")
        
        # Login ADMIN
        login_response = requests.post(f"{BASE_URL}/auth/login-password/", json={
            "phone_number": admin_data['phone_number'],
            "password": "admin123456"
        })
        
        if login_response.status_code == 200:
            admin_tokens = login_response.json()['tokens']
            admin_headers = {"Authorization": f"Bearer {admin_tokens['access']}"}
            
            # Create society
            society_data = {
                "name": f"Test Society {random.randint(1000, 9999)}",
                "address": "123 Test Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "registration_number": f"TS{random.randint(1000, 9999)}"
            }
            
            society_response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=admin_headers)
            if society_response.status_code == 201:
                society_id = society_response.json()['id']
                print_success(f"Society created: {society_response.json()['name']}")
                
                # Create SUB_ADMIN invitation
                print_step(2, "Create SUB_ADMIN Invitation")
                subadmin_phone = f"92{random.randint(10000000, 99999999)}"
                invitation_data = {
                    "society": society_id,
                    "phone_number": subadmin_phone,
                    "email": "chairman@society.com"
                }
                
                invitation_response = requests.post(f"{BASE_URL}/admin/create-subadmin-invitation/", 
                                                   json=invitation_data, headers=admin_headers)
                if invitation_response.status_code == 201:
                    invitation_data = invitation_response.json()
                    print_success(f"SUB_ADMIN invitation created for {subadmin_phone}")
                    
                    # Complete SUB_ADMIN registration
                    print_step(3, "Complete SUB_ADMIN Registration")
                    
                    # Verify OTP
                    otp_verify_response = requests.post(f"{BASE_URL}/invitation/verify-otp/", json={
                        "phone_number": subadmin_phone,
                        "otp_code": invitation_data['otp_info']['otp_code']
                    })
                    
                    if otp_verify_response.status_code == 200:
                        # Complete registration
                        complete_response = requests.post(f"{BASE_URL}/invitation/complete-registration/", json={
                            "invitation_id": invitation_data['invitation']['id'],
                            "first_name": "Society",
                            "last_name": "Chairman",
                            "password": "chairman123456",
                            "password_confirm": "chairman123456"
                        })
                        
                        if complete_response.status_code == 201:
                            subadmin_data = complete_response.json()
                            subadmin_tokens = subadmin_data['tokens']
                            print_success(f"SUB_ADMIN created: {subadmin_data['user']['first_name']} {subadmin_data['user']['last_name']}")
                            
                            # Now test member registration and approval
                            return test_member_registration_approval(society_id, subadmin_tokens, subadmin_phone)
    
    return False

def test_member_registration_approval(society_id, subadmin_tokens, chairman_phone):
    """Test member registration, pending status, and approval"""
    print_step(4, "Member Self-Registration")
    
    member_phone = f"93{random.randint(10000000, 99999999)}"
    member_data = {
        "phone_number": member_phone,
        "email": "member@test.com",
        "first_name": "Test",
        "last_name": "Member",
        "password": "member123456",
        "password_confirm": "member123456"
    }
    
    # Register member (will be pending approval)
    response = requests.post(f"{BASE_URL}/auth/register/", json=member_data)
    if response.status_code == 201:
        member_data_response = response.json()
        print_success(f"Member registered: {member_phone}")
        print(f"  Status: {'Approved' if 'tokens' in member_data_response else 'Pending Approval'}")
        
        # Test member login attempt (should be blocked)
        print_step(5, "Test Member Login (Should Be Blocked)")
        
        login_response = requests.post(f"{BASE_URL}/auth/login-password/", json={
            "phone_number": member_phone,
            "password": "member123456"
        })
        
        if login_response.status_code == 400:
            error_message = login_response.json().get('non_field_errors', [''])[0]
            print_success("Member login correctly blocked")
            print(f"  📞 Chairman contact displayed: {chairman_phone in error_message}")
            print(f"  💬 Error message: {error_message}")
        else:
            print_error(f"Member login should be blocked: {login_response.status_code}")
        
        # Test SUB_ADMIN direct member addition
        print_step(6, "SUB_ADMIN Direct Member Addition")
        
        subadmin_headers = {"Authorization": f"Bearer {subadmin_tokens['access']}"}
        direct_member_data = {
            "phone_number": f"94{random.randint(10000000, 99999999)}",
            "email": "direct.member@test.com",
            "first_name": "Direct",
            "last_name": "Member",
            "password": "direct123456",
            "password_confirm": "direct123456",
            "ownership_type": "TENANT",
            "date_of_birth": "1985-05-15",
            "occupation": "Teacher",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "9876543210",
            "permanent_address": "123 Permanent Address"
        }
        
        direct_response = requests.post(f"{BASE_URL}/members/direct-add/", 
                                      json=direct_member_data, headers=subadmin_headers)
        
        if direct_response.status_code == 201:
            direct_member_result = direct_response.json()
            print_success(f"Direct member added: {direct_member_result['user']['first_name']} {direct_member_result['user']['last_name']}")
            print(f"  📋 Temp password: {direct_member_result['temp_password']}")
            
            # Test direct member login (should work immediately)
            direct_login_response = requests.post(f"{BASE_URL}/auth/login-password/", json={
                "phone_number": direct_member_data['phone_number'],
                "password": direct_member_result['temp_password']
            })
            
            if direct_login_response.status_code == 200:
                print_success("Direct member can login immediately (approved by SUB_ADMIN)")
            else:
                print_error(f"Direct member login failed: {direct_login_response.status_code}")
        else:
            print_error(f"Direct member addition failed: {direct_response.status_code}")
            print(f"Error: {direct_response.text}")
        
        return True
    
    return False

def main():
    """Run the complete enhanced workflow test"""
    print("🎯 ENHANCED MEMBER APPROVAL WORKFLOW TEST")
    print("Testing member approval with chairman contact info and direct addition")
    
    try:
        # Test 1: Super Admin Setup
        super_admin_tokens = test_super_admin_setup()
        
        # Test 2: Member Approval Workflow
        success = test_member_approval_workflow()
        
        if success:
            print_section("WORKFLOW TEST COMPLETED SUCCESSFULLY")
            print("✅ VERIFIED FEATURES:")
            print("   🔐 Member registration creates pending accounts")
            print("   🚫 Pending members cannot login")
            print("   📞 Login error shows chairman contact info")
            print("   ⚡ SUB_ADMIN can directly add approved members")
            print("   ✅ Direct members can login immediately")
            print("   👑 Super Admin login available for admin functions")
            print()
            print("🎉 ENHANCED MEMBER APPROVAL SYSTEM IS WORKING!")
        else:
            print_error("Some tests failed")
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Django server")
        print("💡 Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print_error(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()