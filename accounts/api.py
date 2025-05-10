from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .models import Role, PermissionChangeLog
from .serializers import (
    UserSerializer, UserCreateSerializer, RoleSerializer,
    PermissionSerializer, PermissionChangeLogSerializer
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only access to any authenticated user, but only admins can modify."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class UserRateThrottleBasic(UserRateThrottle):
    """Throttle for authenticated users."""
    rate = '60/minute'


class AnonRateThrottleBasic(AnonRateThrottle):
    """Throttle for anonymous users."""
    rate = '20/minute'


class UserViewSet(viewsets.ModelViewSet):
    """API endpoints for managing users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']
    throttle_classes = [UserRateThrottleBasic, AnonRateThrottleBasic]

    def get_queryset(self):
        """Optimize query to include role"""
        return super().get_queryset().select_related('role')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's details."""
        # Use cache to avoid repeated DB queries for the same user
        cache_key = f'user_profile_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
            
        serializer = self.get_serializer(request.user)
        cache.set(cache_key, serializer.data, timeout=300)  # Cache for 5 minutes
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "user activated"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a user account."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": _("You cannot deactivate your own account.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return Response({"status": "user deactivated"})
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def bulk_create(self, request):
        """Create multiple users at once."""
        users_data = request.data
        if not isinstance(users_data, list):
            return Response(
                {"detail": _("Expected a list of users")},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        created_users = []
        errors = []
        
        with transaction.atomic():
            for index, user_data in enumerate(users_data):
                serializer = UserCreateSerializer(data=user_data)
                try:
                    if serializer.is_valid(raise_exception=True):
                        user = serializer.save()
                        created_users.append(UserSerializer(user).data)
                except ValidationError as e:
                    errors.append({
                        "index": index,
                        "data": user_data,
                        "errors": str(e)
                    })
                except Exception as e:
                    errors.append({
                        "index": index,
                        "data": user_data,
                        "errors": str(e)
                    })
        
        if errors and not created_users:
            return Response(
                {"detail": _("All user creations failed"), "errors": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "created": len(created_users),
            "failed": len(errors),
            "users": created_users,
            "errors": errors
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)


class RoleViewSet(viewsets.ModelViewSet):
    """API endpoints for managing roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    throttle_classes = [UserRateThrottleBasic]

    def get_queryset(self):
        """Optimize query with parent and prefetch permissions"""
        return super().get_queryset().select_related('parent').prefetch_related('permissions', 'children')

    def perform_create(self, serializer):
        """Save the role with the current user as creator."""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Save the role with the current user as updater."""
        serializer.save(updated_by=self.request.user)

    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def add_permissions(self, request, pk=None):
        """Add permissions to a role."""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        if not permission_ids:
            return Response(
                {"detail": _("No permission IDs provided")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permissions_to_add = Permission.objects.filter(id__in=permission_ids)
        if not permissions_to_add:
            return Response(
                {"detail": _("No valid permissions found")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log permission changes
        for permission in permissions_to_add:
            PermissionChangeLog.objects.create(
                role=role,
                permission=permission,
                action='add',
                changed_by=request.user
            )
            
        # Add permissions to role
        role.permissions.add(*permissions_to_add)
        
        # Clear the permission cache for this role
        cache.delete(f'role_permissions_{role.id}')
        
        # Clear cache for all users with this role
        for user in User.objects.filter(role=role):
            cache.delete(f'user_permissions_{user.pk}')
            cache.delete(f'user_role_permissions_{user.pk}')
        
        serializer = self.get_serializer(role)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def remove_permissions(self, request, pk=None):
        """Remove permissions from a role."""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        if not permission_ids:
            return Response(
                {"detail": _("No permission IDs provided")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permissions_to_remove = Permission.objects.filter(id__in=permission_ids)
        if not permissions_to_remove:
            return Response(
                {"detail": _("No valid permissions found")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log permission changes
        for permission in permissions_to_remove:
            PermissionChangeLog.objects.create(
                role=role,
                permission=permission,
                action='remove',
                changed_by=request.user
            )
            
        # Remove permissions from role
        role.permissions.remove(*permissions_to_remove)
        
        # Clear the permission cache for this role
        cache.delete(f'role_permissions_{role.id}')
        
        # Clear cache for all users with this role
        for user in User.objects.filter(role=role):
            cache.delete(f'user_permissions_{user.pk}')
            cache.delete(f'user_role_permissions_{user.pk}')
        
        serializer = self.get_serializer(role)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users with this role."""
        role = self.get_object()
        users = User.objects.filter(role=role)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def all_permissions(self, request, pk=None):
        """Get all permissions for this role including inherited ones."""
        role = self.get_object()
        permissions = role.get_all_permissions()
        
        page = self.paginate_queryset(permissions)
        if page is not None:
            serializer = PermissionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for viewing permissions (read-only)."""
    queryset = Permission.objects.all().select_related('content_type')
    serializer_class = PermissionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'codename', 'content_type__app_label']
    ordering_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']
    throttle_classes = [UserRateThrottleBasic]

    def list(self, request, *args, **kwargs):
        """Override list to use caching"""
        cache_key = 'all_permissions'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None and not request.query_params:
            return Response(cached_data)
            
        response = super().list(request, *args, **kwargs)
        
        if not request.query_params:  # Only cache if no filters are applied
            cache.set(cache_key, response.data, timeout=3600)  # Cache for 1 hour
            
        return response
    
    @action(detail=False, methods=['get'])
    def by_app(self, request):
        """Get permissions grouped by app"""
        permissions = Permission.objects.all().select_related('content_type')
        
        # Group permissions by app
        app_permissions = {}
        for permission in permissions:
            app_label = permission.content_type.app_label
            if app_label not in app_permissions:
                app_permissions[app_label] = []
            
            app_permissions[app_label].append(PermissionSerializer(permission).data)
        
        return Response(app_permissions)


class PermissionChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for viewing permission change logs (read-only)."""
    queryset = PermissionChangeLog.objects.all().select_related('role', 'permission', 'changed_by')
    serializer_class = PermissionChangeLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['role__name', 'permission__name', 'changed_by__email']
    ordering_fields = ['changed_at', 'action']
    ordering = ['-changed_at']
    throttle_classes = [UserRateThrottleBasic]
    
    def get_queryset(self):
        """Apply filters for role and date range"""
        queryset = super().get_queryset()
        
        role_id = self.request.query_params.get('role_id')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
            
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(changed_at__gte=date_from)
            
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(changed_at__lte=date_to)
            
        return queryset 