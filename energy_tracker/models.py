from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Activity(models.Model):
    """
    Model to store user activities with energy ratings.
    Energy level ranges from -2 (very draining) to +2 (very energizing).
    """
    ENERGY_CHOICES = [
        (-2, 'Very Draining'),
        (-1, 'Draining'),
        (0, 'Neutral'),
        (1, 'Energizing'),
        (2, 'Flow State / Very Energizing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    energy_level = models.IntegerField(choices=ENERGY_CHOICES)
    activity_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-activity_date']
        verbose_name_plural = 'Activities'
        # Explicit app_label to avoid import-time app detection issues when the
        # project/workspace directory name contains characters (like '-') that
        # make Python package/module names invalid. This keeps tests importable
        # and is safe because the real app label is `energy_tracker`.
        app_label = 'energy_tracker'
    
    def __str__(self):
        return f"{self.name} ({self.get_energy_level_display()})"
    
    def get_energy_emoji(self):
        """Return an emoji representing the energy level"""
        emoji_map = {
            -2: '😫',
            -1: '😔',
            0: '😐',
            1: '😊',
            2: '🚀',
        }
        return emoji_map.get(self.energy_level, '😐')


class UserProfile(models.Model):
    """Simple user profile to store UI preferences."""
    THEME_LIGHT = 'light'
    THEME_DARK = 'dark'
    THEME_CHOICES = [
        (THEME_LIGHT, 'Light'),
        (THEME_DARK, 'Dark'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default=THEME_LIGHT)
    notifications = models.BooleanField(default=True)

    class Meta:
        app_label = 'energy_tracker'

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
