# app/views/dashboard_view.py

import customtkinter as ctk
from app.utils.config import PRAYER_NAMES

def create_dashboard_view(parent, app_controller):
    """
    Creates and returns the main dashboard frame.

    Args:
        parent (ctk.CTk): The parent widget (the main app window).
        app_controller (MainView): The instance of the main application view to access its methods and attributes.
    """
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # --- Title ---
    title = ctk.CTkLabel(frame, text="Namaz Reminder", font=ctk.CTkFont(size=28, weight="bold"))
    title.pack(pady=(20, 10))

    # --- Clock and Countdown Labels ---
    # These are configured in the main view's update loop
    app_controller.clock_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=40, family="Consolas"))
    app_controller.clock_label.pack(pady=10)

    app_controller.countdown_label = ctk.CTkLabel(frame, text="Loading...", font=ctk.CTkFont(size=16), text_color="cyan")
    app_controller.countdown_label.pack(pady=(0, 20))

    # --- Prayer Times Grid ---
    _create_prayer_times_grid(frame, app_controller)

    # --- Navigation Buttons ---
    set_times_button = ctk.CTkButton(frame, text="Set Prayer Times", command=lambda: app_controller.show_frame("settings"))
    set_times_button.pack(pady=10, padx=40, fill="x")

    calendar_button = ctk.CTkButton(frame, text="Prayer Calendar", command=app_controller.open_calendar_page)
    calendar_button.pack(pady=10, padx=40, fill="x")

    ai_chat_button = ctk.CTkButton(frame, text="Ask Islamic Assistant", command=lambda: app_controller.show_frame("chatbot"))
    ai_chat_button.pack(pady=10, padx=40, fill="x")

    return frame

def _create_prayer_times_grid(parent, app_controller):
    """
    Creates the grid that displays the prayer names and times.

    Args:
        parent (ctk.CTkFrame): The parent frame for this grid.
        app_controller (MainView): The main application controller to access its attributes.
    """
    times_grid = ctk.CTkFrame(parent)
    times_grid.pack(pady=10, padx=20, fill="x")
    times_grid.columnconfigure((0, 1), weight=1)

    # We initialize the labels and store them on the app_controller
    # so the main update loop can access and configure them later.
    app_controller.prayer_labels = {}
    for i, name in enumerate(PRAYER_NAMES):
        name_label = ctk.CTkLabel(times_grid, text=name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=i, column=0, sticky="w", padx=15, pady=8)

        # Get initial time from the prayer_times dictionary stored in the controller
        initial_time = app_controller.prayer_times.get(name, "00:00")
        time_label = ctk.CTkLabel(times_grid, text=initial_time, font=ctk.CTkFont(size=16))
        time_label.grid(row=i, column=1, sticky="e", padx=15, pady=8)

        app_controller.prayer_labels[name] = (name_label, time_label)