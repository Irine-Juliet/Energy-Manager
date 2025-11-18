from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
import json
from .models import Activity
from .forms import SignUpForm, ActivityForm


def signup_view(request):
    """User registration view using Django's built-in User model"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after signup
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'energy_tracker/signup.html', {'form': form})


def login_view(request):
    """User login view using Django's built-in authentication"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'energy_tracker/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Dashboard with daily summary and simple chart data"""
    today = timezone.now().date()
    
    # Get today's activities
    today_activities = Activity.objects.filter(
        user=request.user,
        activity_date__date=today
    )
    
    # Calculate today's stats
    today_count = today_activities.count()
    today_avg = today_activities.aggregate(Avg('energy_level'))['energy_level__avg'] or 0
    
    # Get last 7 days data for chart
    seven_days_ago = timezone.now() - timedelta(days=6)
    weekly_data = Activity.objects.filter(
        user=request.user,
        activity_date__gte=seven_days_ago
    ).annotate(
        date=TruncDate('activity_date')
    ).values('date').annotate(
        avg_energy=Avg('energy_level'),
        count=Count('id')
    ).order_by('date')
    
    # Find top draining and energizing activities
    draining_activities = Activity.objects.filter(
        user=request.user,
        energy_level__lt=0
    ).values('name').annotate(
        avg_energy=Avg('energy_level'),
        count=Count('id')
    ).order_by('avg_energy')[:3]
    
    energizing_activities = Activity.objects.filter(
        user=request.user,
        energy_level__gt=0
    ).values('name').annotate(
        avg_energy=Avg('energy_level'),
        count=Count('id')
    ).order_by('-avg_energy')[:3]
    
    # --- Build data for dashboard charts ---------------------------------
    # Activity points (for line chart): include ISO timestamp and energy level
    activity_points = [
        {
            'id': a.id,
            'name': a.name,
            'startTime': a.activity_date.isoformat(),
            'energy': a.energy_level,
        }
        for a in today_activities
    ]

    # Hourly averages for 24 hours (None when no data for that hour)
    hourly_avg = []
    for hour in range(24):
        q = today_activities.filter(activity_date__hour=hour)
        avg_val = q.aggregate(Avg('energy_level'))['energy_level__avg']
        hourly_avg.append(float(avg_val) if avg_val is not None else None)

    # Count how many hours (distinct hour slots) fall into each category.
    # We treat a slot with at least one activity as 1 "hour" for this summary.
    hours_per_category = {'-1': 0, '0': 0, '1': 0, '2': 0}
    for avg in hourly_avg:
        if avg is None:
            continue
        if avg < 0:
            hours_per_category['-1'] += 1
        elif avg == 0:
            hours_per_category['0'] += 1
        elif 0 < avg < 2:
            hours_per_category['1'] += 1
        else:
            hours_per_category['2'] += 1

    context = {
        'today_count': today_count,
        'today_avg': round(today_avg, 2),
        'weekly_data': json.dumps([
            {
                'date': str(item['date']),
                'avg_energy': float(item['avg_energy']),
                'count': item['count']
            }
            for item in weekly_data
        ]),
        'draining_activities': draining_activities,
        'energizing_activities': energizing_activities,
        'recent_activities': today_activities[:5],
        'activity_points': json.dumps(activity_points, default=str),
        'hourly_avg': json.dumps(hourly_avg),
        'hours_per_category': json.dumps(hours_per_category),
    }

    return render(request, 'energy_tracker/dashboard.html', context)


@login_required
def log_activity_view(request):
    """View for logging a new activity"""
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            
            # Use current time if no date provided
            if not activity.activity_date:
                activity.activity_date = timezone.now()
            
            activity.save()
            messages.success(request, f'Activity "{activity.name}" logged successfully!')
            return redirect('dashboard')
    else:
        form = ActivityForm()
    
    return render(request, 'energy_tracker/log_activity.html', {'form': form})


@login_required
def activity_history_view(request):
    """View for displaying paginated activity history"""
    # Get filter parameters
    energy_filter = request.GET.get('energy', None)
    
    # Base queryset
    activities = Activity.objects.filter(user=request.user)
    
    # Apply filters
    if energy_filter:
        try:
            energy_filter = int(energy_filter)
            activities = activities.filter(energy_level=energy_filter)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(activities, 20)  # 20 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'energy_filter': energy_filter,
    }
    
    return render(request, 'energy_tracker/activity_history.html', context)


@login_required
def edit_activity_view(request, pk):
    """View for editing an existing activity"""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('activity_history')
    else:
        form = ActivityForm(instance=activity)
    
    return render(request, 'energy_tracker/edit_activity.html', {'form': form, 'activity': activity})


@login_required
def delete_activity_view(request, pk):
    """View for deleting an activity"""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    
    if request.method == 'POST':
        activity_name = activity.name
        activity.delete()
        messages.success(request, f'Activity "{activity_name}" deleted successfully!')
        return redirect('activity_history')
    
    return render(request, 'energy_tracker/delete_activity.html', {'activity': activity})
