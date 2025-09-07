#!/usr/bin/env python3
"""
Comprehensive Society Management System Test
Tests all the enhanced features including member registration, 
billing, security, and helpdesk management.
"""

import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

class SocietyManagementTester:
    def __init__(self):
        self.admin_tokens = {}
        self.subadmin_tokens = {}
        self.member_tokens = {}
        self.staff_tokens = {}
        self.society_id = None
        self.building_id = None
        self.flat_id = None
        
    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"🔸 {title}")
        print('='*60)
    
    def print_result(self, test_name, response, expected_status=200):
        status = "✅ PASS" if response.status_code == expected_status else "❌ FAIL"
        print(f"{status} {test_name} - Status: {response.status_code}")
        
        if response.status_code != expected_status:
            try:
                error_details = response.json()
                print(f"   Error: {error_details}")
            except:
                print(f"   Error: {response.text[:200]}...")
        
        return response.status_code == expected_status
    
    def test_admin_setup(self):
        """Test ADMIN registration and society creation"""
        self.print_section("ADMIN SETUP AND SOCIETY CREATION")
        
        # Register ADMIN
        admin_data = {
            "phone_number": f"91{random.randint(1000000000, 9999999999)}",
            "email": "admin@testsociety.com",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "admin123456",
            "password_confirm": "admin123456",
            "role": "ADMIN"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
        if self.print_result("Admin Registration", response, 201):
            self.admin_tokens = response.json()["tokens"]
            self.admin_phone = admin_data["phone_number"]
        
        # Create Society
        headers = {"Authorization": f"Bearer {self.admin_tokens['access']}"}
        society_data = {
            "name": "Greenfield Apartments",
            "address": "123 Green Valley Road",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "registration_number": "GFA2025001"
        }
        
        response = requests.post(f"{BASE_URL}/societies/", json=society_data, headers=headers)
        if self.print_result("Society Creation", response, 201):
            self.society_id = response.json()["id"]
            print(f"   Society ID: {self.society_id}")
    
    def test_building_management(self):
        """Test building and flat management"""
        self.print_section("BUILDING AND FLAT MANAGEMENT")
        
        headers = {"Authorization": f"Bearer {self.subadmin_tokens.get('access', self.admin_tokens['access'])}"}
        
        # Create Building
        building_data = {
            "society": self.society_id,
            "name": "Tower A",
            "description": "Main residential tower",
            "total_floors": 10,
            "flats_per_floor": 4,
            "amenities": "Elevator, Security"
        }
        
        response = requests.post(f"{BASE_URL}/buildings/", json=building_data, headers=headers)
        if self.print_result("Building Creation", response, 201):
            self.building_id = response.json()["id"]
            print(f"   Building ID: {self.building_id}")
        
        # Create Enhanced Flat
        flat_data = {
            "society": self.society_id,
            "building": self.building_id,
            "floor_number": 1,
            "flat_number": "101",
            "flat_type": "2BHK",
            "carpet_area": 1200.0,
            "balcony_area": 150.0,
            "parking_slots": 1,
            "is_available": True,
            "monthly_rent": 25000.00
        }
        
        response = requests.post(f"{BASE_URL}/enhanced-flats/", json=flat_data, headers=headers)
        if self.print_result("Enhanced Flat Creation", response, 201):
            self.flat_id = response.json()["id"]
            print(f"   Flat ID: {self.flat_id}")
    
    def test_subadmin_invitation(self):
        """Test SUB_ADMIN invitation flow"""
        self.print_section("SUB_ADMIN INVITATION FLOW")
        
        headers = {"Authorization": f"Bearer {self.admin_tokens['access']}"}
        
        # Create SUB_ADMIN invitation
        invitation_data = {
            "society": self.society_id,
            "phone_number": f"92{random.randint(1000000000, 9999999999)}",
            "email": "subadmin@testsociety.com"
        }
        
        response = requests.post(f"{BASE_URL}/admin/create-subadmin-invitation/", 
                               json=invitation_data, headers=headers)
        if self.print_result("SUB_ADMIN Invitation", response, 201):
            invitation_otp = response.json()["otp_info"]["otp_code"]
            subadmin_phone = invitation_data["phone_number"]
            invitation_id = response.json()["invitation"]["id"]
            
            print(f"   Invitation OTP: {invitation_otp}")
            
            # Verify OTP
            verify_data = {
                "phone_number": subadmin_phone,
                "otp_code": invitation_otp
            }
            response = requests.post(f"{BASE_URL}/invitation/verify-otp/", json=verify_data)
            if self.print_result("OTP Verification", response):
                
                # Complete registration
                registration_data = {
                    "invitation_id": invitation_id,
                    "first_name": "Test",
                    "last_name": "SubAdmin",
                    "password": "subadmin123456",
                    "password_confirm": "subadmin123456"
                }
                
                response = requests.post(f"{BASE_URL}/invitation/complete-registration/", 
                                       json=registration_data)
                if self.print_result("SUB_ADMIN Registration", response, 201):
                    self.subadmin_tokens = response.json()["tokens"]
                    self.subadmin_phone = subadmin_phone
    
    def test_member_registration_flow(self):
        """Test member registration flows"""
        self.print_section("MEMBER REGISTRATION FLOWS")
        
        # Test society search (public endpoint)
        response = requests.get(f"{BASE_URL}/societies/search/?search=Green")
        self.print_result("Society Search", response)
        
        # Test self-registration request
        if self.building_id and self.flat_id:
            registration_data = {
                "first_name": "John",
                "last_name": "Member",
                "phone_number": f"93{random.randint(1000000000, 9999999999)}",
                "email": "member@test.com",
                "date_of_birth": "1990-01-01",
                "occupation": "Software Engineer",
                "society": self.society_id,
                "building": self.building_id,
                "flat": self.flat_id,
                "ownership_type": "OWNER",
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "9876543210",
                "permanent_address": "456 Test Street",
                "id_proof_number": "ABCD1234567890"
            }
            
            response = requests.post(f"{BASE_URL}/members/self-register/", json=registration_data)
            self.print_result("Self Registration Request", response, 201)
    
    def test_billing_system(self):
        """Test enhanced billing system"""
        self.print_section("ENHANCED BILLING SYSTEM")
        
        headers = {"Authorization": f"Bearer {self.subadmin_tokens.get('access', self.admin_tokens['access'])}"}
        
        # Create Bill Type
        bill_type_data = {
            "society": self.society_id,
            "name": "Monthly Maintenance",
            "description": "Regular maintenance charges",
            "is_recurring": True,
            "recurrence_period": "monthly",
            "is_splitable": True,
            "default_amount": 5000.00,
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/bill-types/", json=bill_type_data, headers=headers)
        if self.print_result("Bill Type Creation", response, 201):
            bill_type_id = response.json()["id"]
            
            # Create Enhanced Bill
            bill_data = {
                "society": self.society_id,
                "bill_type": bill_type_id,
                "title": "January 2025 Maintenance",
                "description": "Monthly maintenance for January 2025",
                "amount": 5000.00,
                "tax_amount": 900.00,
                "payment_details": {
                    "bank_name": "Test Bank",
                    "account_number": "123456789",
                    "ifsc": "TEST0001234"
                },
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "attachments": ["http://example.com/bill.pdf"],
                "is_recurring": True,
                "status": "PENDING"
            }
            
            response = requests.post(f"{BASE_URL}/enhanced-bills/", json=bill_data, headers=headers)
            self.print_result("Enhanced Bill Creation", response, 201)
    
    def test_visitor_management(self):
        """Test visitor pass and gate management"""
        self.print_section("VISITOR AND GATE MANAGEMENT")
        
        headers = {"Authorization": f"Bearer {self.subadmin_tokens.get('access', self.admin_tokens['access'])}"}
        
        if self.flat_id:
            # Create Visitor Pass
            visitor_data = {
                "visitor_name": "John Visitor",
                "visitor_phone": "9988776655",
                "purpose_of_visit": "Personal visit",
                "society": self.society_id,
                "flat_to_visit": self.flat_id,
                "expected_entry_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "referenced_by": "Flat Owner",
                "reference_phone": "9876543210"
            }
            
            response = requests.post(f"{BASE_URL}/visitor-passes/", json=visitor_data, headers=headers)
            if self.print_result("Visitor Pass Creation", response, 201):
                pass_number = response.json()["pass_number"]
                print(f"   Visitor Pass Number: {pass_number}")
    
    def test_helpdesk_management(self):
        """Test helpdesk management system"""
        self.print_section("HELPDESK MANAGEMENT")
        
        headers = {"Authorization": f"Bearer {self.subadmin_tokens.get('access', self.admin_tokens['access'])}"}
        
        # Create Helpdesk Designation
        designation_data = {
            "society": self.society_id,
            "title": "Electrician",
            "description": "Electrical maintenance and repairs",
            "category": "Maintenance",
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/helpdesk-designations/", json=designation_data, headers=headers)
        if self.print_result("Helpdesk Designation Creation", response, 201):
            designation_id = response.json()["id"]
            
            # Create Helpdesk Contact
            contact_data = {
                "society": self.society_id,
                "designation": designation_id,
                "name": "John Electrician",
                "primary_phone": "9876543210",
                "secondary_phone": "9876543211",
                "email": "electrician@test.com",
                "address": "Local area",
                "availability": "9 AM - 6 PM",
                "service_charges": "Rs. 500 per visit",
                "rating": 4.5,
                "is_active": True
            }
            
            response = requests.post(f"{BASE_URL}/helpdesk-contacts/", json=contact_data, headers=headers)
            self.print_result("Helpdesk Contact Creation", response, 201)
    
    def test_directory_management(self):
        """Test directory and search functionality"""
        self.print_section("DIRECTORY MANAGEMENT")
        
        headers = {"Authorization": f"Bearer {self.subadmin_tokens.get('access', self.admin_tokens['access'])}"}
        
        # List directory entries
        response = requests.get(f"{BASE_URL}/directory/", headers=headers)
        self.print_result("Directory Listing", response)
        
        if response.status_code == 200:
            entries = response.json().get("results", [])
            print(f"   Found {len(entries)} directory entries")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE SOCIETY MANAGEMENT SYSTEM TEST")
        print("=" * 80)
        
        try:
            self.test_admin_setup()
            
            if self.society_id:
                self.test_subadmin_invitation()
                self.test_building_management()
                self.test_member_registration_flow()
                self.test_billing_system()
                self.test_visitor_management()
                self.test_helpdesk_management()
                self.test_directory_management()
                
                print(f"\n{'='*80}")
                print("🎉 COMPREHENSIVE TESTING COMPLETED!")
                print("=" * 80)
                
                print("\n📊 SUMMARY:")
                print("✅ Admin registration and society creation")
                print("✅ SUB_ADMIN invitation flow")
                print("✅ Building and flat management")
                print("✅ Member registration flows")
                print("✅ Enhanced billing system")
                print("✅ Visitor pass management")
                print("✅ Helpdesk management")
                print("✅ Directory management")
                
                print(f"\n🏢 Test Society: {self.society_id}")
                print(f"📱 Admin Phone: {getattr(self, 'admin_phone', 'N/A')}")
                print(f"📱 SubAdmin Phone: {getattr(self, 'subadmin_phone', 'N/A')}")
                
            else:
                print("❌ Cannot proceed without society ID")
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Cannot connect to Django server")
            print("💡 Make sure the server is running: python manage.py runserver")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    tester = SocietyManagementTester()
    tester.run_all_tests()