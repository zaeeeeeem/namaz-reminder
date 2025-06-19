# app/services/prayer_calendar.py
"""
This module acts as a service for the prayer calendar feature. It handles
data operations (loading/saving status) and orchestrates the UI rendering.
"""

import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta

from app.utils import config
from app.utils.utils import logging
from app.views import calendar_view  # Import the new view module


# --- Data Handling Functions ---

def _load_status_data():
    """
    Loads the prayer status data from its JSON file in the models directory.
    """
    if os.path.exists(config.PRAYER_STATUS_FILE):
        try:
            with open(config.PRAYER_STATUS_FILE, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read prayer status file: {e}")
    return {}


def _save_status_data(data):
    """
    Saves the provided prayer status data to its JSON file.
    """
    try:
        with open(config.PRAYER_STATUS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logging.info("Prayer status data saved successfully.")
    except IOError as e:
        logging.error(f"Failed to save prayer status data: {e}")


# --- Logic Helper Functions ---

def _should_disable_button(date, today, prayer_time_str):
    """
    Determines if a prayer status button should be disabled (i.e., is in the future).
    """
    if date > today:
        return True
    if date == today:
        if not prayer_time_str:  # If no time is set for today, disable
            return True
        now_time = datetime.now().time()
        prayer_time = datetime.strptime(prayer_time_str, "%H:%M").time()
        return now_time < prayer_time
    return False  # For all past dates


# --- Main Service Function ---

def open_calendar_view(root_frame, get_today_times_callback, switch_to_dashboard):
    """
    Creates and displays the 7-day prayer calendar view.

    Args:
        root_frame (ctk.CTk): The main application window.
        get_today_times_callback (function): A function that returns today's prayer times.
        switch_to_dashboard (function): A function to call to return to the dashboard.

    Returns:
        ctk.CTkFrame: The main frame for the calendar view.
    """
    frame = ctk.CTkFrame(root_frame, fg_color="transparent")

    title = ctk.CTkLabel(frame, text="7-Day Prayer Calendar", font=ctk.CTkFont(size=22, weight="bold"))
    title.pack(pady=10)

    # --- Prepare data for the view ---
    today = datetime.now().date()
    all_statuses = _load_status_data()
    today_times = get_today_times_callback()
    dates_data = []
    for i in range(7):
        date = today + timedelta(days=i)
        dates_data.append({
            "date": date,
            "is_today": date == today,
            "statuses": all_statuses,
            "prayer_disabled_status": {
                prayer: _should_disable_button(date, today, today_times.get(prayer))
                for prayer in config.PRAYER_NAMES
            }
        })

    status_vars = {}  # This will be populated by the view

    # --- Build the UI using the view module ---
    def show_dropdown_callback(var, btn):
        """Wrapper to call the dropdown display function from the view."""
        calendar_view.display_status_dropdown(root_frame, var, btn)

    calendar_view.build_calendar_frame(frame, dates_data, status_vars, show_dropdown_callback)

    # --- Save and Back Button ---
    def save_and_back():
        """Saves all current statuses and switches back to the dashboard."""
        updated_data = {key: var.get() for key, var in status_vars.items()}
        # Merge with existing data to preserve history
        final_data = all_statuses
        final_data.update(updated_data)
        _save_status_data(final_data)

        frame.destroy()  # Destroy the frame to ensure it's fresh next time
        switch_to_dashboard()

    back_btn = ctk.CTkButton(frame, text="Back to Dashboard", command=save_and_back)
    back_btn.pack(pady=15)

    return frame