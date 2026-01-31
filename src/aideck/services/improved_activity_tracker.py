"""
Improved Workday Summarizer with Dynamic Activity Categorization
"""

from datetime import datetime
from typing import Any

# Activity categories
WORK_KEYWORDS = [
    "coding",
    "programming",
    "development",
    "writing",
    "editing",
    "designing",
    "analyzing",
    "researching",
    "planning",
    "documenting",
    "debugging",
    "testing",
    "reviewing",
    "spreadsheet",
    "excel",
    "word",
    "document",
    "report",
    "presentation",
    "slide",
    "data",
    "analysis",
    "calculation",
    "modeling",
    "database",
    "sql",
]

COMMUNICATION_KEYWORDS = [
    "meeting",
    "call",
    "video",
    "conference",
    "chat",
    "message",
    "email",
    "outlook",
    "teams",
    "slack",
    "discord",
    "zoom",
    "skype",
    "webex",
    "discussion",
    "collaboration",
    "review",
    "feedback",
    "planning",
    "standup",
    "sync",
    "1:1",
]

BREAKS_KEYWORDS = [
    "break",
    "lunch",
    "coffee",
    "rest",
    "relax",
    "music",
    "video",
    "youtube",
    "netflix",
    "game",
    "social media",
    "facebook",
    "twitter",
    "instagram",
    "tiktok",
    "reddit",
    "news",
    "entertainment",
]


def categorize_activity(
    user_activity: str, content_summary: str, window_title: str
) -> tuple[str, float]:
    """Categorize an activity based on keywords and context.

    Args:
        user_activity: Description of what the user is doing
        content_summary: Summary of the content being displayed
        window_title: Title of the window

    Returns:
        Tuple of (category, confidence_score)
    """
    text_to_analyze = f"{user_activity} {content_summary} {window_title}".lower()

    # Score each category
    category_scores = {
        "work": sum(1 for keyword in WORK_KEYWORDS if keyword in text_to_analyze),
        "communication": sum(
            1 for keyword in COMMUNICATION_KEYWORDS if keyword in text_to_analyze
        ),
        "breaks": sum(1 for keyword in BREAKS_KEYWORDS if keyword in text_to_analyze),
    }

    # Find the category with the highest score
    if not any(category_scores.values()):
        return "uncategorized", 0.0

    best_category = max(category_scores, key=category_scores.get)
    max_score = category_scores[best_category]

    # Calculate confidence based on score
    max_possible_score = len(eval(f"{best_category.upper()}_KEYWORDS"))
    confidence = max_score / max_possible_score if max_possible_score > 0 else 0.0

    # Only categorize if confidence is above threshold
    if confidence < 0.3:
        return "uncategorized", confidence

    return best_category, confidence


def generate_activity_summary(activity_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of activities with dynamic categorization.

    Args:
        activity_log: List of activity entries

    Returns:
        Dictionary containing the activity summary
    """
    if not activity_log:
        return {"error": "No activity data available"}

    # Calculate time statistics
    SNAPSHOT_INTERVAL = 10  # seconds
    total_minutes = len(activity_log) * (SNAPSHOT_INTERVAL / 60)

    # Track time spent per app
    time_spent = {}
    for entry in activity_log:
        app = entry["app_name"]
        time_spent[app] = time_spent.get(app, 0) + SNAPSHOT_INTERVAL

    # Categorize activities and calculate time distribution
    category_times = {"work": 0, "communication": 0, "breaks": 0, "uncategorized": 0}
    categorized_activities = {
        "work": [],
        "communication": [],
        "breaks": [],
        "uncategorized": [],
    }

    for entry in activity_log:
        category, confidence = categorize_activity(
            entry["user_activity"], entry["content_summary"], entry["window_title"]
        )

        category_times[category] += SNAPSHOT_INTERVAL
        categorized_activities[category].append(
            {**entry, "category": category, "confidence": confidence}
        )

    # Convert to minutes and calculate percentages
    time_distribution = {}
    for category, seconds in category_times.items():
        minutes = int(seconds // 60)
        percentage = (
            int((seconds / (total_minutes * 60)) * 100) if total_minutes > 0 else 0
        )
        time_distribution[category] = {"minutes": minutes, "percentage": percentage}

    # Generate summary report
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_tracked_minutes": int(total_minutes),
        "apps_used": [
            {"app": app, "minutes": int(duration // 60)}
            for app, duration in time_spent.items()
        ],
        "time_distribution": time_distribution,
        "summary": {
            "work_minutes": time_distribution.get("work", {}).get("minutes", 0),
            "communication_minutes": time_distribution.get("communication", {}).get(
                "minutes", 0
            ),
            "breaks_minutes": time_distribution.get("breaks", {}).get("minutes", 0),
            "uncategorized_minutes": time_distribution.get("uncategorized", {}).get(
                "minutes", 0
            ),
        },
        "categorized_activities_count": {
            category: len(activities)
            for category, activities in categorized_activities.items()
        },
    }

    return summary


# Example usage
if __name__ == "__main__":
    # Sample activity log (this would come from your monitoring system)
    sample_activity_log = [
        {
            "timestamp": "2024-01-15 09:00:00",
            "app_name": "Visual Studio Code",
            "window_title": "main.py - GPT Computer Agent",
            "content_summary": "Writing Python code for activity tracking",
            "user_activity": "coding and debugging application",
        },
        {
            "timestamp": "2024-01-15 09:10:00",
            "app_name": "Microsoft Teams",
            "window_title": "Team Standup Meeting",
            "content_summary": "Video call with team members",
            "user_activity": "participating in daily standup meeting",
        },
        {
            "timestamp": "2024-01-15 09:30:00",
            "app_name": "Chrome",
            "window_title": "YouTube - Tutorial",
            "content_summary": "Watching programming tutorial",
            "user_activity": "learning new programming concepts",
        },
    ]

    # Generate the improved summary
    summary = generate_activity_summary(sample_activity_log)

    print("=== ACTIVITY SUMMARY ===")
    print(f"Date: {summary['date']}")
    print(f"Total Tracked: {summary['total_tracked_minutes']} minutes")
    print(f"Apps Used: {len(summary['apps_used'])}")
    print("\n=== TIME DISTRIBUTION ===")
    for category, data in summary["time_distribution"].items():
        if data["minutes"] > 0:
            print(f"{category.title()}: {data['minutes']} min ({data['percentage']}%)")

    print("\n=== BREAKDOWN ===")
    work_min = summary["summary"]["work_minutes"]
    comm_min = summary["summary"]["communication_minutes"]
    break_min = summary["summary"]["breaks_minutes"]

    print(f"Work: {work_min} minutes")
    print(f"Communication: {comm_min} minutes")
    print(f"Breaks: {break_min} minutes")

    # Calculate productivity score
    total_categorized = work_min + comm_min + break_min
    if total_categorized > 0:
        productivity_score = int((work_min + comm_min) / total_categorized * 100)
        print(f"\nProductivity Score: {productivity_score}%")
