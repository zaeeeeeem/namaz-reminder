# app/utils/config.py

"""
This file contains all the configuration constants for the application.
By centralizing them here, we can easily manage settings without
hardcoding them throughout the project.
"""

from pathlib import Path

# --- Core Application Settings ---
PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
START_MINIMIZED = False # Set to True to start directly in the system tray

# --- Base Directory ---
# Defines the absolute path to the project's root directory (namaz-reminder/)
# This makes all other file paths stable and reliable.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Path Definitions ---
# All paths are now constructed from the BASE_DIR for robustness.
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = APP_DIR / "assets"
MODELS_DIR = APP_DIR / "models"
DATA_DIR = BASE_DIR / "data" # For runtime data if needed

# --- Model File Paths ---
USER_TIMES_FILE = MODELS_DIR / "user_times.json"
USER_LOG_FILE = MODELS_DIR / "user_logs.json"
PRAYER_STATUS_FILE = MODELS_DIR / "prayer_status.json"

# --- Asset File Paths ---
AZAN_SOUND_FILE = ASSETS_DIR / "azan.mp3"
APP_ICON_ICO = ASSETS_DIR / "app_icon.ico"
APP_ICON_PNG = ASSETS_DIR / "icon.png"

# --- Scheduler Settings ---
DEFAULT_SNOOZE_MINUTES = 1
SCHEDULER_CHECK_INTERVAL_SECONDS = 30

# --- Calendar View Settings ---
STATUS_OPTIONS = ["Completed", "Late", "Not Completed"]
STATUS_COLORS = {
    "Completed": "#228B22",  # ForestGreen
    "Late": "#FFA500",      # Orange
    "Not Completed": "#808080" # Gray
}