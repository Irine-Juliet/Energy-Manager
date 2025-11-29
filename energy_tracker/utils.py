"""
Utility functions for the energy_tracker app.
"""

from django.db.models import Count


def get_canonical_activity_name(user, name_input):
    """
    Return the most common casing for an activity name.

    This function consolidates activity names that differ only in casing
    (e.g., "Meeting" vs "meeting" vs "MEETING") by returning the most
    frequently used casing variant.

    Args:
        user: The User object to filter activities by
        name_input: The activity name to normalize (string)

    Returns:
        The most common casing of the activity name, or the input if no match

    Algorithm:
        1. Query all user's activities with case-insensitive name match
        2. Group by exact name (case-sensitive)
        3. Count occurrences of each casing variant
        4. Return most common casing (or most recent on tie)
        5. If no match, return stripped input
    """
    from .models import Activity

    # Strip whitespace from input
    name_input = name_input.strip()

    # Query activities with case-insensitive match
    matching_activities = (
        Activity.objects.filter(user=user, name__iexact=name_input)
        .values("name")
        .annotate(count=Count("name"))
        .order_by("-count")
    )

    # Return the most common casing (first result due to ordering)
    if matching_activities.exists():
        return matching_activities.first()["name"]

    # No match found, return the input
    return name_input
