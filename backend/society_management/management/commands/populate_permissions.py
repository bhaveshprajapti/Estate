from django.core.management.base import BaseCommand
from society_management.models import Permission, RolePermission


class Command(BaseCommand):
    help = 'Populate default permissions and role permissions for the system'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating default permissions...')
        
        # Define default permissions
        permissions_data = [
            # User Management
            {
                'name': 'Create Users',
                'code': 'create_users',
                'description': 'Ability to create new users in the system',
                'category': 'USER_MANAGEMENT'
            },
            {
                'name': 'View All Users',
                'code': 'view_all_users',
                'description': 'Ability to view all users in the system',
                'category': 'USER_MANAGEMENT'
            },
            {
                'name': 'Update User Roles',
                'code': 'update_user_roles',
                'description': 'Ability to change user roles',
                'category': 'USER_MANAGEMENT'
            },
            {
                'name': 'Deactivate Users',
                'code': 'deactivate_users',
                'description': 'Ability to deactivate/activate users',
                'category': 'USER_MANAGEMENT'
            },
            
            # Billing & Payments
            {
                'name': 'Manage Maintenance Bills',
                'code': 'manage_maintenance_bills',
                'description': 'Create, update, delete maintenance bills',
                'category': 'BILLING'
            },
            {
                'name': 'View Payment History',
                'code': 'view_payment_history',
                'description': 'View payment transactions and history',
                'category': 'BILLING'
            },
            {
                'name': 'Manage Common Expenses',
                'code': 'manage_common_expenses',
                'description': 'Create and manage shared expenses',
                'category': 'BILLING'
            },
            
            # Community Features
            {
                'name': 'Manage Notices',
                'code': 'manage_notices',
                'description': 'Create, update, delete notices',
                'category': 'COMMUNITY'
            },
            {
                'name': 'Manage Amenities',
                'code': 'manage_amenities',
                'description': 'Add, remove, configure amenities',
                'category': 'COMMUNITY'
            },
            {
                'name': 'Approve Bookings',
                'code': 'approve_bookings',
                'description': 'Approve or reject amenity bookings',
                'category': 'COMMUNITY'
            },
            {
                'name': 'Moderate Marketplace',
                'code': 'moderate_marketplace',
                'description': 'Approve/reject marketplace listings',
                'category': 'COMMUNITY'
            },
            
            # Security & Visitors
            {
                'name': 'Manage Visitor Logs',
                'code': 'manage_visitor_logs',
                'description': 'View and manage visitor entries/exits',
                'category': 'SECURITY'
            },
            {
                'name': 'Configure Security Settings',
                'code': 'configure_security',
                'description': 'Modify security and visitor policies',
                'category': 'SECURITY'
            },
            
            # Maintenance & Complaints
            {
                'name': 'Manage Complaints',
                'code': 'manage_complaints',
                'description': 'View, assign, resolve complaints',
                'category': 'MAINTENANCE'
            },
            {
                'name': 'Assign Staff Tasks',
                'code': 'assign_staff_tasks',
                'description': 'Create and assign tasks to staff',
                'category': 'MAINTENANCE'
            },
            {
                'name': 'Manage Staff Schedules',
                'code': 'manage_staff_schedules',
                'description': 'Create and modify staff duty schedules',
                'category': 'MAINTENANCE'
            },
            
            # Society Settings
            {
                'name': 'Manage Society Settings',
                'code': 'manage_society_settings',
                'description': 'Modify society configuration and settings',
                'category': 'SOCIETY_SETTINGS'
            },
            {
                'name': 'Manage Fee Structures',
                'code': 'manage_fee_structures',
                'description': 'Create and modify fee structures',
                'category': 'SOCIETY_SETTINGS'
            },
            {
                'name': 'Invite Chairmen',
                'code': 'invite_chairmen',
                'description': 'Send chairman invitations',
                'category': 'SOCIETY_SETTINGS'
            },
            
            # Reports & Analytics
            {
                'name': 'View Reports',
                'code': 'view_reports',
                'description': 'Access system reports and analytics',
                'category': 'REPORTS'
            },
            {
                'name': 'Export Data',
                'code': 'export_data',
                'description': 'Export system data',
                'category': 'REPORTS'
            }
        ]
        
        # Create permissions
        created_permissions = {}
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(  # type: ignore
                code=perm_data['code'],
                defaults=perm_data
            )
            created_permissions[perm_data['code']] = permission
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission: {perm_data["name"]}')  # type: ignore
                )
        
        # Define role permissions
        role_permissions = {
            'ADMIN': {
                # Admins have full access
                'create_users': {'create': True, 'read': True, 'update': True, 'delete': True},
                'view_all_users': {'create': True, 'read': True, 'update': True, 'delete': True},
                'update_user_roles': {'create': True, 'read': True, 'update': True, 'delete': False},
                'deactivate_users': {'create': True, 'read': True, 'update': True, 'delete': False},
                'manage_society_settings': {'create': True, 'read': True, 'update': True, 'delete': True},
                'manage_fee_structures': {'create': True, 'read': True, 'update': True, 'delete': True},
                'invite_chairmen': {'create': True, 'read': True, 'update': True, 'delete': False},
                'view_reports': {'create': False, 'read': True, 'update': False, 'delete': False},
                'export_data': {'create': True, 'read': True, 'update': False, 'delete': False},
            },
            'SUB_ADMIN': {
                # Sub-admins (Chairmen) have society-specific permissions
                'create_users': {'create': True, 'read': True, 'update': True, 'delete': False},
                'view_all_users': {'create': False, 'read': True, 'update': False, 'delete': False},
                'manage_maintenance_bills': {'create': True, 'read': True, 'update': True, 'delete': False},
                'view_payment_history': {'create': False, 'read': True, 'update': False, 'delete': False},
                'manage_common_expenses': {'create': True, 'read': True, 'update': True, 'delete': True},
                'manage_notices': {'create': True, 'read': True, 'update': True, 'delete': True},
                'manage_amenities': {'create': True, 'read': True, 'update': True, 'delete': True},
                'approve_bookings': {'create': False, 'read': True, 'update': True, 'delete': False},
                'moderate_marketplace': {'create': False, 'read': True, 'update': True, 'delete': False},
                'manage_visitor_logs': {'create': False, 'read': True, 'update': True, 'delete': False},
                'manage_complaints': {'create': False, 'read': True, 'update': True, 'delete': False},
                'assign_staff_tasks': {'create': True, 'read': True, 'update': True, 'delete': True},
                'manage_staff_schedules': {'create': True, 'read': True, 'update': True, 'delete': True},
                'view_reports': {'create': False, 'read': True, 'update': False, 'delete': False},
            },
            'MEMBER': {
                # Members have limited permissions
                'view_payment_history': {'create': False, 'read': True, 'update': False, 'delete': False},
                'manage_complaints': {'create': True, 'read': True, 'update': False, 'delete': False},
                'moderate_marketplace': {'create': True, 'read': True, 'update': True, 'delete': False},
            },
            'STAFF': {
                # Staff have task-specific permissions
                'manage_visitor_logs': {'create': True, 'read': True, 'update': True, 'delete': False},
                'manage_complaints': {'create': False, 'read': True, 'update': True, 'delete': False},
            }
        }
        
        # Create role permissions
        for role, permissions in role_permissions.items():
            for perm_code, access in permissions.items():
                if perm_code in created_permissions:
                    role_perm, created = RolePermission.objects.get_or_create(  # type: ignore
                        role=role,
                        permission=created_permissions[perm_code],
                        society=None,  # Global permissions
                        defaults={
                            'can_create': access.get('create', False),
                            'can_read': access.get('read', True),
                            'can_update': access.get('update', False),
                            'can_delete': access.get('delete', False),
                        }
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created role permission: {role} - {perm_code}')  # type: ignore
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated default permissions!')  # type: ignore
        )