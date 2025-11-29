import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ActivityForm, SettingsForm, SignUpForm
from .models import Activity, UserProfile
from .utils import get_canonical_activity_name


@login_required
def homepage_view(request):
    """Homepage showing today's energy level, recent activities, and quick log button"""
    # Get the start and end of today in the current timezone
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Get today's activities
    today_activities = Activity.objects.filter(
        user=request.user, activity_date__gte=today_start, activity_date__lte=today_end
    )

    # Calculate today's average energy level
    today_avg = today_activities.aggregate(Avg("energy_level"))["energy_level__avg"]

    # Get 5 most recent activities for today (ordered by activity date, descending)
    recent_activities = today_activities.order_by("-activity_date")[:5]

    context = {
        "today_avg": round(today_avg, 1) if today_avg is not None else None,
        "recent_activities": recent_activities,
        "activity_count": today_activities.count(),
    }

    return render(request, "energy_tracker/homepage.html", context)


def signup_view(request):
    """User registration view using Django's built-in User model"""
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after signup
            messages.success(
                request, f"Welcome {user.username}! Your account has been created."
            )
            return redirect("homepage")
    else:
        form = SignUpForm()

    return render(request, "energy_tracker/signup.html", {"form": form})


def login_view(request):
    """User login view using Django's built-in authentication"""
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("homepage")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "energy_tracker/login.html")


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard_view(request):
    """Dashboard with daily summary and simple chart data"""
    today = timezone.now().date()

    # Get today's activities
    today_activities = Activity.objects.filter(
        user=request.user, activity_date__date=today
    ).order_by("-activity_date")

    # Calculate today's stats
    today_count = today_activities.count()
    today_avg = (
        today_activities.aggregate(Avg("energy_level"))["energy_level__avg"] or 0
    )

    # Get last 7 days data for chart
    seven_days_ago = timezone.now() - timedelta(days=6)
    weekly_data = (
        Activity.objects.filter(user=request.user, activity_date__gte=seven_days_ago)
        .annotate(date=TruncDate("activity_date"))
        .values("date")
        .annotate(avg_energy=Avg("energy_level"), count=Count("id"))
        .order_by("date")
    )

    # Find top draining and energizing activities
    # New scale: -2,-1 are draining, 1,2 are energizing
    draining_activities = (
        Activity.objects.filter(user=request.user, energy_level__lt=0)
        .values("name")
        .annotate(avg_energy=Avg("energy_level"), count=Count("id"))
        .order_by("avg_energy")[:3]
    )

    energizing_activities = (
        Activity.objects.filter(user=request.user, energy_level__gt=0)
        .values("name")
        .annotate(avg_energy=Avg("energy_level"), count=Count("id"))
        .order_by("-avg_energy")[:3]
    )

    # --- Build data for dashboard charts ---------------------------------
    # Activity points (for line chart): include ISO timestamp and energy level
    # Note: today_activities is already ordered by '-activity_date' from the queryset above
    activity_points = [
        {
            "id": a.id,
            "name": a.name,
            "startTime": a.activity_date.isoformat(),
            "energy": a.energy_level,
        }
        for a in today_activities
    ]

    # Hourly averages for 24 hours (None when no data for that hour)
    hourly_avg = []
    for hour in range(24):
        q = today_activities.filter(activity_date__hour=hour)
        avg_val = q.aggregate(Avg("energy_level"))["energy_level__avg"]
        hourly_avg.append(float(avg_val) if avg_val is not None else None)

    # Calculate total time (in hours) spent in each energy state today
    # This sums the actual duration of activities, not hour slots
    hours_per_category = {"-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0}
    categories = [-2, -1, 0, 1, 2]

    for category in categories:
        total_minutes = (
            today_activities.filter(energy_level=category).aggregate(
                total=Sum("duration")
            )["total"]
            or 0
        )

        # Convert minutes to hours (rounded to 2 decimal places)
        hours_per_category[str(category)] = round(total_minutes / 60.0, 2)

    context = {
        "today_count": today_count,
        "today_avg": round(today_avg, 2),
        "weekly_data": json.dumps(
            [
                {
                    "date": str(item["date"]),
                    "avg_energy": float(item["avg_energy"]),
                    "count": item["count"],
                }
                for item in weekly_data
            ]
        ),
        "draining_activities": draining_activities,
        "energizing_activities": energizing_activities,
        "recent_activities": today_activities[:5],
        "activity_points": json.dumps(activity_points, default=str),
        "hourly_avg": json.dumps(hourly_avg),
        "hours_per_category": json.dumps(hours_per_category),
    }

    return render(request, "energy_tracker/dashboard.html", context)


@login_required
def log_activity_view(request):
    """View for logging a new activity with AJAX support"""
    if request.method == "POST":
        form = ActivityForm(request.POST)

        # Check if it's an AJAX request
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user

            # Normalize activity name (case-insensitive consolidation)
            activity.name = get_canonical_activity_name(request.user, activity.name)

            # Set duration from form's calculated value
            activity.duration = form.cleaned_data["duration"]

            # Use current time if no date provided
            if not activity.activity_date:
                activity.activity_date = timezone.now()

            activity.save()

            # Return JSON for AJAX requests
            if is_ajax:
                return JsonResponse(
                    {
                        "success": True,
                        "activity": {
                            "name": activity.name,
                            "duration": activity.get_duration_display(),
                            "energy_level": activity.get_energy_level_display(),
                            "energy_emoji": activity.get_energy_emoji(),
                        },
                    }
                )

            # Traditional form submission
            messages.success(
                request, f'Activity "{activity.name}" logged successfully!'
            )
            return redirect("log_activity")
        else:
            # Return errors for AJAX requests
            if is_ajax:
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )
    else:
        form = ActivityForm()

    return render(request, "energy_tracker/log_activity.html", {"form": form})


@login_required
def autocomplete_activities_view(request):
    """
    API endpoint for activity name autocomplete.
    Returns top 5 most frequent activities matching the search term.
    """
    search_term = request.GET.get("q", "").strip()

    if not search_term:
        return JsonResponse({"suggestions": []})

    # Get all activities matching the search term (case-insensitive)
    matching_activities = (
        Activity.objects.filter(user=request.user, name__icontains=search_term)
        .values("name")
        .annotate(count=Count("name"))
        .order_by("-count", "name")[:5]
    )

    # Get top 5 most frequent activities overall for is_top_5 flag
    top_5_overall = (
        Activity.objects.filter(user=request.user)
        .values("name")
        .annotate(count=Count("name"))
        .order_by("-count")[:5]
    )

    top_5_names = {item["name"].lower() for item in top_5_overall}

    # Format suggestions
    suggestions = [
        {
            "name": item["name"],
            "count": item["count"],
            "is_top_5": item["name"].lower() in top_5_names,
        }
        for item in matching_activities
    ]

    return JsonResponse({"suggestions": suggestions})


@login_required
def activity_history_view(request):
    """View for displaying paginated activity history"""
    # Get filter parameters
    energy_filter = request.GET.get("energy", None)
    q = request.GET.get("q", "").strip()
    view = request.GET.get("view", "day")  # 'day' | 'week' | 'month'

    # Base queryset
    activities = Activity.objects.filter(user=request.user)

    # Apply energy level filter if present
    if energy_filter:
        try:
            energy_filter = int(energy_filter)
            activities = activities.filter(energy_level=energy_filter)
        except ValueError:
            energy_filter = None

    # Apply time window filter based on view
    now = timezone.now()
    if view == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif view == "week":
        start = now - timedelta(days=7)
    else:  # month
        start = now - timedelta(days=30)

    activities = activities.filter(activity_date__gte=start)

    # Apply search filter on name
    if q:
        activities = activities.filter(name__icontains=q)

    # Ensure consistent ordering by activity date (most recent first)
    activities = activities.order_by("-activity_date")

    # Pagination
    paginator = Paginator(activities, 20)  # 20 activities per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "energy_filter": energy_filter,
        "q": q,
        "view": view,
    }

    return render(request, "energy_tracker/activity_history.html", context)


@login_required
def edit_activity_view(request, pk):
    """View for editing an existing activity"""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            updated_activity = form.save(commit=False)
            # Set duration from form's calculated value
            updated_activity.duration = form.cleaned_data["duration"]
            updated_activity.save()
            messages.success(request, "Activity updated successfully!")
            return redirect("activity_history")
    else:
        form = ActivityForm(instance=activity)

    return render(
        request,
        "energy_tracker/edit_activity.html",
        {"form": form, "activity": activity},
    )


@login_required
def delete_activity_view(request, pk):
    """View for deleting an activity"""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)

    if request.method == "POST":
        activity_name = activity.name
        activity.delete()
        messages.success(request, f'Activity "{activity_name}" deleted successfully!')
        return redirect("activity_history")

    return render(
        request, "energy_tracker/delete_activity.html", {"activity": activity}
    )


@login_required
def bulk_delete_activities_view(request):
    """View for deleting multiple activities at once"""
    if request.method == "POST":
        activity_ids = request.POST.getlist("activity_ids")

        if activity_ids:
            # Filter activities that belong to the current user
            activities = Activity.objects.filter(pk__in=activity_ids, user=request.user)
            count = activities.count()

            if count > 0:
                activities.delete()
                messages.success(
                    request,
                    f'Successfully deleted {count} {"activity" if count == 1 else "activities"}!',
                )
            else:
                messages.warning(request, "No activities were selected or found.")
        else:
            messages.warning(request, "No activities were selected.")

    return redirect("activity_history")


@login_required
def settings_view(request):
    """Allow users to change theme and notification preferences."""
    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = SettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Set a cookie so client-side can pick up theme quickly
            theme = form.cleaned_data.get("theme", UserProfile.THEME_LIGHT)
            response = redirect("dashboard")
            response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 365)
            messages.success(request, "Settings updated.")
            return response
    else:
        form = SettingsForm(instance=profile)

    return render(request, "energy_tracker/settings.html", {"form": form})


@login_required
def account_view(request):
    """Simple account page showing basic user info."""
    user = request.user
    profile = None
    try:
        profile = user.profile
    except Exception:
        profile = None

    context = {
        "user_obj": user,
        "profile": profile,
    }

    return render(request, "energy_tracker/account.html", context)


@login_required
def change_password_view(request):
    """Allow users to change their password from the account area."""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: update session hash so the user isn't logged out
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed successfully.")
            return redirect("account")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "energy_tracker/change_password.html", {"form": form})
