import customtkinter as ctk
import os
import json
from datetime import datetime, timedelta
from app.utils.config import PRAYER_NAMES

# ---------------------------
# Constants and Configuration
# ---------------------------

STATUS_OPTIONS = ["Completed", "Late", "Not Completed"]
STATUS_COLORS = {
    "Completed": "green",
    "Late": "orange",
    "Not Completed": "gray"
}
STATUS_FILE = "../models/prayer_status.json"


# ---------------------------
# Data Handling Functions
# ---------------------------

def load_status_data():
    """Load saved prayer status data from JSON file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_status_data(data):
    """Save updated prayer status data to file."""
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_day_name(date_obj):
    """Get day name (e.g. Monday, Tuesday) for a date."""
    return date_obj.strftime("%A")


# ---------------------------
# Main Calendar View Function
# ---------------------------

def open_calendar_view(root_frame, get_today_times_callback, switch_to_dashboard):
    """
    Create and display the 7-day prayer calendar UI.

    Args:
        root_frame: Parent tkinter frame.
        get_today_times_callback: Function to fetch today's prayer times.
        switch_to_dashboard: Function to switch back to dashboard.
    """
    frame = ctk.CTkFrame(root_frame, fg_color="transparent")
    frame.pack(fill="both", expand=True)

    title = ctk.CTkLabel(
        frame, 
        text="7-Day Prayer Calendar", 
        font=ctk.CTkFont(size=22, weight="bold")
    )
    title.pack(pady=10)

    content = ctk.CTkScrollableFrame(frame, fg_color="transparent", width=360, height=350)
    content.pack(pady=10, padx=20)

    today = datetime.now().date()
    all_status = load_status_data()
    today_times = get_today_times_callback()
    var_refs = {}

    # Render calendar for 7 days
    for i in range(7):
        date = today + timedelta(days=i)
        render_day_section(content, date, today, today_times, all_status, var_refs, root_frame)

    # Save and back button row
    button_row = ctk.CTkFrame(frame, fg_color="transparent")
    button_row.pack(pady=15)

    def save_and_back():
        """Save status data and switch back to dashboard."""
        updated = {k: var.get() for k, var in var_refs.items()}
        save_status_data(updated)
        frame.pack_forget()
        switch_to_dashboard()

    back_btn = ctk.CTkButton(button_row, text="Back to Dashboard", command=save_and_back)
    back_btn.pack()

    return frame


# ---------------------------
# Subcomponents and Helpers
# ---------------------------

def render_day_section(content, date, today, today_times, all_status, var_refs, root_frame):
    """Render one day's row of prayer status buttons."""
    date_str = date.strftime("%Y-%m-%d")
    display_date = date.strftime("%d %B - ") + get_day_name(date)

    day_label = ctk.CTkLabel(content, text=display_date, font=ctk.CTkFont(size=16, weight="bold"))
    day_label.pack(pady=(10 if date != today else 5, 5), anchor="w", padx=10)

    for prayer in PRAYER_NAMES:
        key = f"{date_str}_{prayer}"
        status = all_status.get(key, "Not Completed")
        var = ctk.StringVar(value=status)
        var_refs[key] = var

        disable = should_disable_button(date, today, today_times.get(prayer))

        row = ctk.CTkFrame(content, fg_color="#2a2a2a")
        row.pack(fill="x", padx=10, pady=3)

        prayer_label = ctk.CTkLabel(row, text=prayer, width=60, anchor="w")
        prayer_label.pack(side="left", padx=10)

        btn = ctk.CTkButton(
            row,
            textvariable=var,
            fg_color=STATUS_COLORS[var.get()],
            state="disabled" if disable else "normal",
            width=140
        )
        btn.pack(side="right", padx=10)

        def bind_btn(v=var, b=btn):
            b.configure(command=lambda: show_dropdown(v, b, root_frame))
        bind_btn()


def should_disable_button(date, today, prayer_time_str):
    """Determine if a button should be disabled based on date and time."""
    if date > today:
        return True
    if date == today:
        if not prayer_time_str:
            return True
        now_time = datetime.now().time()
        prayer_time = datetime.strptime(prayer_time_str, "%H:%M").time()
        return now_time < prayer_time
    return False


def show_dropdown(var, btn, root_frame):
    """Show a dropdown below a button to select prayer status."""
    dropdown = ctk.CTkFrame(btn.master.master, fg_color="#222", corner_radius=8)
    x = btn.winfo_rootx() - root_frame.winfo_rootx()
    y = btn.winfo_rooty() - root_frame.winfo_rooty() + 30
    dropdown.place(x=x, y=y)

    for option in STATUS_OPTIONS:
        def select(opt=option):
            var.set(opt)
            btn.configure(fg_color=STATUS_COLORS[opt])
            dropdown.destroy()

        opt_btn = ctk.CTkButton(dropdown, text=option, width=120, command=select)
        opt_btn.pack(pady=2, padx=5)
