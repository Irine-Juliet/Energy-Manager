from django.contrib import admin
from .models import Activity, ABTestEvent


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'duration', 'energy_level', 'activity_date', 'created_at']
    list_filter = ['energy_level', 'activity_date', 'user']
    search_fields = ['name', 'description', 'user__username']
    date_hierarchy = 'activity_date'
    ordering = ['-activity_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ABTestEvent)
class ABTestEventAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'event_type', 'variant', 'session_id', 'ip_address']
    list_filter = ['event_type', 'variant', 'timestamp']
    search_fields = ['session_id', 'ip_address']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    readonly_fields = ['timestamp', 'event_type', 'variant', 'session_id', 'user_agent', 'ip_address']
    
    def has_add_permission(self, request):
        # Prevent manual creation through admin
        return False
