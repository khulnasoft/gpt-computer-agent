"""
Activity tracking service for categorizing and analyzing user activities.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActivityCategory(Enum):
    """Categories for user activities."""

    WORK = "work"
    COMMUNICATION = "communication"
    BREAKS = "breaks"
    UNCATEGORIZED = "uncategorized"


@dataclass
class ActivityEntry:
    """Represents a single activity snapshot."""

    timestamp: datetime
    app_name: str
    window_title: str
    content_summary: str
    user_activity: str
    category: ActivityCategory = ActivityCategory.UNCATEGORIZED
    confidence: float = 0.0


@dataclass
class ActivitySummary:
    """Summary of activities for a time period."""

    date: str
    total_tracked_minutes: int
    apps_used: list[dict[str, int]]
    time_distribution: dict[str, dict[str, int]]
    categorized_activities: dict[ActivityCategory, list[ActivityEntry]]
    total_activities: int


class ActivityTracker:
    """Service for tracking and categorizing user activities."""

    def __init__(self):
        """Initialize the activity tracker."""
        self.activity_log: list[ActivityEntry] = []
        self.category_keywords = {
            ActivityCategory.WORK: [
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
            ],
            ActivityCategory.COMMUNICATION: [
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
            ],
            ActivityCategory.BREAKS: [
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
            ],
        }

    def add_activity(
        self, app_name: str, window_title: str, content_summary: str, user_activity: str
    ) -> ActivityEntry:
        """Add a new activity and categorize it.

        Args:
            app_name: Name of the application
            window_title: Title of the window
            content_summary: Summary of the content
            user_activity: Description of what the user is doing

        Returns:
            The categorized activity entry
        """
        # Create the activity entry
        entry = ActivityEntry(
            timestamp=datetime.now(),
            app_name=app_name,
            window_title=window_title,
            content_summary=content_summary,
            user_activity=user_activity,
        )

        # Categorize the activity
        entry.category, entry.confidence = self._categorize_activity(entry)

        # Add to log
        self.activity_log.append(entry)

        return entry

    def _categorize_activity(
        self, entry: ActivityEntry
    ) -> tuple[ActivityCategory, float]:
        """Categorize an activity based on keywords and context.

        Args:
            entry: The activity entry to categorize

        Returns:
            Tuple of (category, confidence_score)
        """
        text_to_analyze = f"{entry.user_activity} {entry.content_summary} {entry.window_title}".lower()

        # Score each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_to_analyze:
                    score += 1
            category_scores[category] = score

        # Find the category with the highest score
        if not category_scores:
            return ActivityCategory.UNCATEGORIZED, 0.0

        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]

        # Calculate confidence based on score
        max_possible_score = len(self.category_keywords[best_category])
        confidence = max_score / max_possible_score if max_possible_score > 0 else 0.0

        # Only categorize if confidence is above threshold
        if confidence < 0.3:
            return ActivityCategory.UNCATEGORIZED, confidence

        return best_category, confidence

    def get_summary(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> ActivitySummary:
        """Generate a summary of activities for a time period.

        Args:
            start_time: Start of the time period (default: beginning of log)
            end_time: End of the time period (default: end of log)

        Returns:
            Activity summary for the period
        """
        if not self.activity_log:
            return self._create_empty_summary()

        # Filter activities by time range
        filtered_activities = self._filter_activities_by_time(start_time, end_time)

        if not filtered_activities:
            return self._create_empty_summary()

        # Calculate time statistics
        total_minutes = self._calculate_total_minutes(filtered_activities)
        apps_used = self._calculate_apps_used(filtered_activities)
        time_distribution = self._calculate_time_distribution(
            filtered_activities, total_minutes
        )
        categorized_activities = self._group_by_category(filtered_activities)

        return ActivitySummary(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_tracked_minutes=total_minutes,
            apps_used=apps_used,
            time_distribution=time_distribution,
            categorized_activities=categorized_activities,
            total_activities=len(filtered_activities),
        )

    def _filter_activities_by_time(
        self, start_time: datetime | None, end_time: datetime | None
    ) -> list[ActivityEntry]:
        """Filter activities by time range."""
        if start_time is None:
            start_time = self.activity_log[0].timestamp
        if end_time is None:
            end_time = self.activity_log[-1].timestamp

        return [
            entry
            for entry in self.activity_log
            if start_time <= entry.timestamp <= end_time
        ]

    def _calculate_total_minutes(self, activities: list[ActivityEntry]) -> int:
        """Calculate total tracked minutes from activities."""
        if not activities:
            return 0

        # For now, use a simple approximation
        # In a real implementation, this would be based on actual time intervals
        SNAPSHOT_INTERVAL = 10  # seconds
        estimated_minutes = len(activities) * (SNAPSHOT_INTERVAL / 60)
        return int(estimated_minutes)

    def _calculate_apps_used(
        self, activities: list[ActivityEntry]
    ) -> list[dict[str, int]]:
        """Calculate time spent per application."""
        app_times = {}
        SNAPSHOT_INTERVAL = 10  # seconds

        for entry in activities:
            app_times[entry.app_name] = (
                app_times.get(entry.app_name, 0) + SNAPSHOT_INTERVAL
            )

        return [
            {"app": app, "minutes": int(duration // 60)}
            for app, duration in app_times.items()
        ]

    def _calculate_time_distribution(
        self, activities: list[ActivityEntry], total_minutes: int
    ) -> dict[str, dict[str, int]]:
        """Calculate time distribution by category."""
        category_times = dict.fromkeys(ActivityCategory, 0)
        SNAPSHOT_INTERVAL = 10  # seconds

        for entry in activities:
            category_times[entry.category] += SNAPSHOT_INTERVAL

        # Convert to minutes and calculate percentages
        distribution = {}
        for category, seconds in category_times.items():
            minutes = int(seconds // 60)
            percentage = (
                int((seconds / (total_minutes * 60)) * 100) if total_minutes > 0 else 0
            )
            distribution[category.value] = {
                "minutes": minutes,
                "percentage": percentage,
            }

        return distribution

    def _group_by_category(
        self, activities: list[ActivityEntry]
    ) -> dict[ActivityCategory, list[ActivityEntry]]:
        """Group activities by category."""
        grouped = {category: [] for category in ActivityCategory}

        for entry in activities:
            grouped[entry.category].append(entry)

        return grouped

    def _create_empty_summary(self) -> ActivitySummary:
        """Create an empty summary when no activities are available."""
        return ActivitySummary(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_tracked_minutes=0,
            apps_used=[],
            time_distribution={
                category.value: {"minutes": 0, "percentage": 0}
                for category in ActivityCategory
            },
            categorized_activities={category: [] for category in ActivityCategory},
            total_activities=0,
        )

    def save_to_file(self, filename: str) -> None:
        """Save activity log to a JSON file."""
        data = {
            "activities": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "app_name": entry.app_name,
                    "window_title": entry.window_title,
                    "content_summary": entry.content_summary,
                    "user_activity": entry.user_activity,
                    "category": entry.category.value,
                    "confidence": entry.confidence,
                }
                for entry in self.activity_log
            ]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename: str) -> None:
        """Load activity log from a JSON file."""
        with open(filename) as f:
            data = json.load(f)

        self.activity_log = []
        for entry_data in data.get("activities", []):
            entry = ActivityEntry(
                timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                app_name=entry_data["app_name"],
                window_title=entry_data["window_title"],
                content_summary=entry_data["content_summary"],
                user_activity=entry_data["user_activity"],
                category=ActivityCategory(entry_data["category"]),
                confidence=entry_data.get("confidence", 0.0),
            )
            self.activity_log.append(entry)


# Global instance
activity_tracker = ActivityTracker()
