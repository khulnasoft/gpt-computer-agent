"""
Activity tracking tools for the GPT Computer Agent.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.tools import tool
from ..services.activity_tracker import ActivityCategory, activity_tracker


@tool
def track_activity(app_name: str, window_title: str, content_summary: str, user_activity: str) -> Dict[str, Any]:
    """Track a user activity and categorize it.

    Args:
        app_name: Name of the application currently in use
        window_title: Title of the active window
        content_summary: Summary of the content being displayed
        user_activity: Description of what the user is doing

    Returns:
        Dictionary containing the categorized activity information
    """
    entry = activity_tracker.add_activity(
        app_name=app_name,
        window_title=window_title,
        content_summary=content_summary,
        user_activity=user_activity
    )

    return {
        "timestamp": entry.timestamp.isoformat(),
        "app_name": entry.app_name,
        "window_title": entry.window_title,
        "user_activity": entry.user_activity,
        "category": entry.category.value,
        "confidence": entry.confidence,
        "message": f"Activity categorized as {entry.category.value} with {entry.confidence".1%"} confidence"
    }

@tool
def get_activity_summary(start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
    """Get a summary of tracked activities for a time period.

    Args:
        start_time: ISO format start time (optional)
        end_time: ISO format end time (optional)

    Returns:
        Dictionary containing the activity summary
    """
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    summary = activity_tracker.get_summary(start_time=start_dt, end_time=end_dt)

    return {
        "date": summary.date,
        "total_tracked_minutes": summary.total_tracked_minutes,
        "total_activities": summary.total_activities,
        "apps_used": summary.apps_used,
        "time_distribution": summary.time_distribution,
        "summary": {
            "work_minutes": summary.time_distribution.get("work", {}).get("minutes", 0),
            "communication_minutes": summary.time_distribution.get("communication", {}).get("minutes", 0),
            "breaks_minutes": summary.time_distribution.get("breaks", {}).get("minutes", 0),
            "uncategorized_minutes": summary.time_distribution.get("uncategorized", {}).get("minutes", 0)
        }
    }

@tool
def categorize_activities_interactive() -> Dict[str, Any]:
    """Interactively categorize uncategorized activities.

    Returns:
        Dictionary containing categorization results
    """
    uncategorized = [
        entry for entry in activity_tracker.activity_log
        if entry.category == ActivityCategory.UNCATEGORIZED
    ]

    if not uncategorized:
        return {"message": "No uncategorized activities found", "categorized": 0}

    categorized_count = 0

    # This would typically use the remote.input() function to ask the user
    # For now, we'll use keyword-based categorization as a fallback
    for entry in uncategorized:
        # Try to recategorize using a more lenient approach
        category, confidence = activity_tracker._categorize_activity(entry)

        # If we get a better categorization, update it
        if confidence > entry.confidence:
            entry.category = category
            entry.confidence = confidence
            categorized_count += 1

    return {
        "message": f"Recategorized {categorized_count} activities",
        "total_uncategorized": len(uncategorized),
        "categorized": categorized_count
    }

@tool
def save_activity_log(filename: str) -> Dict[str, Any]:
    """Save the activity log to a JSON file.

    Args:
        filename: Name of the file to save to

    Returns:
        Dictionary containing save results
    """
    try:
        activity_tracker.save_to_file(filename)
        return {
            "success": True,
            "filename": filename,
            "activities_saved": len(activity_tracker.activity_log),
            "message": f"Activity log saved to {filename}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save activity log: {e}"
        }

@tool
def load_activity_log(filename: str) -> Dict[str, Any]:
    """Load an activity log from a JSON file.

    Args:
        filename: Name of the file to load from

    Returns:
        Dictionary containing load results
    """
    try:
        activity_tracker.load_from_file(filename)
        return {
            "success": True,
            "filename": filename,
            "activities_loaded": len(activity_tracker.activity_log),
            "message": f"Activity log loaded from {filename}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to load activity log: {e}"
        }

@tool
def get_productivity_insights() -> Dict[str, Any]:
    """Get productivity insights based on activity patterns.

    Returns:
        Dictionary containing productivity insights
    """
    summary = activity_tracker.get_summary()

    if summary.total_tracked_minutes == 0:
        return {"message": "No activity data available for insights"}

    # Calculate productivity metrics
    work_time = summary.time_distribution.get("work", {}).get("minutes", 0)
    communication_time = summary.time_distribution.get("communication", {}).get("minutes", 0)
    break_time = summary.time_distribution.get("breaks", {}).get("minutes", 0)

    # Simple productivity score calculation
    if summary.total_tracked_minutes > 0:
        productive_time = work_time + communication_time
        productivity_score = int((productive_time / summary.total_tracked_minutes) * 100)
    else:
        productivity_score = 0

    # Generate insights
    insights = []

    if productivity_score > 80:
        insights.append("Excellent productivity! You're making great use of your time.")
    elif productivity_score > 60:
        insights.append("Good productivity. Consider taking more focused work sessions.")
    elif productivity_score > 40:
        insights.append("Moderate productivity. Try to minimize distractions.")
    else:
        insights.append("Low productivity detected. Consider setting specific goals and taking regular breaks.")

    # App usage insights
    if summary.apps_used:
        top_app = max(summary.apps_used, key=lambda x: x["minutes"])
        insights.append(f"Your most used app is {top_app['app']} ({top_app['minutes']} minutes)")

    # Break pattern insights
    if break_time > 0:
        break_frequency = break_time / (summary.total_tracked_minutes / 60)  # breaks per hour
        if break_frequency < 1:
            insights.append("Consider taking more frequent short breaks to maintain focus.")
        elif break_frequency > 3:
            insights.append("You seem to be taking many breaks. Try consolidating them.")

    return {
        "productivity_score": productivity_score,
        "insights": insights,
        "recommendations": [
            "Use the Pomodoro technique: 25 minutes focused work + 5 minute break",
            "Schedule important tasks during your peak energy hours",
            "Minimize context switching between different types of work",
            "Take regular breaks to maintain long-term productivity"
        ]
    }
