from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from .api import (
    UserViewSet, RoleViewSet, PermissionViewSet, PermissionChangeLogViewSet
)
from .auth import (
    RegisterView, LoginView, LogoutView, 
    PasswordResetRequestView, PasswordResetConfirmView, PasswordChangeView
)

app_name = 'accounts'

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'permission-logs', PermissionChangeLogViewSet)

# Standard URL patterns
urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
]

# Optional format suffix support (e.g. /users.json)
format_suffix_patterns_urlpatterns = format_suffix_patterns(urlpatterns) 