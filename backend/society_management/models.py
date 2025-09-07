from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from decimal import Decimal
import random
import string
from datetime import timedelta
import uuid


class CustomUserManager(UserManager):
    """Custom user manager for phone number authentication"""
    
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        # Handle both username and phone_number parameters for compatibility
        phone_number = extra_fields.pop('phone_number', username)
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        
        # Remove username from extra_fields if it exists to avoid duplication
        extra_fields.pop('username', None)
        
        user = self.model(phone_number=phone_number, email=email, username=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        # Handle both username and phone_number parameters for compatibility
        phone_number = extra_fields.pop('phone_number', username)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username=phone_number, email=email, password=password, **extra_fields)


class User(AbstractUser):
    """Stores all users of the platform (Admins, Sub-Admins, Members, Staff)"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('SUB_ADMIN', 'Sub Admin'),
        ('MEMBER', 'Member'),
        ('STAFF', 'Staff'),
    ]
    
    OWNERSHIP_TYPE_CHOICES = [
        ('OWNER', 'Owner'),
        ('TENANT', 'Tenant'),
    ]
    
    phone_number = models.CharField(max_length=20, unique=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True, help_text="URL/path to image")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    society = models.ForeignKey('Society', on_delete=models.CASCADE, null=True, blank=True)
    
    # Enhanced member fields
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPE_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    aadhaar_number = models.CharField(max_length=12, null=True, blank=True, unique=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    
    # New fields for enhanced functionality
    is_approved = models.BooleanField(default=True, help_text="Whether user is approved by admin")  # type: ignore
    approved_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users')
    approval_date = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Override username to make it optional
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)
    
    def has_permission(self, permission_code, society=None):
        """Check if user has a specific permission"""
        try:
            permission = Permission.objects.get(code=permission_code)  # type: ignore
            role_permission = RolePermission.objects.filter(  # type: ignore
                role=self.role,
                permission=permission,
                society=society or self.society
            ).first()
            return role_permission is not None
        except Permission.DoesNotExist:  # type: ignore
            return False


class OTP(models.Model):
    """Model to store OTPs for authentication purposes"""
    
    PURPOSE_CHOICES = [
        ('FORGOT_PASSWORD', 'Forgot Password'),
        ('REGISTRATION', 'Registration'),
        ('LOGIN', 'Login'),
        ('PHONE_VERIFICATION', 'Phone Verification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps', null=True, blank=True)
    phone_number = models.CharField(max_length=20)  # For cases where user doesn't exist yet
    email = models.EmailField(null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)  # type: ignore
    is_expired = models.BooleanField(default=False)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP {self.otp_code} for {self.phone_number} ({self.purpose})"
    
    def save(self, *args, **kwargs):
        # Set expiry time if not set (default 10 minutes)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        
        # Generate OTP if not set
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP of specified length"""
        return ''.join(random.choices(string.digits, k=length))
    
    def is_valid(self):
        """Check if OTP is valid (not used, not expired, and within time limit)"""
        return (
            not self.is_used and 
            not self.is_expired and 
            timezone.now() <= self.expires_at
        )
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.verified_at = timezone.now()
        self.save()
    
    def mark_as_expired(self):
        """Mark OTP as expired"""
        self.is_expired = True
        self.save()
    
    @classmethod
    def create_otp(cls, phone_number, purpose, user=None, email=None):
        """Create a new OTP for the given phone number and purpose"""
        # Mark any existing OTPs for this phone/purpose as expired
        cls.objects.filter(  # type: ignore
            phone_number=phone_number,
            purpose=purpose,
            is_used=False,
            is_expired=False
        ).update(is_expired=True)
        
        # Create new OTP
        otp = cls.objects.create(  # type: ignore
            user=user,
            phone_number=phone_number,
            email=email,
            purpose=purpose
        )
        
        return otp
    
    @classmethod
    def verify_otp(cls, phone_number, otp_code, purpose):
        """Verify OTP and return the OTP instance if valid"""
        try:
            otp = cls.objects.get(  # type: ignore
                phone_number=phone_number,
                otp_code=otp_code,
                purpose=purpose,
                is_used=False,
                is_expired=False
            )
            
            if otp.is_valid():
                otp.mark_as_used()
                return otp
            else:
                otp.mark_as_expired()
                return None
        except cls.DoesNotExist:  # type: ignore
            return None


class AdminSociety(models.Model):
    """Many-to-many relationship for admins managing multiple societies"""
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_societies')
    society = models.ForeignKey('Society', on_delete=models.CASCADE, related_name='admins')
    is_primary = models.BooleanField(default=False, help_text="Primary society for this admin")  # type: ignore
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['admin', 'society']
    
    def __str__(self):
        return f"{self.admin.get_full_name()} manages {self.society.name}"  # type: ignore


class SubAdminInvitation(models.Model):
    """Model for SUB_ADMIN invitations from ADMIN"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subadmin_invitations_sent')
    society = models.ForeignKey('Society', on_delete=models.CASCADE, related_name='subadmin_invitations')
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    otp_verified = models.BooleanField(default=False)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['society', 'phone_number']
    
    def __str__(self):
        return f"Invitation for {self.phone_number} to {self.society.name}"
    
    def save(self, *args, **kwargs):
        # Set expiry time if not set (default 7 days)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if invitation is still valid"""
        return (
            self.status == 'PENDING' and
            timezone.now() <= self.expires_at
        )
    
    def mark_expired(self):
        """Mark invitation as expired"""
        self.status = 'EXPIRED'
        self.save()


class Society(models.Model):
    """Represents a single residential society"""
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Societies"
    
    def __str__(self) -> str:
        return str(self.name)


class Flat(models.Model):
    """Represents an individual unit (flat/apartment) within a society"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='flats')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_flats')
    tenant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_flats')
    block_number = models.CharField(max_length=20, help_text='e.g., "A", "Wing-C"')
    flat_number = models.CharField(max_length=20, help_text='e.g., "101", "G-504"')
    type = models.CharField(max_length=50, help_text='e.g., "2BHK", "3BHK"')
    area_sqft = models.IntegerField(null=True, blank=True)
    
    # Link to enhanced flat for detailed information
    enhanced_flat = models.OneToOneField('EnhancedFlat', on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_flat')
    
    class Meta:
        unique_together = ['society', 'block_number', 'flat_number']
    
    def __str__(self):
        return f"{self.society.name} - {self.block_number}/{self.flat_number}"


class Vehicle(models.Model):
    """Stores vehicle details for members"""
    
    VEHICLE_TYPES = [
        ('CAR', 'Car'),
        ('BIKE', 'Bike'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    
    def __str__(self):
        return f"{self.vehicle_number} ({self.owner.first_name})"  # type: ignore


class MaintenanceBill(models.Model):
    """Records individual monthly maintenance bills for each flat"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    ]
    
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='maintenance_bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.flat} - {self.billing_period_start} to {self.billing_period_end}"


class CommonExpense(models.Model):
    """Stores shared expenses like festival costs"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='common_expenses')
    title = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses')
    invoice_attachment = models.CharField(max_length=255, null=True, blank=True, help_text="URL/path to invoice file")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.society.name} - {self.title}"
    
    def split_expense(self):
        """Split the expense among all flats in the society"""
        flats = self.society.flats.all()  # type: ignore
        if flats.exists():
            amount_per_flat = self.total_amount / flats.count()
            for flat in flats:
                CommonExpenseSplit.objects.get_or_create(  # type: ignore
                    common_expense=self,
                    flat=flat,
                    defaults={'amount_due': amount_per_flat}
                )


class CommonExpenseSplit(models.Model):
    """Links a common expense to each flat and tracks its payment status"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]
    
    common_expense = models.ForeignKey(CommonExpense, on_delete=models.CASCADE, related_name='splits')
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='expense_splits')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    paid_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['common_expense', 'flat']
    
    def __str__(self):
        return f"{self.common_expense.title} - {self.flat}"  # type: ignore


class Notice(models.Model):
    """For global and society-specific announcements"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notices')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, null=True, blank=True, related_name='notices', help_text="Null for global notices")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.title)


class Amenity(models.Model):
    """Lists the bookable amenities in a society"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100, help_text='e.g., "Clubhouse"')
    booking_rules = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return f"{self.society.name} - {self.name}"


class AmenityBooking(models.Model):
    """Records booking requests from members"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amenity_bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.amenity.name} - {self.booked_by.first_name} ({self.status})"  # type: ignore


class VisitorLog(models.Model):
    """Tracks all visitors entering the society"""
    
    STATUS_CHOICES = [
        ('PRE_APPROVED', 'Pre-approved'),
        ('ENTERED', 'Entered'),
        ('EXITED', 'Exited'),
    ]
    
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    flat_to_visit = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='visitors')
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRE_APPROVED')
    pass_code = models.CharField(max_length=10, unique=True, help_text="for pinless entry")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} visiting {self.flat_to_visit}"


class Complaint(models.Model):
    """For raising and tracking service requests or complaints"""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]
    
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints', help_text="Staff member")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.raised_by.first_name}"  # type: ignore


class MarketplaceListing(models.Model):
    """For members to list businesses, offers, etc."""
    
    STATUS_CHOICES = [
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_APPROVAL')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.title)


class JobListing(models.Model):
    """For job vacancies posted by members"""
    
    STATUS_CHOICES = [
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_APPROVAL')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.title)


class AdBanner(models.Model):
    """Stores advertisement details"""
    
    PLACEMENT_CHOICES = [
        ('HOME_TOP', 'Home Top'),
        ('MARKETPLACE_BANNER', 'Marketplace Banner'),
    ]
    
    title = models.CharField(max_length=255, help_text="For internal reference")
    image_url = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, help_text="URL to redirect on click")
    placement_location = models.CharField(max_length=50, choices=PLACEMENT_CHOICES)
    is_active = models.BooleanField(default=True)  # type: ignore
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self) -> str:
        return str(self.title)


# ===== NEW MODELS FOR ENHANCED SOCIETY MANAGEMENT =====

class ChairmanInvitation(models.Model):
    """Handles invitations for chairman/sub-admin positions"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='chairman_invitations')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    invitation_token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Chairman invitation for {self.first_name} {self.last_name} - {self.society.name}"


class StaffCategory(models.Model):
    """Categories of staff members"""
    
    name = models.CharField(max_length=100)  # Security, Cleaning, Maintenance, etc.
    description = models.TextField(blank=True)
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='staff_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Staff Categories"
        unique_together = ['name', 'society']
    
    def __str__(self):
        return f"{self.society.name} - {self.name}"


class StaffMember(models.Model):
    """Extended staff information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(StaffCategory, on_delete=models.CASCADE, related_name='staff_members')
    join_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    is_active = models.BooleanField(default=True)  # type: ignore
    emergency_contact = models.CharField(max_length=20)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_id}"  # type: ignore  # type: ignore


class DutySchedule(models.Model):
    """Staff duty scheduling and shift management"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('MISSED', 'Missed'),
        ('PARTIAL', 'Partially Completed'),
    ]
    
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='duty_schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    task_description = models.TextField()
    location = models.CharField(max_length=255, help_text="Specific location within society")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_duties')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['staff_member', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.date} {self.start_time}"  # type: ignore  # type: ignore


class Permission(models.Model):
    """Custom permissions for granular access control"""
    
    CATEGORY_CHOICES = [
        ('USER_MANAGEMENT', 'User Management'),
        ('BILLING', 'Billing & Payments'),
        ('COMMUNITY', 'Community Features'),
        ('SECURITY', 'Security & Visitors'),
        ('MAINTENANCE', 'Maintenance & Complaints'),
        ('SOCIETY_SETTINGS', 'Society Settings'),
        ('REPORTS', 'Reports & Analytics'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)  # type: ignore
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class RolePermission(models.Model):
    """Links roles to permissions with society-specific access"""
    
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    society = models.ForeignKey(Society, on_delete=models.CASCADE, null=True, blank=True)
    can_create = models.BooleanField(default=False)  # type: ignore
    can_read = models.BooleanField(default=True)  # type: ignore
    can_update = models.BooleanField(default=False)  # type: ignore
    can_delete = models.BooleanField(default=False)  # type: ignore
    
    class Meta:
        unique_together = ['role', 'permission', 'society']
    
    def __str__(self):
        society_name = self.society.name if self.society else "Global"
        return f"{self.role} - {self.permission.name} ({society_name})"


class UserRoleTransition(models.Model):
    """Tracks role changes for users"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_transitions')
    from_role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    to_role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_transitions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transitions')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}: {self.from_role} → {self.to_role}"  # type: ignore


class SocietySettings(models.Model):
    """Society-specific configurations and settings"""
    
    society = models.OneToOneField(Society, on_delete=models.CASCADE, related_name='settings')
    
    # Billing Settings
    default_maintenance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_due_day = models.IntegerField(default=5, help_text="Day of month when maintenance is due")  # type: ignore
    late_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    
    # Community Settings
    allow_marketplace = models.BooleanField(default=True)  # type: ignore
    allow_job_postings = models.BooleanField(default=True)  # type: ignore
    auto_approve_bookings = models.BooleanField(default=False)  # type: ignore
    
    # Security Settings
    visitor_approval_required = models.BooleanField(default=True)  # type: ignore
    max_visitor_duration_hours = models.IntegerField(default=24)  # type: ignore
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)  # type: ignore
    sms_notifications = models.BooleanField(default=False)  # type: ignore
    
    # Other Settings
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='18:00')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.society.name}"


class FeeStructure(models.Model):
    """Different fee structures for different flat types"""
    
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='fee_structures')
    flat_type = models.CharField(max_length=50, help_text='e.g., 1BHK, 2BHK, 3BHK')
    maintenance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    parking_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    amenity_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['society', 'flat_type']
    
    def __str__(self):
        return f"{self.society.name} - {self.flat_type}: ₹{self.maintenance_amount}"


class BulkUserOperation(models.Model):
    """Tracks bulk operations on users"""
    
    OPERATION_CHOICES = [
        ('IMPORT', 'Import Users'),
        ('EXPORT', 'Export Users'),
        ('BULK_UPDATE', 'Bulk Update'),
        ('BULK_DELETE', 'Bulk Delete'),
        ('ROLE_CHANGE', 'Bulk Role Change'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    operation_type = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_operations')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='bulk_operations')
    file_path = models.CharField(max_length=500, blank=True)
    total_records = models.IntegerField(default=0)  # type: ignore
    successful_records = models.IntegerField(default=0)  # type: ignore
    failed_records = models.IntegerField(default=0)  # type: ignore
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.operation_type} - {self.society.name} ({self.status})"


# ===== ENHANCED MODELS FOR COMPREHENSIVE SOCIETY MANAGEMENT =====

# Building and Flat Management
class Building(models.Model):
    """Represents a building within a society"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=100, help_text='e.g., "Block A", "Tower 1"')
    description = models.TextField(blank=True)
    total_floors = models.IntegerField()
    flats_per_floor = models.IntegerField()
    amenities = models.TextField(blank=True, help_text='Building-specific amenities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['society', 'name']
    
    def __str__(self):
        return f"{self.society.name} - {self.name}"


class EnhancedFlat(models.Model):
    """Enhanced flat model with more details"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='enhanced_flats')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='flats')
    floor_number = models.IntegerField()
    flat_number = models.CharField(max_length=20)
    flat_type = models.CharField(max_length=50, help_text='e.g., "1BHK", "2BHK", "3BHK"')
    carpet_area = models.FloatField(help_text='Area in sq ft')
    balcony_area = models.FloatField(default=0.0, help_text='Balcony area in sq ft')  # type: ignore
    parking_slots = models.IntegerField(default=0)  # type: ignore
    is_available = models.BooleanField(default=True)  # type: ignore
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    possession_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['building', 'floor_number', 'flat_number']
    
    def __str__(self):
        return f"{self.building.name} - Floor {self.floor_number} - {self.flat_number}"


# Member Registration and Management
class MemberRegistrationRequest(models.Model):
    """Handles self-registration requests from prospective members"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    OWNERSHIP_TYPE_CHOICES = [
        ('OWNER', 'Owner'),
        ('TENANT', 'Tenant'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    
    # Property Information
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='member_requests')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='member_requests')
    flat = models.ForeignKey(EnhancedFlat, on_delete=models.CASCADE, related_name='member_requests')
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPE_CHOICES)
    
    # Additional Information
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    permanent_address = models.TextField()
    id_proof_number = models.CharField(max_length=50, help_text='Aadhaar/PAN/Passport number')
    
    # Request Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True)
    documents_uploaded = models.JSONField(default=list, help_text='List of document URLs')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.society.name} ({self.status})"
    
    def approve_request(self, reviewer):
        """Approve the registration request and create user"""
        if self.status == 'PENDING':
            # Create user account
            user = User.objects.create_user(
                phone_number=self.phone_number,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                role='MEMBER',
                society=self.society,
                ownership_type=self.ownership_type,
                date_of_birth=self.date_of_birth,
                occupation=self.occupation,
                emergency_contact_name=self.emergency_contact_name,
                emergency_contact_phone=self.emergency_contact_phone,
                permanent_address=self.permanent_address,
                is_approved=True,
                approved_by=reviewer,
                approval_date=timezone.now()
            )
            
            # Update request status
            self.status = 'APPROVED'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.save()
            
            # Assign flat
            flat_instance = self.flat
            if self.ownership_type == 'OWNER':
                flat_instance.owner = user  # type: ignore
            else:
                flat_instance.tenant = user  # type: ignore
            flat_instance.is_available = False  # type: ignore
            flat_instance.save()  # type: ignore
            
            return user
        return None


class MemberInvitation(models.Model):
    """SUB_ADMIN can invite new members directly"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_invitations_sent')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='member_invitations')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='member_invitations')
    flat = models.ForeignKey(EnhancedFlat, on_delete=models.CASCADE, related_name='member_invitations')
    
    # Invitee Information
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    ownership_type = models.CharField(max_length=20, choices=MemberRegistrationRequest.OWNERSHIP_TYPE_CHOICES)
    
    # Invitation Management
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Invitation for {self.first_name} {self.last_name} to {self.society.name}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)


# Staff Management
class StaffInvitation(models.Model):
    """SUB_ADMIN can invite staff members"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_invitations_sent')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='staff_invitations')
    category = models.ForeignKey(StaffCategory, on_delete=models.CASCADE, related_name='staff_invitations')
    
    # Invitee Information
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    # Staff Details
    staff_id = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    
    # Invitation Management
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Staff invitation for {self.first_name} {self.last_name} - {self.designation}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)


# Society Profile Management
class SocietyProfile(models.Model):
    """Extended society profile with comprehensive information"""
    society = models.OneToOneField(Society, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Information
    established_year = models.IntegerField(null=True, blank=True)
    total_units = models.IntegerField(default=0)  # type: ignore
    society_logo = models.CharField(max_length=255, null=True, blank=True, help_text='URL/path to logo')
    society_type = models.CharField(max_length=50, default='Residential')
    
    # Amenities
    amenities_list = models.JSONField(default=list, help_text='List of society amenities')
    
    # Rules and Regulations
    society_rules = models.TextField(blank=True)
    visitor_policy = models.TextField(blank=True)
    pet_policy = models.TextField(blank=True)
    parking_rules = models.TextField(blank=True)
    noise_policy = models.TextField(blank=True)
    
    # Contact Information
    office_timings = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    social_media_links = models.JSONField(default=dict, help_text='Social media links')
    
    # Legal Information
    registration_authority = models.CharField(max_length=100, blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.society.name}"


# Helpdesk Management
class HelpdeskDesignation(models.Model):
    """Designations for helpdesk contacts"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='helpdesk_designations')
    title = models.CharField(max_length=100, help_text='e.g., Electrician, Plumber, Manager')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, help_text='e.g., Maintenance, Emergency, Administrative')
    is_active = models.BooleanField(default=True)  # type: ignore
    
    class Meta:
        unique_together = ['society', 'title']
    
    def __str__(self):
        return f"{self.society.name} - {self.title}"


class HelpdeskContact(models.Model):
    """Helpdesk contacts for society services"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='helpdesk_contacts')
    designation = models.ForeignKey(HelpdeskDesignation, on_delete=models.CASCADE, related_name='contacts')
    
    # Contact Information
    name = models.CharField(max_length=100)
    primary_phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Additional Information
    photo = models.CharField(max_length=255, null=True, blank=True, help_text='URL/path to photo')
    availability = models.CharField(max_length=100, blank=True, help_text='Available hours')
    service_charges = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)  # type: ignore
    
    # Status
    is_active = models.BooleanField(default=True)  # type: ignore
    is_verified = models.BooleanField(default=False)  # type: ignore
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_helpdesk_contacts')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.designation.title}"  # type: ignore


# Enhanced Billing System
class BillType(models.Model):
    """Types of bills that can be created"""
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='bill_types')
    name = models.CharField(max_length=100, help_text='e.g., Maintenance, Water, Electricity')
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)  # type: ignore
    recurrence_period = models.CharField(max_length=20, null=True, blank=True, help_text='monthly, quarterly, yearly')
    is_splitable = models.BooleanField(default=False)  # type: ignore
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # type: ignore
    
    class Meta:
        unique_together = ['society', 'name']
    
    def __str__(self):
        return f"{self.society.name} - {self.name}"


class EnhancedBill(models.Model):
    """Enhanced billing system with attachments and recurring bills"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('ONLINE', 'Online'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('UPI', 'UPI'),
    ]
    
    # Basic Information
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='enhanced_bills')
    bill_type = models.ForeignKey(BillType, on_delete=models.CASCADE, related_name='bills')
    bill_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Financial Information
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Information
    payment_details = models.JSONField(default=dict, help_text='Bank account info, UPI ID, etc.')
    due_date = models.DateField()
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Attachments
    attachments = models.JSONField(default=list, help_text='List of attachment URLs')
    
    # Recurring Information
    is_recurring = models.BooleanField(default=False)  # type: ignore
    parent_bill = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_bills')
    next_due_date = models.DateField(null=True, blank=True)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Payment Tracking
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paid_bills')
    
    def __str__(self):
        return f"{self.bill_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate unique bill number
            prefix = self.society.name[:3].upper()
            count = EnhancedBill.objects.filter(society=self.society).count() + 1  # type: ignore
            self.bill_number = f"{prefix}{count:06d}"
        
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount + self.late_fee  # type: ignore
        
        super().save(*args, **kwargs)


class BillDistribution(models.Model):
    """For splitable bills - distribution among flats"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    bill = models.ForeignKey(EnhancedBill, on_delete=models.CASCADE, related_name='distributions')
    flat = models.ForeignKey(EnhancedFlat, on_delete=models.CASCADE, related_name='bill_distributions')
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateTimeField(null=True, blank=True)
    payment_mode = models.CharField(max_length=20, choices=EnhancedBill.PAYMENT_MODE_CHOICES, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        unique_together = ['bill', 'flat']
    
    def __str__(self):
        return f"{self.bill.title} - {self.flat}"  # type: ignore


# Security and Gate Management
class VisitorPass(models.Model):
    """Digital visitor passes created by SUB_ADMIN"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('USED', 'Used'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Pass Information
    pass_number = models.CharField(max_length=20, unique=True)
    qr_code = models.CharField(max_length=255, null=True, blank=True, help_text='QR code data')
    
    # Visitor Information
    visitor_name = models.CharField(max_length=255)
    visitor_phone = models.CharField(max_length=20)
    visitor_id_proof = models.CharField(max_length=100, blank=True)
    purpose_of_visit = models.CharField(max_length=255)
    
    # Visit Details
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='visitor_passes')
    flat_to_visit = models.ForeignKey(EnhancedFlat, on_delete=models.CASCADE, related_name='visitor_passes')
    expected_entry_time = models.DateTimeField()
    expected_exit_time = models.DateTimeField(null=True, blank=True)
    
    # Reference Information
    referenced_by = models.CharField(max_length=255, help_text='Name of person who referred')
    reference_phone = models.CharField(max_length=20, blank=True)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_visitor_passes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Actual Visit Tracking
    actual_entry_time = models.DateTimeField(null=True, blank=True)
    actual_exit_time = models.DateTimeField(null=True, blank=True)
    gate_entry_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_visitors')
    gate_exit_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_out_visitors')
    
    def __str__(self):
        return f"{self.pass_number} - {self.visitor_name}"
    
    def save(self, *args, **kwargs):
        if not self.pass_number:
            # Generate unique pass number
            date_part = timezone.now().strftime('%Y%m%d')
            count = VisitorPass.objects.filter(created_at__date=timezone.now().date()).count() + 1  # type: ignore
            self.pass_number = f"VP{date_part}{count:04d}"
        super().save(*args, **kwargs)


class GateUpdateLog(models.Model):
    """Real-time log of all gate updates by security staff"""
    
    UPDATE_TYPE_CHOICES = [
        ('VISITOR_ENTRY', 'Visitor Entry'),
        ('VISITOR_EXIT', 'Visitor Exit'),
        ('VEHICLE_ENTRY', 'Vehicle Entry'),
        ('VEHICLE_EXIT', 'Vehicle Exit'),
        ('STAFF_ENTRY', 'Staff Entry'),
        ('STAFF_EXIT', 'Staff Exit'),
        ('DENIED_ENTRY', 'Denied Entry'),
        ('EMERGENCY', 'Emergency'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='gate_logs')
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES)
    
    # Entry Information
    person_name = models.CharField(max_length=255, blank=True)
    person_phone = models.CharField(max_length=20, blank=True)
    id_proof_number = models.CharField(max_length=100, blank=True)
    
    # Vehicle Information (if applicable)
    vehicle_number = models.CharField(max_length=20, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True)
    
    # Visit Information
    flat_number = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    visitor_pass = models.ForeignKey(VisitorPass, on_delete=models.SET_NULL, null=True, blank=True, related_name='gate_logs')
    
    # Gate Information
    gate_number = models.CharField(max_length=10, default='1')
    entry_method = models.CharField(max_length=50, blank=True, help_text='Manual, QR Scan, etc.')
    
    # Staff Information
    logged_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gate_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # Status
    is_approved = models.BooleanField(default=True)  # type: ignore
    approval_required = models.BooleanField(default=False)  # type: ignore
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_gate_logs')
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.update_type} - {self.person_name or 'Unknown'} at {self.timestamp}"


# Member and Staff Directory
class DirectoryEntry(models.Model):
    """Directory entry for members and staff with search capabilities"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='directory_entry')
    
    # Display Information
    display_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Contact Visibility
    show_phone = models.BooleanField(default=True)  # type: ignore
    show_email = models.BooleanField(default=True)  # type: ignore
    show_address = models.BooleanField(default=False)  # type: ignore
    
    # Additional Information
    interests = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    
    # Social Links
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Status
    is_visible = models.BooleanField(default=True)  # type: ignore
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Directory: {self.display_name}"
    
    def get_flat_numbers(self):
        """Get list of flat numbers associated with this user"""
        owned_flats = EnhancedFlat.objects.filter(owner=self.user).values_list('flat_number', flat=True)  # type: ignore
        rented_flats = EnhancedFlat.objects.filter(tenant=self.user).values_list('flat_number', flat=True)  # type: ignore
        return list(set(list(owned_flats) + list(rented_flats)))
