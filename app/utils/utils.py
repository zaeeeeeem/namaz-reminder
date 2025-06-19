import json
import os
import logging
from datetime import datetime, timedelta
from app.utils.config import USER_TIMES_FILE, USER_LOG_FILE, PRAYER_NAMES

# -------------------------
# Logging Configuration
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# -------------------------
# Prayer Time Functions
# -------------------------

def load_prayer_times():
    """
    Load user-defined prayer times from file.
    Returns default empty times if file missing or unreadable.
    """
    if os.path.exists(USER_TIMES_FILE):
        try:
            with open(USER_TIMES_FILE, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read {USER_TIMES_FILE}: {e}")
    return {name: "00:00" for name in PRAYER_NAMES}


def save_prayer_times(times):
    """
    Save prayer times to user file.
    
    Args:
        times (dict): Prayer name → HH:MM time

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(USER_TIMES_FILE), exist_ok=True)
        with open(USER_TIMES_FILE, 'w') as f:
            json.dump(times, f, indent=4)
        logging.info("Prayer times saved successfully.")
        return True
    except IOError as e:
        logging.error(f"Error writing to {USER_TIMES_FILE}: {e}")
        return False


# -------------------------
# User Log Functions
# -------------------------

def log_user_action(action_type, prayer_name=None, extra_info=None):
    """
    Append a new user action (like prayer offered/snoozed) to the logs.

    Args:
        action_type (str): e.g., 'Offered', 'Snoozed'
        prayer_name (str): Name of the prayer (optional)
        extra_info (str): Optional additional context
    """
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action_type,
        "prayer": prayer_name,
        "details": extra_info
    }

    logs = []
    if os.path.exists(USER_LOG_FILE):
        try:
            with open(USER_LOG_FILE, 'r') as f:
                existing_data = json.load(f)
                logs = existing_data if isinstance(existing_data, list) else []
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Could not read logs: {e}. Starting fresh.")

    logs.append(log_entry)

    try:
        os.makedirs(os.path.dirname(USER_LOG_FILE), exist_ok=True)
        with open(USER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write logs: {e}")


# -------------------------
# Prayer Calculation Utility
# -------------------------

def get_next_prayer_info(current_times):
    """
    Determine the next upcoming prayer from current time.

    Args:
        current_times (dict): Prayer name → HH:MM time

    Returns:
        tuple: (prayer_name, time_until as HH:MM:SS string)
    """
    now = datetime.now()
    prayer_times_today = []

    for name, time_str in current_times.items():
        try:
            prayer_dt = datetime.strptime(time_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            prayer_times_today.append((name, prayer_dt))
        except ValueError:
            continue

    prayer_times_today.sort(key=lambda x: x[1])

    for name, prayer_dt in prayer_times_today:
        if prayer_dt > now:
            time_diff = prayer_dt - now
            return name, str(timedelta(seconds=int(time_diff.total_seconds())))

    if prayer_times_today:
        first_prayer_name, first_prayer_dt = prayer_times_today[0]
        next_prayer_dt = first_prayer_dt + timedelta(days=1)
        time_diff = next_prayer_dt - now
        return first_prayer_name, str(timedelta(seconds=int(time_diff.total_seconds())))

    return "N/A", "N/A"


# -------------------------
# Misc Utility
# -------------------------

def get_day_name(date_str):
    """
    Given a date string in format YYYY-MM-DD, return the weekday name.

    Args:
        date_str (str): e.g., "2025-06-20"

    Returns:
        str: Day of the week or "Invalid date"
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A")
    except ValueError:
        return "Invalid date"
