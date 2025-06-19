# app/utils/utils.py

"""
This module provides utility functions for the application, including
file I/O for prayer times and logs, time calculations, and logging setup.
"""

import json
import os
import logging
from datetime import datetime, timedelta

# Use the refactored config module for all constants
from app.utils import config

# --- Logging Configuration ---
# Set up a basic logger for the application.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s - %(message)s'
)


# --- Prayer Time File Operations ---

def load_prayer_times():
    """
    Loads prayer times from the user_times.json file.

    Returns:
        dict: A dictionary of prayer names to times (HH:MM).
              Returns a default dict with "00:00" if the file is not found or corrupt.
    """
    if os.path.exists(config.USER_TIMES_FILE):
        try:
            with open(config.USER_TIMES_FILE, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read or parse {config.USER_TIMES_FILE}: {e}")
    # Return default values if file doesn't exist or is invalid
    return {name: "00:00" for name in config.PRAYER_NAMES}


def save_prayer_times(times):
    """
    Saves the provided prayer times dictionary to the user_times.json file.

    Args:
        times (dict): A dictionary of prayer names to times (HH:MM).

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        # os.makedirs works with pathlib objects and handles directory creation
        os.makedirs(os.path.dirname(config.USER_TIMES_FILE), exist_ok=True)
        with open(config.USER_TIMES_FILE, 'w') as f:
            json.dump(times, f, indent=4)
        logging.info("Prayer times saved successfully.")
        return True
    except IOError as e:
        logging.error(f"Error writing to {config.USER_TIMES_FILE}: {e}")
        return False


# --- User Action Logging ---

def log_user_action(action_type, prayer_name=None, extra_info=None):
    """
    Appends a log entry to the user_logs.json file.

    Args:
        action_type (str): The type of action being logged (e.g., 'notified', 'offered').
        prayer_name (str, optional): The name of the prayer associated with the action. Defaults to None.
        extra_info (dict, optional): Any extra key-value pairs for more details. Defaults to None.
    """
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action_type,
        "prayer": prayer_name,
        "details": extra_info or {}
    }

    logs = []
    if os.path.exists(config.USER_LOG_FILE):
        try:
            with open(config.USER_LOG_FILE, 'r') as f:
                existing_data = json.load(f)
                # Ensure we are appending to a list, even if the file is malformed
                if isinstance(existing_data, list):
                    logs = existing_data
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Could not read logs from {config.USER_LOG_FILE}: {e}. Starting a new log.")

    logs.append(log_entry)

    try:
        os.makedirs(os.path.dirname(config.USER_LOG_FILE), exist_ok=True)
        with open(config.USER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write logs to {config.USER_LOG_FILE}: {e}")


# --- Time Calculation Logic ---

def get_next_prayer_info(current_times):
    """
    Calculates the next upcoming prayer and the time remaining until it.

    Args:
        current_times (dict): A dictionary of prayer names to times (HH:MM).

    Returns:
        tuple: A tuple containing (next_prayer_name, countdown_string).
               Returns ("N/A", "N/A") if no times are set.
    """
    now = datetime.now()
    prayer_times_today = []

    for name, time_str in current_times.items():
        try:
            prayer_dt = datetime.strptime(time_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            prayer_times_today.append((name, prayer_dt))
        except (ValueError, TypeError):
            continue  # Skip invalid time formats or None values

    prayer_times_today.sort(key=lambda x: x[1])

    # Find the next prayer that is later today
    for name, prayer_dt in prayer_times_today:
        if prayer_dt > now:
            time_diff = prayer_dt - now
            return name, str(timedelta(seconds=int(time_diff.total_seconds())))

    # If all of today's prayers have passed, the next is the first one tomorrow
    if prayer_times_today:
        first_prayer_name, first_prayer_dt = prayer_times_today[0]
        next_prayer_dt = first_prayer_dt + timedelta(days=1)
        time_diff = next_prayer_dt - now
        return first_prayer_name, str(timedelta(seconds=int(time_diff.total_seconds())))

    return "N/A", "N/A"

def get_day_name(date_obj: datetime.date) -> str:
    """
    Converts a datetime.date object into the full name of the weekday.

    Args:
        date_obj (datetime.date): The date object to be converted.

    Returns:
        str: The full name of the weekday (e.g., "Friday").
    """
    # .strftime("%A") is the format code for the full weekday name
    return date_obj.strftime("%A")