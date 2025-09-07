from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Society, Flat, Vehicle, MaintenanceBill, CommonExpense, 
    CommonExpenseSplit, Notice, Amenity, AmenityBooking, VisitorLog, 
    Complaint, MarketplaceListing, JobListing, AdBanner, ChairmanInvitation,
    StaffCategory, StaffMember, DutySchedule, Permission, RolePermission,
    UserRoleTransition, SocietySettings, FeeStructure, BulkUserOperation,
    AdminSociety, OTP, SubAdminInvitation, Building, EnhancedFlat,
    MemberRegistrationRequest, MemberInvitation, StaffInvitation,
    SocietyProfile, HelpdeskDesignation, HelpdeskContact, BillType,
    EnhancedBill, BillDistribution, VisitorPass, GateUpdateLog,
    DirectoryEntry
)


# Secure Admin Creation Serializers (Superuser Only)
class AdminCreationSerializer(serializers.ModelSerializer):
    """Serializer for creating ADMIN users - Only superusers can use this"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():  # type: ignore
            raise serializers.ValidationError('User with this phone number already exists')
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # SECURITY: Force role to ADMIN
        validated_data['role'] = 'ADMIN'
        validated_data['is_approved'] = True
        validated_data['is_staff'] = True  # Allow Django admin access
        validated_data['is_superuser'] = True  # Give superuser privileges
        user = User.objects.create_user(**validated_data)
        return user


class StaffUserCreationSerializer(serializers.ModelSerializer):
    """Serializer for creating STAFF users - Only SUB_ADMIN and ADMIN can use this"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():  # type: ignore
            raise serializers.ValidationError('User with this phone number already exists')
        return value
    
    def create(self, validated_data):
        from django.utils import timezone
        validated_data.pop('password_confirm')
        # SECURITY: Force role to STAFF
        validated_data['role'] = 'STAFF'
        validated_data['is_approved'] = True
        validated_data['society'] = self.context['request'].user.society
        validated_data['approved_by'] = self.context['request'].user
        validated_data['approval_date'] = timezone.now()
        user = User.objects.create_user(**validated_data)
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():  # type: ignore
            raise serializers.ValidationError('User with this phone number already exists')
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # SECURITY: Force role to MEMBER for public registration
        validated_data['role'] = 'MEMBER'
        # SECURITY: Set is_approved to False for manual approval
        validated_data['is_approved'] = False
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
            
            # Check if member is approved (skip for ADMIN/SUB_ADMIN/STAFF)
            if user.role == 'MEMBER' and not user.is_approved:
                # Get SUB_ADMIN/Chairman contact info for the society
                chairman_info = self._get_chairman_contact(user.society)
                error_message = f"Your account is pending approval. Please contact your society's chairman: {chairman_info}"
                raise serializers.ValidationError(error_message)
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include phone number and password')
        
        return attrs
    
    def _get_chairman_contact(self, society):
        """Get SUB_ADMIN/Chairman contact information for the society"""
        if society:
            try:
                # Find SUB_ADMIN for this society
                chairman = User.objects.filter(
                    role='SUB_ADMIN', 
                    society=society, 
                    is_active=True, 
                    is_approved=True
                ).first()
                
                if chairman:
                    return f"{chairman.get_full_name()} ({chairman.phone_number})"
                else:
                    return "Society Administrator (Contact details not available)"
            except Exception:
                return "Society Administrator"
        return "Society Administrator"


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
            
            # Check if member is approved (skip for ADMIN/SUB_ADMIN/STAFF)
            if user.role == 'MEMBER' and not user.is_approved:
                # Get SUB_ADMIN/Chairman contact info for the society
                chairman_info = self._get_chairman_contact(user.society)
                error_message = f"Your account is pending approval. Please contact your society's chairman: {chairman_info}"
                raise serializers.ValidationError(error_message)
            
            attrs['user'] = user
        except User.DoesNotExist:  # type: ignore
            raise serializers.ValidationError('User not found')
        
        attrs['otp'] = otp
        return attrs
    
    def _get_chairman_contact(self, society):
        """Get SUB_ADMIN/Chairman contact information for the society"""
        if society:
            try:
                # Find SUB_ADMIN for this society
                chairman = User.objects.filter(
                    role='SUB_ADMIN', 
                    society=society, 
                    is_active=True, 
                    is_approved=True
                ).first()
                
                if chairman:
                    return f"{chairman.get_full_name()} ({chairman.phone_number})"
                else:
                    return "Society Administrator (Contact details not available)"
            except Exception:
                return "Society Administrator"
        return "Society Administrator"


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


# ===== ENHANCED SERIALIZERS FOR COMPREHENSIVE SOCIETY MANAGEMENT =====

# Building and Flat Management Serializers
class BuildingSerializer(serializers.ModelSerializer):
    """Serializer for Building model"""
    total_flats = serializers.SerializerMethodField()
    available_flats = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def get_total_flats(self, obj):
        return obj.flats.count()
    
    def get_available_flats(self, obj):
        return obj.flats.filter(is_available=True).count()


class EnhancedFlatSerializer(serializers.ModelSerializer):
    """Serializer for EnhancedFlat model"""
    building_name = serializers.CharField(source='building.name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    owner_name = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EnhancedFlat
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def get_owner_name(self, obj):
        if hasattr(obj, 'legacy_flat') and obj.legacy_flat and obj.legacy_flat.owner:
            return obj.legacy_flat.owner.get_full_name()
        return None
    
    def get_tenant_name(self, obj):
        if hasattr(obj, 'legacy_flat') and obj.legacy_flat and obj.legacy_flat.tenant:
            return obj.legacy_flat.tenant.get_full_name()
        return None


# Member Registration Serializers
class MemberRegistrationRequestSerializer(serializers.ModelSerializer):
    """Serializer for member self-registration requests"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = MemberRegistrationRequest
        fields = '__all__'
        read_only_fields = ('requested_at', 'reviewed_by', 'reviewed_at', 'society_name', 
                           'building_name', 'flat_details', 'reviewed_by_name')
    
    def validate(self, attrs):
        # Check if flat is available
        flat = attrs.get('flat')
        ownership_type = attrs.get('ownership_type')
        
        if flat and not flat.is_available:
            raise serializers.ValidationError("Selected flat is not available")
        
        # Check if phone number is already registered
        phone_number = attrs.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        
        return attrs


class MemberInvitationSerializer(serializers.ModelSerializer):
    """Serializer for member invitations"""
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    
    class Meta:
        model = MemberInvitation
        fields = '__all__'
        read_only_fields = ('invited_by', 'invitation_token', 'created_at', 'expires_at',
                           'invited_by_name', 'society_name', 'building_name', 'flat_details')
    
    def create(self, validated_data):
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)


class SocietySearchSerializer(serializers.Serializer):
    """Serializer for society search by address"""
    search_query = serializers.CharField(max_length=255, help_text='Search by address, city, or society name')


class SocietyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for society list in search results"""
    full_address = serializers.SerializerMethodField()
    total_flats = serializers.SerializerMethodField()
    available_flats = serializers.SerializerMethodField()
    
    class Meta:
        model = Society
        fields = ('id', 'name', 'full_address', 'city', 'state', 'pincode', 
                 'total_flats', 'available_flats')
    
    def get_full_address(self, obj):
        return f"{obj.address}, {obj.city}, {obj.state} - {obj.pincode}"
    
    def get_total_flats(self, obj):
        return obj.enhanced_flats.count()
    
    def get_available_flats(self, obj):
        return obj.enhanced_flats.filter(is_available=True).count()


# Staff Management Serializers
class StaffInvitationSerializer(serializers.ModelSerializer):
    """Serializer for staff invitations"""
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    society_name = serializers.CharField(source='society.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = StaffInvitation
        fields = '__all__'
        read_only_fields = ('invited_by', 'invitation_token', 'created_at', 'expires_at',
                           'invited_by_name', 'society_name', 'category_name')
    
    def create(self, validated_data):
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)


# Society Profile Management Serializers
class SocietyProfileSerializer(serializers.ModelSerializer):
    """Serializer for extended society profile"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    
    class Meta:
        model = SocietyProfile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'society_name')


# Helpdesk Management Serializers
class HelpdeskDesignationSerializer(serializers.ModelSerializer):
    """Serializer for helpdesk designations"""
    contacts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HelpdeskDesignation
        fields = '__all__'
    
    def get_contacts_count(self, obj):
        return obj.contacts.filter(is_active=True).count()


class HelpdeskContactSerializer(serializers.ModelSerializer):
    """Serializer for helpdesk contacts"""
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    designation_category = serializers.CharField(source='designation.category', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = HelpdeskContact
        fields = '__all__'
        read_only_fields = ('added_by', 'added_at', 'designation_title', 
                           'designation_category', 'added_by_name')
    
    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)


# Enhanced Billing Serializers
class BillTypeSerializer(serializers.ModelSerializer):
    """Serializer for bill types"""
    bills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BillType
        fields = '__all__'
    
    def get_bills_count(self, obj):
        return obj.bills.count()


class EnhancedBillSerializer(serializers.ModelSerializer):
    """Serializer for enhanced bills"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    bill_type_name = serializers.CharField(source='bill_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    paid_by_name = serializers.CharField(source='paid_by.get_full_name', read_only=True)
    
    class Meta:
        model = EnhancedBill
        fields = '__all__'
        read_only_fields = ('bill_number', 'total_amount', 'created_by', 'created_at', 
                           'updated_at', 'society_name', 'bill_type_name', 
                           'created_by_name', 'paid_by_name')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BillDistributionSerializer(serializers.ModelSerializer):
    """Serializer for bill distributions"""
    bill_title = serializers.CharField(source='bill.title', read_only=True)
    flat_details = serializers.CharField(source='flat.__str__', read_only=True)
    
    class Meta:
        model = BillDistribution
        fields = '__all__'
        read_only_fields = ('bill_title', 'flat_details')


class BillSplitSerializer(serializers.Serializer):
    """Serializer for splitting bills among flats"""
    bill_id = serializers.IntegerField()
    split_equally = serializers.BooleanField(default=True)
    custom_allocations = serializers.JSONField(required=False, help_text='Custom allocation per flat')
    
    def validate_bill_id(self, value):
        try:
            bill = EnhancedBill.objects.get(id=value)  # type: ignore
            if not bill.bill_type.is_splitable:
                raise serializers.ValidationError("This bill type is not splitable")
            return value
        except EnhancedBill.DoesNotExist:  # type: ignore
            raise serializers.ValidationError("Bill not found")


# Security and Gate Management Serializers
class VisitorPassSerializer(serializers.ModelSerializer):
    """Serializer for visitor passes"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    flat_details = serializers.CharField(source='flat_to_visit.__str__', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    gate_entry_staff_name = serializers.CharField(source='gate_entry_staff.get_full_name', read_only=True)
    gate_exit_staff_name = serializers.CharField(source='gate_exit_staff.get_full_name', read_only=True)
    
    class Meta:
        model = VisitorPass
        fields = '__all__'
        read_only_fields = ('pass_number', 'qr_code', 'created_by', 'created_at',
                           'society_name', 'flat_details', 'created_by_name',
                           'gate_entry_staff_name', 'gate_exit_staff_name')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class GateUpdateLogSerializer(serializers.ModelSerializer):
    """Serializer for gate update logs"""
    society_name = serializers.CharField(source='society.name', read_only=True)
    logged_by_name = serializers.CharField(source='logged_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    visitor_pass_number = serializers.CharField(source='visitor_pass.pass_number', read_only=True)
    
    class Meta:
        model = GateUpdateLog
        fields = '__all__'
        read_only_fields = ('logged_by', 'timestamp', 'society_name', 'logged_by_name',
                           'approved_by_name', 'visitor_pass_number')
    
    def create(self, validated_data):
        validated_data['logged_by'] = self.context['request'].user
        return super().create(validated_data)


# Directory Management Serializers
class DirectoryEntrySerializer(serializers.ModelSerializer):
    """Serializer for directory entries"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    society_name = serializers.CharField(source='user.society.name', read_only=True)
    flat_numbers = serializers.SerializerMethodField()
    profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)
    
    class Meta:
        model = DirectoryEntry
        fields = '__all__'
        read_only_fields = ('user', 'last_updated', 'user_name', 'user_phone', 
                           'user_email', 'user_role', 'society_name', 'flat_numbers',
                           'profile_picture')
    
    def get_flat_numbers(self, obj):
        return obj.get_flat_numbers()


class DirectorySearchSerializer(serializers.Serializer):
    """Serializer for directory search"""
    search_query = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    building = serializers.CharField(max_length=100, required=False)
    flat_number = serializers.CharField(max_length=20, required=False)
    designation = serializers.CharField(max_length=100, required=False)


# Member Approval Serializers
class MemberApprovalSerializer(serializers.Serializer):
    """Serializer for approving/rejecting member registration requests"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comments = serializers.CharField(max_length=500, required=False)
    assign_flat = serializers.BooleanField(default=True)
    
    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('comments'):
            raise serializers.ValidationError("Comments are required for rejection")
        return attrs


# Direct Member Addition Serializers
class DirectMemberAdditionSerializer(serializers.ModelSerializer):
    """Serializer for SUB_ADMIN to directly add members"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'password', 
                 'password_confirm', 'ownership_type', 'date_of_birth', 'occupation',
                 'emergency_contact_name', 'emergency_contact_phone', 'permanent_address')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        from django.utils import timezone
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Get society from the request user
        society = self.context['request'].user.society
        
        user = User.objects.create_user(
            **validated_data,
            role='MEMBER',
            society=society,
            is_approved=True,
            approved_by=self.context['request'].user,
            approval_date=timezone.now()
        )
        user.set_password(password)
        user.save()
        
        return user


# Staff Direct Addition Serializer
class DirectStaffAdditionSerializer(serializers.Serializer):
    """Serializer for SUB_ADMIN to directly add staff"""
    # User Information
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    # Staff Information
    category = serializers.PrimaryKeyRelatedField(queryset=StaffCategory.objects.all())  # type: ignore
    staff_id = serializers.CharField(max_length=50)
    designation = serializers.CharField(max_length=100)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    shift_start_time = serializers.TimeField()
    shift_end_time = serializers.TimeField()
    emergency_contact = serializers.CharField(max_length=20)
    address = serializers.CharField()
    join_date = serializers.DateField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if staff_id is unique
        if StaffMember.objects.filter(staff_id=attrs['staff_id']).exists():  # type: ignore
            raise serializers.ValidationError("Staff ID already exists")
        
        return attrs
    
    def create(self, validated_data):
        from django.utils import timezone
        password_confirm = validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Extract staff data
        staff_data = {
            'category': validated_data.pop('category'),
            'staff_id': validated_data.pop('staff_id'),
            'designation': validated_data.pop('designation'),
            'salary': validated_data.pop('salary', None),
            'shift_start_time': validated_data.pop('shift_start_time'),
            'shift_end_time': validated_data.pop('shift_end_time'),
            'emergency_contact': validated_data.pop('emergency_contact'),
            'address': validated_data.pop('address'),
            'join_date': validated_data.pop('join_date'),
        }
        
        # Get society from the request user
        society = self.context['request'].user.society
        
        # Create user
        user = User.objects.create_user(
            **validated_data,
            role='STAFF',
            society=society,
            is_approved=True,
            approved_by=self.context['request'].user,
            approval_date=timezone.now()
        )
        user.set_password(password)
        user.save()
        
        # Create staff profile
        staff_member = StaffMember.objects.create(  # type: ignore
            user=user,
            **staff_data
        )
        
        return {'user': user, 'staff_member': staff_member}


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