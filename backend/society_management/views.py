from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import *
from .serializers import *


# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        # Generate registration OTP for testing purposes
        otp = OTP.create_otp(
            phone_number=user.phone_number,  # type: ignore
            purpose='REGISTRATION',
            user=user,
            email=user.email  # type: ignore
        )
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'otp_info': {
                'otp_code': otp.otp_code,  # For testing only
                'purpose': 'REGISTRATION',
                'expires_at': otp.expires_at,
                'note': 'OTP shown for testing purposes only'
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_with_password(request):
    """User login with phone number and password"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  # type: ignore
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_with_otp_step1(request):
    """Step 1: Send OTP to phone number for login"""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({'error': 'Phone number is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone_number=phone_number)  # type: ignore
        if not user.is_active:
            return Response({'error': 'Account is disabled'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Create OTP for login
        otp = OTP.create_otp(
            phone_number=phone_number,
            purpose='LOGIN',
            user=user,
            email=user.email
        )
        
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'otp_code': otp.otp_code,  # For testing only
            'expires_at': otp.expires_at,
            'note': 'OTP shown for testing purposes only'
        })
        
    except User.DoesNotExist:  # type: ignore
        return Response({'error': 'No user found with this phone number'}, 
                       status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_with_otp_step2(request):
    """Step 2: Verify OTP and complete login"""
    serializer = OTPLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  # type: ignore
        otp = serializer.validated_data['otp']  # type: ignore
        
        # Mark OTP as used
        otp.mark_as_used()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Legacy login endpoint (for backward compatibility)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Legacy login endpoint with OTP generation"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  # type: ignore
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        # Generate login OTP for testing purposes
        otp = OTP.create_otp(
            phone_number=user.phone_number,  # type: ignore
            purpose='LOGIN',
            user=user,
            email=user.email  # type: ignore
        )
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'otp_info': {
                'otp_code': otp.otp_code,  # For testing only
                'purpose': 'LOGIN',
                'expires_at': otp.expires_at,
                'note': 'OTP shown for testing purposes only'
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


# OTP Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """Initiate forgot password process by sending OTP"""
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']  # type: ignore
        
        try:
            user = User.objects.get(phone_number=phone_number)  # type: ignore
            
            # Create OTP
            otp = OTP.create_otp(
                phone_number=phone_number,
                purpose='FORGOT_PASSWORD',
                user=user,
                email=user.email
            )
            
            # In production, you would send SMS/Email here
            # For testing purposes, we're returning the OTP in response
            return Response({
                'message': 'OTP sent successfully',
                'phone_number': phone_number,
                'otp_code': otp.otp_code,  # For testing only
                'expires_at': otp.expires_at,
                'note': 'OTP shown for testing purposes only'
            })
            
        except User.DoesNotExist:  # type: ignore
            return Response({'error': 'No user found with this phone number'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify OTP for any purpose"""
    serializer = OTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        otp = serializer.validated_data['otp']  # type: ignore
        
        return Response({
            'message': 'OTP verified successfully',
            'phone_number': otp.phone_number,
            'purpose': otp.purpose,
            'verified_at': otp.verified_at
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Reset password using OTP verification"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  # type: ignore
        otp = serializer.validated_data['otp']  # type: ignore
        new_password = serializer.validated_data['new_password']  # type: ignore
        
        # Mark OTP as used
        otp.mark_as_used()
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Generate new tokens
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        return Response({
            'message': 'Password reset successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    """Send OTP for various purposes (registration, login, etc.)"""
    phone_number = request.data.get('phone_number')
    purpose = request.data.get('purpose', 'LOGIN')
    
    if not phone_number:
        return Response({'error': 'Phone number is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate purpose
    valid_purposes = ['FORGOT_PASSWORD', 'REGISTRATION', 'LOGIN', 'PHONE_VERIFICATION']
    if purpose not in valid_purposes:
        return Response({'error': f'Invalid purpose. Must be one of: {valid_purposes}'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # For registration, user might not exist yet
    user = None
    if purpose != 'REGISTRATION':
        try:
            user = User.objects.get(phone_number=phone_number)  # type: ignore
        except User.DoesNotExist:  # type: ignore
            return Response({'error': 'No user found with this phone number'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    # Create OTP
    otp = OTP.create_otp(
        phone_number=phone_number,
        purpose=purpose,
        user=user
    )
    
    # In production, you would send SMS/Email here
    # For testing purposes, we're returning the OTP in response
    return Response({
        'message': 'OTP sent successfully',
        'phone_number': phone_number,
        'purpose': purpose,
        'otp_code': otp.otp_code,  # For testing only
        'expires_at': otp.expires_at,
        'note': 'OTP shown for testing purposes only'
    })


# SUB_ADMIN Invitation Flow
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_subadmin_invitation(request):
    """ADMIN creates invitation for SUB_ADMIN"""
    # Check if user is ADMIN
    if request.user.role != 'ADMIN':
        return Response({'error': 'Only ADMIN can create SUB_ADMIN invitations'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = SubAdminInvitationSerializer(data=request.data)
    if serializer.is_valid():
        invitation = serializer.save(invited_by=request.user)
        
        # Send OTP to invited phone number
        otp = OTP.create_otp(
            phone_number=invitation.phone_number,  # type: ignore
            purpose='REGISTRATION',
            email=invitation.email  # type: ignore
        )
        
        return Response({
            'message': 'SUB_ADMIN invitation created successfully',
            'invitation': SubAdminInvitationSerializer(invitation).data,
            'otp_info': {
                'otp_code': otp.otp_code,  # For testing only
                'purpose': 'REGISTRATION',
                'expires_at': otp.expires_at,
                'note': 'OTP sent to invited phone number for registration'
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_invitation_otp(request):
    """Step 1: Verify OTP for SUB_ADMIN invitation"""
    serializer = InvitationOTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        invitation = serializer.validated_data['invitation']  # type: ignore
        otp = serializer.validated_data['otp']  # type: ignore
        
        # Mark OTP as used
        otp.mark_as_used()
        
        # Mark invitation as OTP verified
        invitation.otp_verified = True
        invitation.save()
        
        return Response({
            'message': 'OTP verified successfully. Please complete registration.',
            'invitation_id': invitation.id,
            'phone_number': invitation.phone_number,
            'society': invitation.society.name,
            'next_step': 'Complete registration with password and details'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def complete_subadmin_registration(request):
    """Step 2: Complete SUB_ADMIN registration with details and password"""
    serializer = CompleteSubAdminRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        invitation = serializer.validated_data['invitation']  # type: ignore
        
        # Create SUB_ADMIN user
        user = User.objects.create_user(
            phone_number=invitation.phone_number,
            email=invitation.email,
            first_name=serializer.validated_data['first_name'],  # type: ignore
            last_name=serializer.validated_data['last_name'],  # type: ignore
            password=serializer.validated_data['password'],  # type: ignore
            role='SUB_ADMIN',
            society=invitation.society,
            is_approved=True,
            approved_by=invitation.invited_by,
            approval_date=timezone.now()
        )
        
        # Mark invitation as completed
        invitation.status = 'ACCEPTED'
        invitation.accepted_at = timezone.now()
        invitation.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)  # type: ignore
        
        return Response({
            'message': 'SUB_ADMIN registration completed successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'society': SocietySerializer(invitation.society).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_subadmin_invitations(request):
    """List SUB_ADMIN invitations (ADMIN only)"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Only ADMIN can view invitations'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    invitations = SubAdminInvitation.objects.filter(invited_by=request.user)  # type: ignore
    serializer = SubAdminInvitationSerializer(invitations, many=True)
    return Response(serializer.data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# Core ViewSets
class SocietyViewSet(viewsets.ModelViewSet):
    """ViewSet for Society model"""
    queryset = Society.objects.all()  # type: ignore
    serializer_class = SocietySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'state']
    search_fields = ['name', 'city']


class FlatViewSet(viewsets.ModelViewSet):
    """ViewSet for Flat model"""
    queryset = Flat.objects.all()  # type: ignore
    serializer_class = FlatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society', 'block_number', 'type']
    search_fields = ['flat_number', 'block_number']


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model"""
    queryset = Vehicle.objects.all()  # type: ignore
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner', 'flat', 'type']
    search_fields = ['vehicle_number']


# Billing ViewSets
class MaintenanceBillViewSet(viewsets.ModelViewSet):
    """ViewSet for MaintenanceBill model"""
    queryset = MaintenanceBill.objects.all()  # type: ignore
    serializer_class = MaintenanceBillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flat', 'status', 'payment_mode']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            return MaintenanceBill.objects.all()  # type: ignore
        # Members can only see their own bills
        return MaintenanceBill.objects.filter(  # type: ignore
            models.Q(flat__owner=user) | models.Q(flat__tenant=user)
        )


class CommonExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for CommonExpense model"""
    queryset = CommonExpense.objects.all()  # type: ignore
    serializer_class = CommonExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society', 'created_by']
    search_fields = ['title']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def split_expense(self, request, pk=None):
        """Split the expense among all flats"""
        expense = self.get_object()
        expense.split_expense()
        return Response({'message': 'Expense split successfully'})


class CommonExpenseSplitViewSet(viewsets.ModelViewSet):
    """ViewSet for CommonExpenseSplit model"""
    queryset = CommonExpenseSplit.objects.all()  # type: ignore
    serializer_class = CommonExpenseSplitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['common_expense', 'flat', 'status']


# Community ViewSets
class NoticeViewSet(viewsets.ModelViewSet):
    """ViewSet for Notice model"""
    queryset = Notice.objects.all()  # type: ignore
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society', 'posted_by']
    search_fields = ['title', 'content']
    ordering = ['-created_at']


class AmenityViewSet(viewsets.ModelViewSet):
    """ViewSet for Amenity model"""
    queryset = Amenity.objects.all()  # type: ignore
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society']
    search_fields = ['name']


class AmenityBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for AmenityBooking model"""
    queryset = AmenityBooking.objects.all()  # type: ignore
    serializer_class = AmenityBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['amenity', 'status', 'booked_by']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            return AmenityBooking.objects.all()  # type: ignore
        return AmenityBooking.objects.filter(booked_by=user)  # type: ignore


# Security ViewSets
class VisitorLogViewSet(viewsets.ModelViewSet):
    """ViewSet for VisitorLog model"""
    queryset = VisitorLog.objects.all()  # type: ignore
    serializer_class = VisitorLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flat_to_visit', 'status']
    search_fields = ['name', 'phone_number']
    ordering = ['-created_at']


class ComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for Complaint model"""
    queryset = Complaint.objects.all()  # type: ignore
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flat', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            return Complaint.objects.all()  # type: ignore
        elif user.role == 'STAFF':
            return Complaint.objects.filter(assigned_to=user)  # type: ignore
        return Complaint.objects.filter(raised_by=user)  # type: ignore


# Marketplace ViewSets
class MarketplaceListingViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketplaceListing model"""
    queryset = MarketplaceListing.objects.all()  # type: ignore
    serializer_class = MarketplaceListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'posted_by']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            return MarketplaceListing.objects.all()  # type: ignore
        # Members can see active listings and their own listings
        return MarketplaceListing.objects.filter(  # type: ignore
            models.Q(status='ACTIVE') | models.Q(posted_by=user)
        )


class JobListingViewSet(viewsets.ModelViewSet):
    """ViewSet for JobListing model"""
    queryset = JobListing.objects.all()  # type: ignore
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'posted_by']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            return JobListing.objects.all()  # type: ignore
        # Members can see active listings and their own listings
        return JobListing.objects.filter(  # type: ignore
            models.Q(status='ACTIVE') | models.Q(posted_by=user)
        )


class AdBannerViewSet(viewsets.ModelViewSet):
    """ViewSet for AdBanner model"""
    queryset = AdBanner.objects.all()  # type: ignore
    serializer_class = AdBannerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['placement_location', 'is_active']


# ===== NEW VIEWS FOR ENHANCED SOCIETY MANAGEMENT =====

# Admin → Sub-Admin (Chairman) Management
class ChairmanInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for Chairman Invitations"""
    queryset = ChairmanInvitation.objects.all()  # type: ignore
    serializer_class = ChairmanInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society', 'status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            # Admins can see invitations for their managed societies
            managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
            return ChairmanInvitation.objects.filter(  # type: ignore
                models.Q(invited_by=user) | models.Q(society_id__in=managed_society_ids)
            )
        return ChairmanInvitation.objects.none()  # type: ignore
    
    @action(detail=True, methods=['post'])
    def accept_invitation(self, request, pk=None):
        """Accept chairman invitation and create sub-admin user"""
        invitation = self.get_object()
        
        if invitation.status != 'PENDING':
            return Response({'error': 'Invitation is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new user as sub-admin
        user_data = {
            'phone_number': invitation.phone_number,
            'email': invitation.email,
            'first_name': invitation.first_name,
            'last_name': invitation.last_name,
            'role': 'SUB_ADMIN',
            'society': invitation.society,
            'is_approved': True,
            'approved_by': invitation.invited_by
        }
        
        try:
            # Create user with temporary password
            temp_password = f"temp_{invitation.phone_number[-4:]}"
            user = User.objects.create_user(  # type: ignore
                password=temp_password,
                **user_data
            )
            
            invitation.status = 'ACCEPTED'
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            return Response({
                'message': 'Invitation accepted successfully',
                'user_id': user.id,
                'temp_password': temp_password
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject_invitation(self, request, pk=None):
        """Reject chairman invitation"""
        invitation = self.get_object()
        invitation.status = 'REJECTED'
        invitation.save()
        return Response({'message': 'Invitation rejected'})


# Staff Management
class StaffCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Staff Categories"""
    queryset = StaffCategory.objects.all()  # type: ignore
    serializer_class = StaffCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            if user.role == 'ADMIN':
                managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
                return StaffCategory.objects.filter(society_id__in=managed_society_ids)  # type: ignore
            else:
                return StaffCategory.objects.filter(society=user.society)  # type: ignore
        return StaffCategory.objects.none()  # type: ignore


class StaffMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for Staff Members"""
    queryset = StaffMember.objects.all()  # type: ignore
    serializer_class = StaffMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            if user.role == 'ADMIN':
                managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
                return StaffMember.objects.filter(category__society_id__in=managed_society_ids)  # type: ignore
            else:
                return StaffMember.objects.filter(category__society=user.society)  # type: ignore
        elif user.role == 'STAFF':
            return StaffMember.objects.filter(user=user)  # type: ignore
        return StaffMember.objects.none()  # type: ignore
    
    @action(detail=False, methods=['post'])
    def create_staff_user(self, request):
        """Create a new staff member with user account"""
        user_data = {
            'phone_number': request.data.get('phone_number'),
            'email': request.data.get('email'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'role': 'STAFF',
            'society_id': request.data.get('society_id')
        }
        
        staff_data = {
            'staff_id': request.data.get('staff_id'),
            'category_id': request.data.get('category_id'),
            'join_date': request.data.get('join_date'),
            'salary': request.data.get('salary'),
            'shift_start_time': request.data.get('shift_start_time'),
            'shift_end_time': request.data.get('shift_end_time'),
            'emergency_contact': request.data.get('emergency_contact'),
            'address': request.data.get('address')
        }
        
        try:
            # Create user
            temp_password = f"staff_{user_data['phone_number'][-4:]}"
            user = User.objects.create_user(  # type: ignore
                password=temp_password,
                **user_data
            )
            
            # Create staff profile
            staff_data['user'] = user
            staff_member = StaffMember.objects.create(**staff_data)  # type: ignore
            
            return Response({
                'message': 'Staff member created successfully',
                'staff_id': staff_member.id,
                'user_id': user.id,
                'temp_password': temp_password
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DutyScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for Duty Schedules"""
    queryset = DutySchedule.objects.all()  # type: ignore
    serializer_class = DutyScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['staff_member', 'date', 'status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'SUB_ADMIN']:
            if user.role == 'ADMIN':
                managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
                return DutySchedule.objects.filter(  # type: ignore
                    staff_member__category__society_id__in=managed_society_ids
                )
            else:
                return DutySchedule.objects.filter(  # type: ignore
                    staff_member__category__society=user.society
                )
        elif user.role == 'STAFF':
            try:
                staff_member = user.staff_profile  # type: ignore
                return DutySchedule.objects.filter(staff_member=staff_member)  # type: ignore
            except StaffMember.DoesNotExist:  # type: ignore
                return DutySchedule.objects.none()  # type: ignore
        return DutySchedule.objects.none()  # type: ignore
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark duty as completed"""
        duty = self.get_object()
        duty.status = 'COMPLETED'
        duty.completed_at = timezone.now()
        duty.notes = request.data.get('notes', '')
        duty.save()
        return Response({'message': 'Duty marked as completed'})


# Permission Management
class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Permissions"""
    queryset = Permission.objects.all()  # type: ignore
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Permission.objects.all()  # type: ignore
        return Permission.objects.filter(is_active=True)  # type: ignore


class RolePermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Role Permissions"""
    queryset = RolePermission.objects.all()  # type: ignore
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'society', 'permission']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
            return RolePermission.objects.filter(  # type: ignore
                models.Q(society_id__in=managed_society_ids) | models.Q(society__isnull=True)
            )
        elif user.role == 'SUB_ADMIN':
            return RolePermission.objects.filter(  # type: ignore
                models.Q(society=user.society) | models.Q(society__isnull=True)
            )
        return RolePermission.objects.none()  # type: ignore


# User Management
class UserRoleTransitionViewSet(viewsets.ModelViewSet):
    """ViewSet for User Role Transitions"""
    queryset = UserRoleTransition.objects.all()  # type: ignore
    serializer_class = UserRoleTransitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'status', 'from_role', 'to_role']
    
    @action(detail=True, methods=['post'])
    def approve_transition(self, request, pk=None):
        """Approve role transition"""
        transition = self.get_object()
        
        if transition.status != 'PENDING':
            return Response({'error': 'Transition is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user role
        user = transition.user
        user.role = transition.to_role
        user.save()
        
        # Update transition
        transition.status = 'APPROVED'
        transition.approved_by = request.user
        transition.processed_at = timezone.now()
        transition.save()
        
        return Response({'message': 'Role transition approved successfully'})
    
    @action(detail=True, methods=['post'])
    def reject_transition(self, request, pk=None):
        """Reject role transition"""
        transition = self.get_object()
        transition.status = 'REJECTED'
        transition.approved_by = request.user
        transition.processed_at = timezone.now()
        transition.save()
        
        return Response({'message': 'Role transition rejected'})


# Society Settings
class SocietySettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for Society Settings"""
    queryset = SocietySettings.objects.all()  # type: ignore
    serializer_class = SocietySettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
            return SocietySettings.objects.filter(society_id__in=managed_society_ids)  # type: ignore
        elif user.role == 'SUB_ADMIN':
            return SocietySettings.objects.filter(society=user.society)  # type: ignore
        return SocietySettings.objects.none()  # type: ignore


class FeeStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for Fee Structures"""
    queryset = FeeStructure.objects.all()  # type: ignore
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['society', 'flat_type', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
            return FeeStructure.objects.filter(society_id__in=managed_society_ids)  # type: ignore
        elif user.role in ['SUB_ADMIN', 'MEMBER']:
            return FeeStructure.objects.filter(society=user.society)  # type: ignore
        return FeeStructure.objects.none()  # type: ignore


# Bulk Operations
class BulkUserOperationViewSet(viewsets.ModelViewSet):
    """ViewSet for Bulk User Operations"""
    queryset = BulkUserOperation.objects.all()  # type: ignore
    serializer_class = BulkUserOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['operation_type', 'status', 'society']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            managed_society_ids = user.managed_societies.values_list('society_id', flat=True)  # type: ignore
            return BulkUserOperation.objects.filter(society_id__in=managed_society_ids)  # type: ignore
        elif user.role == 'SUB_ADMIN':
            return BulkUserOperation.objects.filter(society=user.society)  # type: ignore
        return BulkUserOperation.objects.none()  # type: ignore


class AdminSocietyViewSet(viewsets.ModelViewSet):
    """ViewSet for Admin Society relationships"""
    queryset = AdminSociety.objects.all()  # type: ignore
    serializer_class = AdminSocietySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['admin', 'society', 'is_primary']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return AdminSociety.objects.filter(admin=user)  # type: ignore
        return AdminSociety.objects.none()  # type: ignore


# Enhanced User Management Views
@api_view(['POST'])
def bulk_user_import(request):
    """Import users in bulk from CSV/Excel file"""
    serializer = BulkUserImportSerializer(data=request.data)
    if serializer.is_valid():
        # Process file and create bulk operation record
        operation = BulkUserOperation.objects.create(  # type: ignore
            operation_type='IMPORT',
            initiated_by=request.user,
            society=serializer.validated_data['society'],  # type: ignore
            status='PROCESSING'
        )
        
        # TODO: Implement async file processing
        return Response({
            'message': 'Import process started',
            'operation_id': operation.id
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bulk_user_update(request):
    """Update multiple users at once"""
    serializer = BulkUserUpdateSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']  # type: ignore
        updates = serializer.validated_data['updates']  # type: ignore
        
        # Update users
        updated_count = User.objects.filter(id__in=user_ids).update(**updates)  # type: ignore
        
        return Response({
            'message': f'Successfully updated {updated_count} users',
            'updated_count': updated_count
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_dashboard_stats(request):
    """Get dashboard statistics for different user roles"""
    user = request.user
    stats = {}
    
    if user.role == 'ADMIN':
        managed_societies = user.managed_societies.all()  # type: ignore
        stats = {
            'total_societies': managed_societies.count(),
            'total_users': User.objects.filter(  # type: ignore
                society_id__in=managed_societies.values_list('society_id', flat=True)
            ).count(),
            'pending_invitations': ChairmanInvitation.objects.filter(  # type: ignore
                invited_by=user, status='PENDING'
            ).count(),
            'total_complaints': Complaint.objects.filter(  # type: ignore
                flat__society_id__in=managed_societies.values_list('society_id', flat=True)
            ).count()
        }
    
    elif user.role == 'SUB_ADMIN':
        stats = {
            'total_members': User.objects.filter(society=user.society, role='MEMBER').count(),  # type: ignore
            'total_staff': User.objects.filter(society=user.society, role='STAFF').count(),  # type: ignore
            'pending_complaints': Complaint.objects.filter(  # type: ignore
                flat__society=user.society, status='OPEN'
            ).count(),
            'total_flats': Flat.objects.filter(society=user.society).count()  # type: ignore
        }
    
    elif user.role == 'MEMBER':
        user_flats = Flat.objects.filter(  # type: ignore
            models.Q(owner=user) | models.Q(tenant=user)
        )
        stats = {
            'my_flats': user_flats.count(),
            'pending_bills': MaintenanceBill.objects.filter(  # type: ignore
                flat__in=user_flats, status='PENDING'
            ).count(),
            'my_complaints': Complaint.objects.filter(raised_by=user).count(),  # type: ignore
            'my_bookings': AmenityBooking.objects.filter(booked_by=user).count()  # type: ignore
        }
    
    elif user.role == 'STAFF':
        try:
            staff_member = user.staff_profile  # type: ignore
            today = timezone.now().date()
            stats = {
                'today_duties': DutySchedule.objects.filter(  # type: ignore
                    staff_member=staff_member, date=today
                ).count(),
                'pending_duties': DutySchedule.objects.filter(  # type: ignore
                    staff_member=staff_member, status='SCHEDULED'
                ).count(),
                'assigned_complaints': Complaint.objects.filter(  # type: ignore
                    assigned_to=user, status__in=['OPEN', 'IN_PROGRESS']
                ).count()
            }
        except StaffMember.DoesNotExist:  # type: ignore
            stats = {'error': 'Staff profile not found'}
    
    return Response(stats)
