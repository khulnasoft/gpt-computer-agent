"""
Integration example showing how to use the improved activity tracking system
with the existing workday summarizer.
"""

import json
from datetime import datetime

# Import the improved activity tracker
from .improved_activity_tracker import generate_activity_summary


def improved_workday_summarizer():
    """
    Enhanced version of the workday summarizer that uses dynamic activity categorization
    instead of hardcoded percentages.
    """

    # Configuration
    SNAPSHOT_INTERVAL = 10  # seconds
    TOTAL_DURATION = 5 * 60  # 5 minutes in seconds
    NUM_ITERATIONS = TOTAL_DURATION // SNAPSHOT_INTERVAL

    print(f"Starting improved workday monitoring for {TOTAL_DURATION//60} minutes...")
    print(f"Taking snapshots every {SNAPSHOT_INTERVAL} seconds")

    # Store all activity data
    activity_log = []

    # Main monitoring loop (simplified for demo)
    for i in range(NUM_ITERATIONS):
        print(f"\n--- Snapshot {i+1}/{NUM_ITERATIONS} ---")

        # In a real implementation, you would capture actual screen data here
        # For this demo, we'll use sample data
        sample_activities = [
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": "Visual Studio Code",
                "window_title": "activity_tracker.py - GPT Computer Agent",
                "content_summary": "Writing Python code for activity tracking system",
                "user_activity": "coding and implementing new features",
            },
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": "Microsoft Teams",
                "window_title": "Team Standup Meeting",
                "content_summary": "Daily team synchronization meeting",
                "user_activity": "participating in team standup discussion",
            },
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": "Chrome",
                "window_title": "GitHub - Pull Requests",
                "content_summary": "Reviewing code changes and pull requests",
                "user_activity": "code review and collaboration",
            },
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": "Slack",
                "window_title": "General - Team Communication",
                "content_summary": "Team chat and quick communications",
                "user_activity": "communicating with team members",
            },
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_name": "YouTube",
                "window_title": "Python Tutorial - Advanced Concepts",
                "content_summary": "Educational video about Python programming",
                "user_activity": "learning new programming techniques",
            },
        ]

        # Add sample activity to log
        activity_log.append(sample_activities[i % len(sample_activities)])

    # Generate the improved summary using dynamic categorization
    print("\nGenerating improved workday summary...")
    summary = generate_activity_summary(activity_log)

    # Display results
    print("\n" + "=" * 50)
    print("📊 IMPROVED WORKDAY SUMMARY")
    print("=" * 50)
    print(f"📅 Date: {summary['date']}")
    print(f"⏱️  Total Tracked: {summary['total_tracked_minutes']} minutes")
    print(f"📱 Apps Used: {len(summary['apps_used'])}")

    print("\n📈 TIME DISTRIBUTION:")
    print("-" * 30)
    for category, data in summary["time_distribution"].items():
        if data["minutes"] > 0:
            print(
                f"• {category.title()}: {data['minutes']} min ({data['percentage']}%)"
            )

    print("\n📋 DETAILED BREAKDOWN:")
    print("-" * 30)
    work_min = summary["summary"]["work_minutes"]
    comm_min = summary["summary"]["communication_minutes"]
    break_min = summary["summary"]["breaks_minutes"]
    uncat_min = summary["summary"]["uncategorized_minutes"]

    print(f"💼 Work: {work_min} minutes")
    print(f"💬 Communication: {comm_min} minutes")
    print(f"☕ Breaks: {break_min} minutes")
    print(f"❓ Uncategorized: {uncat_min} minutes")

    # Calculate productivity score
    total_categorized = work_min + comm_min + break_min + uncat_min
    if total_categorized > 0:
        productive_time = work_min + comm_min
        productivity_score = int((productive_time / total_categorized) * 100)
        print(f"\n🎯 Productivity Score: {productivity_score}%")

        # Provide insights
        if productivity_score >= 80:
            print("🌟 Excellent productivity! You're making great use of your time.")
        elif productivity_score >= 60:
            print("👍 Good productivity. Consider taking more focused work sessions.")
        elif productivity_score >= 40:
            print("⚠️  Moderate productivity. Try to minimize distractions.")
        else:
            print(
                "🔧 Low productivity detected. Consider setting specific goals and taking regular breaks."
            )

    print("\n" + "=" * 50)

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"improved_workday_summary_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump({"activity_log": activity_log, "summary": summary}, f, indent=2)

    print(f"✅ Detailed results saved to: {filename}")

    return summary


if __name__ == "__main__":
    # Run the improved workday summarizer
    improved_workday_summarizer()
