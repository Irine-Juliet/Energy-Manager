from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('log-activity/', views.log_activity_view, name='log_activity'),
    path('history/', views.activity_history_view, name='activity_history'),
    path('activity/<int:pk>/edit/', views.edit_activity_view, name='edit_activity'),
    path('activity/<int:pk>/delete/', views.delete_activity_view, name='delete_activity'),
]
