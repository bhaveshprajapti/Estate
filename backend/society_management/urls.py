from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create router and register viewsets
router = DefaultRouter()

# Existing endpoints
router.register(r'societies', views.SocietyViewSet)
router.register(r'flats', views.FlatViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'maintenance-bills', views.MaintenanceBillViewSet)
router.register(r'common-expenses', views.CommonExpenseViewSet)
router.register(r'expense-splits', views.CommonExpenseSplitViewSet)
router.register(r'notices', views.NoticeViewSet)
router.register(r'amenities', views.AmenityViewSet)
router.register(r'amenity-bookings', views.AmenityBookingViewSet)
router.register(r'visitors', views.VisitorLogViewSet)
router.register(r'complaints', views.ComplaintViewSet)
router.register(r'marketplace', views.MarketplaceListingViewSet)
router.register(r'jobs', views.JobListingViewSet)
router.register(r'ad-banners', views.AdBannerViewSet)

# Enhanced management endpoints
router.register(r'chairman-invitations', views.ChairmanInvitationViewSet)
router.register(r'staff-categories', views.StaffCategoryViewSet)
router.register(r'staff-members', views.StaffMemberViewSet)
router.register(r'duty-schedules', views.DutyScheduleViewSet)
router.register(r'permissions', views.PermissionViewSet)
router.register(r'role-permissions', views.RolePermissionViewSet)
router.register(r'user-role-transitions', views.UserRoleTransitionViewSet)
router.register(r'society-settings', views.SocietySettingsViewSet)
router.register(r'fee-structures', views.FeeStructureViewSet)
router.register(r'bulk-operations', views.BulkUserOperationViewSet)
router.register(r'admin-societies', views.AdminSocietyViewSet)

# Comprehensive Society Management endpoints
router.register(r'buildings', views.BuildingViewSet)
router.register(r'enhanced-flats', views.EnhancedFlatViewSet)
router.register(r'member-requests', views.MemberRegistrationRequestViewSet)
router.register(r'member-invitations', views.MemberInvitationViewSet)
router.register(r'staff-invitations', views.StaffInvitationViewSet)
router.register(r'society-profiles', views.SocietyProfileViewSet)
router.register(r'helpdesk-designations', views.HelpdeskDesignationViewSet)
router.register(r'helpdesk-contacts', views.HelpdeskContactViewSet)
router.register(r'bill-types', views.BillTypeViewSet)
router.register(r'enhanced-bills', views.EnhancedBillViewSet)
router.register(r'bill-distributions', views.BillDistributionViewSet)
router.register(r'visitor-passes', views.VisitorPassViewSet)
router.register(r'gate-logs', views.GateUpdateLogViewSet)
router.register(r'directory', views.DirectoryEntryViewSet)
router.register(r'members', views.MemberViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),  # Legacy login with OTP
    path('auth/login-password/', views.login_with_password, name='login_with_password'),
    path('auth/login-otp-step1/', views.login_with_otp_step1, name='login_otp_step1'),
    path('auth/login-otp-step2/', views.login_with_otp_step2, name='login_otp_step2'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # SECURE USER CREATION ENDPOINTS
    path('admin/create-admin-user/', views.create_admin_user, name='create_admin_user'),  # Superuser only
    path('admin/create-staff-user/', views.create_staff_user, name='create_staff_user'),  # SUB_ADMIN/ADMIN only
    
    # OTP and Password Reset endpoints
    path('auth/forgot-password/', views.forgot_password, name='forgot_password'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('auth/reset-password/', views.reset_password, name='reset_password'),
    path('auth/send-otp/', views.send_otp, name='send_otp'),
    
    # SUB_ADMIN Invitation endpoints
    path('admin/create-subadmin-invitation/', views.create_subadmin_invitation, name='create_subadmin_invitation'),
    path('admin/subadmin-invitations/', views.list_subadmin_invitations, name='list_subadmin_invitations'),
    path('invitation/verify-otp/', views.verify_invitation_otp, name='verify_invitation_otp'),
    path('invitation/complete-registration/', views.complete_subadmin_registration, name='complete_subadmin_registration'),
    
    # Member Registration endpoints
    path('societies/search/', views.search_societies, name='search_societies'),
    path('members/self-register/', views.self_register_member, name='self_register_member'),
    path('members/direct-add/', views.direct_add_member, name='direct_add_member'),  # SUB_ADMIN direct add
    
    # Enhanced user management endpoints
    path('users/bulk-import/', views.bulk_user_import, name='bulk_user_import'),
    path('users/bulk-update/', views.bulk_user_update, name='bulk_user_update'),
    path('dashboard/stats/', views.user_dashboard_stats, name='dashboard_stats'),
    
    # API endpoints
    path('', include(router.urls)),
]