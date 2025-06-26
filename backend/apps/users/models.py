from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for VITAL MASTERY platform.
    Extends Django's AbstractUser with additional fields.
    """
    
    email = models.EmailField(
        'email address',
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    
    profile_picture = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='User profile picture'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='Short biography for user profile'
    )
    
    is_author = models.BooleanField(
        default=False,
        help_text='Designates whether this user can create articles.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name