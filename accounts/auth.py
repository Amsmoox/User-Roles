from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

User = get_user_model()


class AuthRateThrottle(AnonRateThrottle):
    """Rate throttle for authentication attempts."""
    rate = '5/minute'


class PasswordResetRateThrottle(AnonRateThrottle):
    """Rate throttle for password reset attempts."""
    rate = '3/hour'


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 
                  'password', 'password_confirm')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(_("Enter a valid email address."))
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError(
                {"password_confirm": _("Password fields didn't match.")}
            )
        return attrs
    
    def create(self, validated_data):
        """Create a new user with validated data."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(read_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('Account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that the email exists in the system."""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(_("Enter a valid email address."))
        
        if not User.objects.filter(email=value).exists():
            # For security reasons, don't reveal if a user doesn't exist
            # Just silently continue
            pass
        
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate token and passwords."""
        # Check if passwords match
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password_confirm": _("Password fields didn't match.")}
            )
        
        # Check if the token is valid
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"uid": _("Invalid user ID.")}
            )
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError(
                {"token": _("Invalid or expired token.")}
            )
        
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password when logged in."""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_current_password(self, value):
        """Validate that the current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Current password is incorrect."))
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password_confirm": _("Password fields didn't match.")}
            )
        return attrs


class RegisterView(APIView):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    @transaction.atomic
    def post(self, request):
        """Process registration request."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Send welcome email
            try:
                self._send_welcome_email(user)
            except Exception as e:
                # Log the error but continue
                print(f"Failed to send welcome email: {str(e)}")
            
            return Response({
                "user": serializer.data,
                "token": token.key,
                "message": _("User registered successfully")
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_welcome_email(self, user):
        """Send welcome email to newly registered user."""
        subject = _('Welcome to our platform')
        message = render_to_string('accounts/emails/welcome_email.txt', {'user': user})
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class LoginView(APIView):
    """API endpoint for user login."""
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    def post(self, request):
        """Process login request."""
        serializer = LoginSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Record login IP if available
        if hasattr(user, 'last_login_ip') and request.META.get('REMOTE_ADDR'):
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save(update_fields=['last_login_ip'])
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })


class LogoutView(APIView):
    """API endpoint for user logout."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process logout request."""
        # Delete the user's token to logout
        Token.objects.filter(user=request.user).delete()
        return Response({"message": _("Successfully logged out.")})


class PasswordResetRequestView(APIView):
    """API endpoint to request a password reset."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    
    def post(self, request):
        """Process password reset request."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        # Find user by email
        users = User.objects.filter(email=email)
        
        if users.exists():
            user = users.first()
            self._send_password_reset_email(user)
        
        # Always return the same response regardless of whether the email exists
        # This is for security purposes
        return Response({
            "message": _("Password reset email has been sent if the email is registered.")
        })
    
    def _send_password_reset_email(self, user):
        """Send password reset email with token."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Reset link would direct to frontend with these parameters
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        subject = _('Password Reset Request')
        message = render_to_string('accounts/emails/password_reset_email.txt', {
            'user': user,
            'reset_url': reset_url,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class PasswordResetConfirmView(APIView):
    """API endpoint to confirm password reset."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    
    @transaction.atomic
    def post(self, request):
        """Process password reset confirmation."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        
        # Set the new password
        user.set_password(new_password)
        user.save()
        
        # Invalidate all existing tokens
        Token.objects.filter(user=user).delete()
        
        return Response({
            "message": _("Password has been reset successfully.")
        })


class PasswordChangeView(APIView):
    """API endpoint to change password when logged in."""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Process password change request."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        # Set the new password
        user.set_password(new_password)
        user.save()
        
        # Invalidate all existing tokens except current one
        current_token = Token.objects.get(user=user)
        Token.objects.filter(user=user).exclude(key=current_token.key).delete()
        
        return Response({
            "message": _("Password has been changed successfully.")
        }) 