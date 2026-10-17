from datetime import datetime
import time

def get_current_datetime() -> str:
    """
    Get the current local date, time, day of the week, and timezone.
    Always use this when questions relate to current events, today's date, deadlines, or schedules.
    """
    now = datetime.now()
    tz_name = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    return (
        f"Current Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Current Time: {now.strftime('%H:%M:%S')}\n"
        f"Timezone: {tz_name}\n"
        f"ISO 8601: {now.isoformat()}"
    )
