from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'energy_level', 'activity_date', 'created_at']
    list_filter = ['energy_level', 'activity_date', 'user']
    search_fields = ['name', 'description', 'user__username']
    date_hierarchy = 'activity_date'
    ordering = ['-activity_date']
