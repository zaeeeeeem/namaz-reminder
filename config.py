# config.py

# List of Namaz names in order
PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

# File paths
USER_TIMES_FILE = "data/user_times.json"
USER_LOG_FILE = "data/user_logs.json"
ASSETS_DIR = "assets"
AZAN_SOUND_FILE = f"{ASSETS_DIR}/azan.mp3" # Make sure you have this file

# App settings
DEFAULT_SNOOZE_MINUTES = 1
SCHEDULER_CHECK_INTERVAL_SECONDS = 30 # Check time every 30 seconds