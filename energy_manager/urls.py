"""
URL configuration for energy_manager project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("energy_tracker.urls")),
]
