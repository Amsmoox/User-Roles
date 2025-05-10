from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from .api import (
    UserViewSet, RoleViewSet, PermissionViewSet, PermissionChangeLogViewSet
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
]

# Optional format suffix support (e.g. /users.json)
format_suffix_patterns_urlpatterns = format_suffix_patterns(urlpatterns) 