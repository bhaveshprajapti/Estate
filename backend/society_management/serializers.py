from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Society, Flat, Vehicle, MaintenanceBill, CommonExpense, 
    CommonExpenseSplit, Notice, Amenity, AmenityBooking, VisitorLog, 
    Complaint, MarketplaceListing, JobListing, AdBanner, ChairmanInvitation,
    StaffCategory, StaffMember, DutySchedule, Permission, RolePermission,
    UserRoleTransition, SocietySettings, FeeStructure, BulkUserOperation,
    AdminSociety, OTP, SubAdminInvitation
)


# Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm', 'role')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    phone_number = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if phone_number and password:
            user = authenticate(username=phone_number, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include phone number and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'first_name', 'last_name', 
                 'profile_picture', 'role', 'society', 'society_name', 
                 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'role')


# OTP Serializers
class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    phone_number = serializers.CharField()
    
    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)  # type: ignore
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            return value
        except User.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('No user found with this phone number')


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    purpose = serializers.ChoiceField(choices=[
        ('FORGOT_PASSWORD', 'Forgot Password'),
        ('REGISTRATION', 'Registration'),
        ('LOGIN', 'Login'),
        ('PHONE_VERIFICATION', 'Phone Verification'),
    ])
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        purpose = attrs.get('purpose')
        
        # Verify OTP
        otp = OTP.verify_otp(phone_number, otp_code, purpose)
        if not otp:
            raise serializers.ValidationError('Invalid or expired OTP')
        
        attrs['otp'] = otp
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset with OTP"""
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Check password confirmation
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")
        
        # Find a valid OTP (not used and not expired)
        try:
            otp = OTP.objects.get(  # type: ignore
                phone_number=phone_number,
                otp_code=otp_code,
                purpose='FORGOT_PASSWORD',
                is_used=False,
                is_expired=False
            )
            
            if not otp.is_valid():
                otp.mark_as_expired()
                raise serializers.ValidationError('OTP has expired')
        except OTP.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('Invalid OTP')
        
        # Get user
        try:
            user = User.objects.get(phone_number=phone_number)  # type: ignore
            attrs['user'] = user
        except User.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('User not found')
        
        attrs['otp'] = otp
        return attrs


class OTPSerializer(serializers.ModelSerializer):
    """Serializer for OTP model (for testing purposes)"""
    
    class Meta:
        model = OTP
        fields = ('id', 'phone_number', 'email', 'otp_code', 'purpose', 
                 'is_used', 'is_expired', 'created_at', 'expires_at')
        read_only_fields = ('id', 'created_at', 'expires_at')


# New Authentication Serializers for Dual Login
class OTPLoginSerializer(serializers.Serializer):
    """Serializer for OTP-based login verification"""
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        
        # Verify OTP
        otp = OTP.verify_otp(phone_number, otp_code, 'LOGIN')
        if not otp:
            raise serializers.ValidationError('Invalid or expired OTP')
        
        # Get user
        try:
            user = User.objects.get(phone_number=phone_number)  # type: ignore
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        except User.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('User not found')
        
        attrs['otp'] = otp
        return attrs


# SUB_ADMIN Invitation Serializers
class SubAdminInvitationSerializer(serializers.ModelSerializer):
    """Serializer for creating SUB_ADMIN invitations"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    
    class Meta:
        model = SubAdminInvitation
        fields = ('id', 'society', 'society_name', 'phone_number', 'email', 
                 'status', 'otp_verified', 'created_at', 'expires_at', 
                 'accepted_at', 'invited_by_name')
        read_only_fields = ('id', 'status', 'otp_verified', 'created_at', 
                           'expires_at', 'accepted_at')
    
    def validate_phone_number(self, value):
        # Check if user already exists
        if User.objects.filter(phone_number=value).exists():  # type: ignore
            raise serializers.ValidationError('User with this phone number already exists')
        return value
    
    def validate(self, attrs):
        society = attrs.get('society')
        phone_number = attrs.get('phone_number')
        
        # Check if there's already a pending invitation for this phone number and society
        existing_invitation = SubAdminInvitation.objects.filter(  # type: ignore
            society=society,
            phone_number=phone_number,
            status='PENDING'
        ).first()
        
        if existing_invitation and existing_invitation.is_valid():
            raise serializers.ValidationError(
                'Active invitation already exists for this phone number and society'
            )
        
        return attrs


class InvitationOTPVerificationSerializer(serializers.Serializer):
    """Serializer for verifying OTP during SUB_ADMIN invitation process"""
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        
        # Find valid invitation
        invitation = SubAdminInvitation.objects.filter(  # type: ignore
            phone_number=phone_number,
            status='PENDING',
            otp_verified=False
        ).first()
        
        if not invitation or not invitation.is_valid():
            raise serializers.ValidationError('No valid invitation found for this phone number')
        
        # Verify OTP
        otp = OTP.verify_otp(phone_number, otp_code, 'REGISTRATION')
        if not otp:
            raise serializers.ValidationError('Invalid or expired OTP')
        
        attrs['invitation'] = invitation
        attrs['otp'] = otp
        return attrs


class CompleteSubAdminRegistrationSerializer(serializers.Serializer):
    """Serializer for completing SUB_ADMIN registration"""
    invitation_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        invitation_id = attrs.get('invitation_id')
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        # Check password confirmation
        if password != password_confirm:
            raise serializers.ValidationError("Passwords don't match")
        
        # Find invitation
        try:
            invitation = SubAdminInvitation.objects.get(  # type: ignore
                id=invitation_id,
                status='PENDING',
                otp_verified=True
            )
            
            if not invitation.is_valid():
                raise serializers.ValidationError('Invitation has expired')
            
        except SubAdminInvitation.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('Invalid invitation or OTP not verified')
        
        # Check if user already exists (double check)
        if User.objects.filter(phone_number=invitation.phone_number).exists():  # type: ignore
            raise serializers.ValidationError('User with this phone number already exists')
        
        attrs['invitation'] = invitation
        return attrs


# Core Models Serializers
class SocietySerializer(serializers.ModelSerializer):
    """Serializer for Society model"""
    flats_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Society
        fields = '__all__'
    
    def get_flats_count(self, obj):
        return obj.flats.count()


class FlatSerializer(serializers.ModelSerializer):
    """Serializer for Flat model"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.get_full_name', read_only=True)
    
    class Meta:
        model = Flat
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    flat_number = serializers.CharField(source='flat.flat_number', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'


# Billing Serializers
class MaintenanceBillSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceBill model"""
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    
    class Meta:
        model = MaintenanceBill
        fields = '__all__'


class CommonExpenseSerializer(serializers.ModelSerializer):
    """Serializer for CommonExpense model"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    splits_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CommonExpense
        fields = '__all__'
        read_only_fields = ('created_by',)
    
    def get_splits_count(self, obj):
        return obj.splits.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommonExpenseSplitSerializer(serializers.ModelSerializer):
    """Serializer for CommonExpenseSplit model"""
    expense_title = serializers.CharField(source='common_expense.title', read_only=True)
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    
    class Meta:
        model = CommonExpenseSplit
        fields = '__all__'


# Community Serializers
class NoticeSerializer(serializers.ModelSerializer):
    """Serializer for Notice model"""
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('posted_by',)
    
    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = Amenity
        fields = '__all__'


class AmenityBookingSerializer(serializers.ModelSerializer):
    """Serializer for AmenityBooking model"""
    amenity_name = serializers.CharField(source='amenity.name', read_only=True)
    booked_by_name = serializers.CharField(source='booked_by.get_full_name', read_only=True)
    
    class Meta:
        model = AmenityBooking
        fields = '__all__'
        read_only_fields = ('booked_by',)
    
    def create(self, validated_data):
        validated_data['booked_by'] = self.context['request'].user
        return super().create(validated_data)


# Security Serializers
class VisitorLogSerializer(serializers.ModelSerializer):
    """Serializer for VisitorLog model"""
    flat_details = serializers.CharField(source='flat_to_visit.__str__', read_only=True)
    
    class Meta:
        model = VisitorLog
        fields = '__all__'


class ComplaintSerializer(serializers.ModelSerializer):
    """Serializer for Complaint model"""
    raised_by_name = serializers.CharField(source='raised_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('raised_by',)
    
    def create(self, validated_data):
        validated_data['raised_by'] = self.context['request'].user
        return super().create(validated_data)


# Marketplace Serializers
class MarketplaceListingSerializer(serializers.ModelSerializer):
    """Serializer for MarketplaceListing model"""
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    
    class Meta:
        model = MarketplaceListing
        fields = '__all__'
        read_only_fields = ('posted_by',)
    
    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class JobListingSerializer(serializers.ModelSerializer):
    """Serializer for JobListing model"""
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    
    class Meta:
        model = JobListing
        fields = '__all__'
        read_only_fields = ('posted_by',)
    
    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class AdBannerSerializer(serializers.ModelSerializer):
    """Serializer for AdBanner model"""
    
    class Meta:
        model = AdBanner
        fields = '__all__'


# ===== NEW SERIALIZERS FOR ENHANCED SOCIETY MANAGEMENT =====

class ChairmanInvitationSerializer(serializers.ModelSerializer):
    """Serializer for Chairman Invitation"""
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = ChairmanInvitation
        fields = '__all__'
        read_only_fields = ('invited_by', 'invitation_token', 'status', 'accepted_at')
    
    def create(self, validated_data):
        import uuid
        from datetime import timedelta
        from django.utils import timezone
        
        validated_data['invited_by'] = self.context['request'].user
        validated_data['invitation_token'] = uuid.uuid4().hex
        validated_data['expires_at'] = timezone.now() + timedelta(days=7)
        return super().create(validated_data)


class StaffCategorySerializer(serializers.ModelSerializer):
    """Serializer for Staff Category"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffCategory
        fields = '__all__'
    
    def get_staff_count(self, obj):
        return obj.staff_members.count()


class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for Staff Member"""
    user_details = UserProfileSerializer(source='user', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = StaffMember
        fields = '__all__'


class DutyScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Duty Schedule"""
    staff_name = serializers.CharField(source='staff_member.user.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = DutySchedule
        fields = '__all__'
        read_only_fields = ('assigned_by',)
    
    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission"""
    
    class Meta:
        model = Permission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for Role Permission"""
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = '__all__'


class UserRoleTransitionSerializer(serializers.ModelSerializer):
    """Serializer for User Role Transition"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserRoleTransition
        fields = '__all__'
        read_only_fields = ('requested_by', 'approved_by', 'processed_at')
    
    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class SocietySettingsSerializer(serializers.ModelSerializer):
    """Serializer for Society Settings"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = SocietySettings
        fields = '__all__'


class FeeStructureSerializer(serializers.ModelSerializer):
    """Serializer for Fee Structure"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    total_fee = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeStructure
        fields = '__all__'
    
    def get_total_fee(self, obj):
        return obj.maintenance_amount + obj.parking_fee + obj.amenity_fee


class BulkUserOperationSerializer(serializers.ModelSerializer):
    """Serializer for Bulk User Operation"""
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkUserOperation
        fields = '__all__'
        read_only_fields = ('initiated_by', 'completed_at')
    
    def get_progress_percentage(self, obj):
        if obj.total_records == 0:
            return 0
        processed = obj.successful_records + obj.failed_records
        return round((processed / obj.total_records) * 100, 2)
    
    def create(self, validated_data):
        validated_data['initiated_by'] = self.context['request'].user
        return super().create(validated_data)


class AdminSocietySerializer(serializers.ModelSerializer):
    """Serializer for Admin Society relationship"""
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = AdminSociety
        fields = '__all__'


class EnhancedUserProfileSerializer(serializers.ModelSerializer):
    """Enhanced User profile serializer with more details"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    managed_societies = AdminSocietySerializer(many=True, read_only=True)
    staff_profile = StaffMemberSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'first_name', 'last_name', 
                 'profile_picture', 'role', 'society', 'society_name', 
                 'is_active', 'is_approved', 'approved_by_name', 'approval_date',
                 'date_joined', 'last_login', 'managed_societies', 'staff_profile')
        read_only_fields = ('id', 'date_joined', 'last_login', 'approved_by_name', 'approval_date')


# Bulk operations serializers
class BulkUserImportSerializer(serializers.Serializer):
    """Serializer for bulk user import"""
    file = serializers.FileField()
    society = serializers.PrimaryKeyRelatedField(queryset=Society.objects.all())  # type: ignore
    default_role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='MEMBER')
    send_welcome_email = serializers.BooleanField(default=True)


class BulkUserUpdateSerializer(serializers.Serializer):
    """Serializer for bulk user updates"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    updates = serializers.DictField(child=serializers.CharField(), allow_empty=False)
    
    def validate_updates(self, value):
        allowed_fields = ['role', 'is_active', 'is_approved', 'society']
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(f"Field '{field}' is not allowed for bulk update")
        return value