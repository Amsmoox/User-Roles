from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    The Role model represents user roles in the system.
    Each role can have multiple permissions.
    """
    name = models.CharField(_("Role Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent Role"),
        help_text=_("Parent role whose permissions will be inherited")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_roles',
        verbose_name=_("Created By"),
    )
    updated_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_roles',
        verbose_name=_("Updated By"),
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return self.name
    
    def get_all_permissions(self):
        """Get all permissions including those from parent roles."""
        # Use cache to avoid repeated DB queries
        cache_key = f'role_permissions_{self.id}'
        cached_permissions = cache.get(cache_key)
        
        if cached_permissions is not None:
            return cached_permissions
            
        # Start with this role's direct permissions
        all_permissions = set(self.permissions.all())
        
        # Add permissions from parent roles
        if self.parent:
            all_permissions.update(self.parent.get_all_permissions())
        
        # Cache the result for future queries
        cache.set(cache_key, all_permissions, timeout=3600)  # Cache for 1 hour
        
        return all_permissions


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email as the primary identifier
    and includes role-based permissions.
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_("Role")
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",
        related_query_name="user",
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    bio = models.TextField(_("Biography"), blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def save(self, *args, **kwargs):
        # Clear permission cache when user's role changes
        if self.pk:
            old_instance = User.objects.get(pk=self.pk)
            if old_instance.role != self.role:
                self._clear_permission_cache()
        super().save(*args, **kwargs)

    def _clear_permission_cache(self):
        """Clear cached permissions for this user."""
        cache.delete(f'user_permissions_{self.pk}')
        cache.delete(f'user_role_permissions_{self.pk}')

    def get_role_permissions(self):
        """Get all permissions from the user's role."""
        cache_key = f'user_role_permissions_{self.pk}'
        cached_permissions = cache.get(cache_key)
        
        if cached_permissions is not None:
            return cached_permissions
            
        if self.role:
            permissions = self.role.get_all_permissions()
            cache.set(cache_key, permissions, timeout=3600)  # Cache for 1 hour
            return permissions
        return Permission.objects.none()

    def has_role_permission(self, permission_name):
        """Check if the user's role has a specific permission."""
        if self.is_superuser:
            return True
        if not self.role:
            return False
            
        # Check cache first
        cache_key = f'user_permission_{self.pk}_{permission_name}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
            
        app_label, codename = permission_name.split('.')
        result = self.role.permissions.filter(
            content_type__app_label=app_label,
            codename=codename
        ).exists()
        
        # Also check parent roles if needed
        if not result and self.role.parent:
            parent_role = self.role.parent
            while parent_role and not result:
                result = parent_role.permissions.filter(
                    content_type__app_label=app_label,
                    codename=codename
                ).exists()
                parent_role = parent_role.parent
        
        # Cache the result
        cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
        return result
        
    def has_multiple_permissions(self, permission_names):
        """Check if the user has all specified permissions."""
        return all(self.has_role_permission(perm) for perm in permission_names)


class PermissionChangeLog(models.Model):
    """
    Audit trail for permission changes.
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permission_changes',
        verbose_name=_("Role")
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_changes',
        verbose_name=_("Permission")
    )
    action = models.CharField(
        _("Action"),
        max_length=10,
        choices=[('add', _('Added')), ('remove', _('Removed'))]
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permission_changes',
        verbose_name=_("Changed By")
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("permission change log")
        verbose_name_plural = _("permission change logs")

    def __str__(self):
        return f"{self.get_action_display()} {self.permission} to {self.role}"
