from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model"""
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'role', 'society', 'is_active')
    list_filter = ('role', 'is_active', 'society')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('phone_number',)
    
    fieldsets = UserAdmin.fieldsets + (  # type: ignore
        ('Additional Info', {
            'fields': ('phone_number', 'profile_picture', 'role', 'society')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (  # type: ignore
        ('Additional Info', {
            'fields': ('phone_number', 'email', 'first_name', 'last_name', 'role', 'society')
        }),
    )


@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'pincode', 'created_at')
    list_filter = ('city', 'state')
    search_fields = ('name', 'city', 'registration_number')


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ('society', 'block_number', 'flat_number', 'type', 'owner', 'tenant')
    list_filter = ('society', 'type', 'block_number')
    search_fields = ('flat_number', 'block_number', 'owner__first_name', 'tenant__first_name')


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'purpose', 'is_used', 'is_expired', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used', 'is_expired', 'created_at')
    search_fields = ('phone_number', 'otp_code', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'expires_at', 'verified_at')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'type', 'owner', 'flat')
    list_filter = ('type',)
    search_fields = ('vehicle_number', 'owner__first_name')


@admin.register(MaintenanceBill)
class MaintenanceBillAdmin(admin.ModelAdmin):
    list_display = ('flat', 'amount', 'due_date', 'status', 'payment_mode', 'paid_date')
    list_filter = ('status', 'payment_mode', 'flat__society')
    search_fields = ('flat__flat_number', 'transaction_id')


@admin.register(CommonExpense)
class CommonExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'society', 'total_amount', 'created_by', 'created_at')
    list_filter = ('society', 'created_at')
    search_fields = ('title', 'created_by__first_name')


@admin.register(CommonExpenseSplit)
class CommonExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('common_expense', 'flat', 'amount_due', 'status', 'paid_date')
    list_filter = ('status', 'flat__society')
    search_fields = ('common_expense__title', 'flat__flat_number')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'society', 'created_at')
    list_filter = ('society', 'created_at')
    search_fields = ('title', 'content')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'society')
    list_filter = ('society',)
    search_fields = ('name',)


@admin.register(AmenityBooking)
class AmenityBookingAdmin(admin.ModelAdmin):
    list_display = ('amenity', 'booked_by', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'amenity__society')
    search_fields = ('booked_by__first_name', 'amenity__name')


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'flat_to_visit', 'status', 'entry_time')
    list_filter = ('status', 'flat_to_visit__society')
    search_fields = ('name', 'phone_number', 'pass_code')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'raised_by', 'flat', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'flat__society')
    search_fields = ('title', 'description', 'raised_by__first_name')


@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'posted_by__first_name')


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'posted_by__first_name')


@admin.register(AdBanner)
class AdBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement_location', 'is_active', 'start_date', 'end_date')
    list_filter = ('placement_location', 'is_active')
    search_fields = ('title',)
