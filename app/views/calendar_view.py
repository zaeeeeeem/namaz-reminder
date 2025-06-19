# app/views/calendar_view.py
"""
This module is responsible for creating and rendering all the UI widgets
for the 7-day prayer calendar view.
"""

import customtkinter as ctk
from datetime import datetime, timedelta

from app.utils import config
from app.utils.utils import get_day_name  # We will move get_day_name to utils


def build_calendar_frame(parent, dates_data, status_vars, show_dropdown_callback):
    """
    Constructs the main scrollable frame and populates it with 7 days of data.

    Args:
        parent (ctk.CTkFrame): The root frame to build the calendar inside.
        dates_data (list): A list of dictionaries, each containing info for a single day.
        status_vars (dict): A dictionary to store the StringVar for each prayer status.
        show_dropdown_callback (function): The function to call when a status button is clicked.
    """
    content = ctk.CTkScrollableFrame(parent, fg_color="transparent", width=360, height=350)
    content.pack(pady=10, padx=20)

    for day_info in dates_data:
        _render_day_section(content, day_info, status_vars, show_dropdown_callback)


def _render_day_section(parent, day_info, status_vars, show_dropdown_callback):
    """
    Renders a single day's section, including the date label and prayer status buttons.

    Args:
        parent (ctk.CTkFrame): The scrollable frame to render into.
        day_info (dict): Contains all necessary data for rendering one day.
        status_vars (dict): The dictionary to store created StringVars.
        show_dropdown_callback (function): The function to call when a status button is clicked.
    """
    date_str = day_info["date"].strftime("%d %B - ") + get_day_name(day_info["date"])
    day_label = ctk.CTkLabel(parent, text=date_str, font=ctk.CTkFont(size=16, weight="bold"))
    day_label.pack(pady=(10 if day_info["is_today"] else 5, 5), anchor="w", padx=10)

    for prayer in config.PRAYER_NAMES:
        key = f"{day_info['date'].strftime('%Y-%m-%d')}_{prayer}"
        initial_status = day_info["statuses"].get(key, "Not Completed")
        status_var = ctk.StringVar(value=initial_status)
        status_vars[key] = status_var

        row = ctk.CTkFrame(parent, fg_color="#2a2a2a")
        row.pack(fill="x", padx=10, pady=3)

        prayer_label = ctk.CTkLabel(row, text=prayer, width=60, anchor="w")
        prayer_label.pack(side="left", padx=10)

        btn = ctk.CTkButton(
            row,
            textvariable=status_var,
            fg_color=config.STATUS_COLORS[status_var.get()],
            state="disabled" if day_info["prayer_disabled_status"][prayer] else "normal",
            width=140
        )
        btn.pack(side="right", padx=10)

        # Use a lambda to pass the specific variable and button to the callback
        btn.configure(command=lambda v=status_var, b=btn: show_dropdown_callback(v, b))


# In app/views/calendar_view.py, replace the old function with this one:

def display_status_dropdown(parent_frame, status_var, button):
    """
    Creates and displays a true pop-up dropdown menu to change a prayer's status.

    Args:
        parent_frame (ctk.CTk): The absolute root window of the application.
        status_var (ctk.StringVar): The variable tied to the button's text.
        button (ctk.CTkButton): The button that was clicked to position the dropdown.
    """
    # 1. Create a CTkToplevel - a true pop-up window
    dropdown = ctk.CTkToplevel(parent_frame)

    # 2. Remove window decorations (title bar, borders) to make it look like a menu
    dropdown.overrideredirect(True)

    # 3. Get the absolute screen position of the button that was clicked
    x = button.winfo_rootx()
    y = button.winfo_rooty() + button.winfo_height() + 2  # Position it just below the button

    # 4. Place the Toplevel window at that absolute screen position
    dropdown.geometry(f"+{int(x)}+{int(y)}")

    def select_option(option):
        """Callback to set the new status and destroy the dropdown."""
        status_var.set(option)
        button.configure(fg_color=config.STATUS_COLORS[option])
        dropdown.destroy()

    # 5. Create the buttons inside the new Toplevel window
    for option in config.STATUS_OPTIONS:
        opt_btn = ctk.CTkButton(
            dropdown,
            text=option,
            width=button.winfo_width(),  # Make the dropdown buttons the same width as the original
            command=lambda o=option: select_option(o)
        )
        opt_btn.pack(pady=2, padx=2)

    # 6. Make the dropdown disappear if the user clicks away from it
    dropdown.bind("<FocusOut>", lambda event: dropdown.destroy())
    dropdown.focus_set()  # Grab focus so the FocusOut event will work