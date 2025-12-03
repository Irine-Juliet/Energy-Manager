from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.homepage_view, name='homepage'),
    
    # A/B Test endpoint (SHA1 hash of "constipated-Lemon": 2be044d)
    path('2be044d/', views.abtest_endpoint_view, name='abtest_endpoint'),
    path('ab-test/log-event/', views.abtest_log_event_view, name='abtest_log_event'),
    path('ab-test/results/', views.abtest_results_view, name='abtest_results'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('log-activity/', views.log_activity_view, name='log_activity'),
    path('autocomplete-activities/', views.autocomplete_activities_view, name='autocomplete_activities'),
    path('history/', views.activity_history_view, name='activity_history'),
    path('activity/<int:pk>/edit/', views.edit_activity_view, name='edit_activity'),
    path('activity/<int:pk>/delete/', views.delete_activity_view, name='delete_activity'),
    path('activities/bulk-delete/', views.bulk_delete_activities_view, name='bulk_delete_activities'),
    path('settings/', views.settings_view, name='settings'),
    path('account/', views.account_view, name='account'),
    path('account/change-password/', views.change_password_view, name='change_password'),
]
