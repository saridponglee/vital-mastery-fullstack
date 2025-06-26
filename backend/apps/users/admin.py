from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.
    """
    
    list_display = (
        'email', 'username', 'first_name', 'last_name', 
        'is_author', 'is_staff', 'is_active', 'date_joined'
    )
    
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_author', 'date_joined'
    )
    
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    ordering = ('-date_joined',)
    
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'bio', 'profile_picture')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_author',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    ) 