# utils.py

import json
import os
from datetime import datetime, timedelta
import logging

from config import USER_TIMES_FILE, USER_LOG_FILE, PRAYER_NAMES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_prayer_times():
    try:
        if os.path.exists(USER_TIMES_FILE):
            with open(USER_TIMES_FILE, 'r') as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Could not read or parse user_times.json: {e}. Returning defaults.")

    return {name: "00:00" for name in PRAYER_NAMES}


def save_prayer_times(times):
    try:
        # Ensure the 'data' directory exists
        os.makedirs(os.path.dirname(USER_TIMES_FILE), exist_ok=True)
        with open(USER_TIMES_FILE, 'w') as f:
            json.dump(times, f, indent=4)
        logging.info("Prayer times saved successfully.")
        return True
    except IOError as e:
        logging.error(f"Error saving prayer times: {e}")
        return False


def log_user_action(action_type, prayer_name=None, extra_info=None):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action_type,
        "prayer": prayer_name,
        "details": extra_info
    }

    logs = []
    try:
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, 'r') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    logs = existing_data
                else:
                    logging.warning("user_logs.json was not a list. Starting fresh.")
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Could not read or parse user_logs.json: {e}. Starting a new log.")

    logs.append(log_entry)

    try:
        os.makedirs(os.path.dirname(USER_LOG_FILE), exist_ok=True)
        with open(USER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write to user_logs.json: {e}")


def get_next_prayer_info(current_times):
    now = datetime.now()

    today_prayer_times = []
    for name, time_str in current_times.items():
        try:
            prayer_dt = datetime.strptime(time_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            today_prayer_times.append((name, prayer_dt))
        except ValueError:
            continue

    today_prayer_times.sort(key=lambda x: x[1])

    for name, prayer_dt in today_prayer_times:
        if prayer_dt > now:
            time_diff = prayer_dt - now
            return name, str(timedelta(seconds=int(time_diff.total_seconds())))

    if today_prayer_times:
        first_prayer_name, first_prayer_dt = today_prayer_times[0]
        next_prayer_dt = first_prayer_dt + timedelta(days=1)
        time_diff = next_prayer_dt - now
        return first_prayer_name, str(timedelta(seconds=int(time_diff.total_seconds())))

    return "N/A", "N/A"