from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Role, PermissionChangeLog

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    content_type_name = serializers.StringRelatedField(source='content_type')
    
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type', 'content_type_name')
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    child_roles = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permissions', 'permission_count',
                  'parent', 'parent_name', 'child_roles', 'user_count',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'permission_count', 'user_count')
    
    def get_child_roles(self, obj):
        """Return list of child role names"""
        return [{'id': role.id, 'name': role.name} for role in obj.children.all()]
    
    def get_permission_count(self, obj):
        """Return the count of direct permissions (not including inherited)"""
        return obj.permissions.count()
    
    def get_user_count(self, obj):
        """Return the count of users with this role"""
        return obj.users.count()
    
    def validate_parent(self, value):
        """Validate that a role cannot be its own parent or create circular references"""
        if value and value.id == self.instance.id if self.instance else False:
            raise serializers.ValidationError("A role cannot be its own parent.")
        
        # Check for circular references
        if value:
            parent = value
            while parent:
                if parent.parent and parent.parent.id == self.instance.id if self.instance else False:
                    raise serializers.ValidationError("This would create a circular reference in the role hierarchy.")
                parent = parent.parent
        
        return value


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 
                  'role', 'role_name', 'is_active', 'bio', 'profile_image',
                  'date_joined', 'last_login')
        read_only_fields = ('is_active', 'date_joined', 'last_login')
    
    def validate_email(self, value):
        """Validate email format"""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check if email is unique
        if User.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
            
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 
                  'password_confirm', 'role', 'bio', 'profile_image')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email format"""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check if email is unique
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
            
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update a user, correctly handling the password."""
        # Remove the password fields from validated_data if they exist
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Update the user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle password separately
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class PermissionChangeLogSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True)
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionChangeLog
        fields = ('id', 'role', 'role_name', 'permission', 'permission_name', 
                  'action', 'changed_by', 'changed_by_email', 'changed_by_name', 'changed_at')
        read_only_fields = ('changed_at',)
    
    def get_changed_by_name(self, obj):
        """Get the full name of the user who changed the permission"""
        return obj.changed_by.get_full_name() if obj.changed_by else None 