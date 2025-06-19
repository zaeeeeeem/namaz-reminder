# app/views/main_view.py

# Standard library imports
import queue
from datetime import datetime

# Third-party imports
import customtkinter as ctk

# Local application imports reflecting the new structure
from app.utils.config import START_MINIMIZED, ASSETS_DIR
from app.utils.utils import (
    load_prayer_times,
    save_prayer_times,
    get_next_prayer_info,
    logging
)
from app.services.notifier import show_notification_popup
from app.services.prayer_calendar import open_calendar_view

# View factory function imports
from app.views.dashboard_view import create_dashboard_view
from app.views.settings_view import create_settings_view
from app.views.chatbot_view import create_chatbot_view


class MainView:
    """
    The main view of the application, acting as a controller for all other UI components.
    """

    def __init__(self, scheduler):
        """
        Initializes the main application window, creates all frames, and starts the event loop.

        Args:
            scheduler: An instance of the ReminderScheduler service.
        """
        self.scheduler = scheduler

        # --- Main Window Setup ---
        self.app = ctk.CTk()
        self.app.title("Namaz Reminder")
        self.app.geometry("400x580")
        try:
            self.app.iconbitmap(f"{ASSETS_DIR}/app_icon.ico")
        except Exception as e:
            logging.warning(f"Could not load window icon: {e}")
        self.app.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # --- Application State ---
        self.prayer_times = load_prayer_times()
        self.frames = {}
        # These attributes will be populated by the view factory functions
        self.prayer_entries = {}
        self.clock_label = None
        self.countdown_label = None
        self.prayer_labels = {}

        # --- Build and Display UI ---
        self._create_all_views()
        self.show_frame("dashboard")

        # --- Start Persistent Processes ---
        self.update_dashboard_display()
        self.process_scheduler_queue()
        self.app.protocol("WM_DELETE_WINDOW", self.hide_window)

        if START_MINIMIZED:
            self.app.withdraw()

        self.app.mainloop()

    def _create_all_views(self):
        """
        Initializes all the different views (frames) of the application.
        """
        logging.info("Creating UI views...")
        self.frames["dashboard"] = create_dashboard_view(self.app, self)
        self.frames["settings"] = create_settings_view(self.app, self)
        self.frames["chatbot"] = create_chatbot_view(self.app, self)
        logging.info("UI views created successfully.")

    def show_frame(self, frame_name):
        """
        Hides all other frames and shows the requested frame.

        Args:
            frame_name (str): The key for the frame to be displayed.
        """
        if frame_name == "settings":
            self.load_times_into_settings_entries()

        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[frame_name].pack(fill="both", expand=True)

    def open_calendar_page(self):
        """
        Dynamically creates and displays the calendar view.
        """
        # This view is created on-demand rather than at startup
        self.frames["calendar"] = open_calendar_view(
            root_frame=self.app,
            get_today_times_callback=self.scheduler.get_today_times,
            switch_to_dashboard=lambda: self.show_frame("dashboard")
        )
        self.show_frame("calendar")

    def save_new_times(self):
        """
        Validates and saves the prayer times entered in the settings view.
        """
        new_times = {}
        for name, entry in self.prayer_entries.items():
            time_str = entry.get()
            try:
                datetime.strptime(time_str, '%H:%M')
                new_times[name] = time_str
            except ValueError:
                logging.error(f"Invalid time format for {name}: {time_str}. Not saving.")
                # Consider showing a UI error message here
                return

        save_prayer_times(new_times)
        self.prayer_times = new_times
        self.scheduler.reload_times()
        logging.info("GUI saved new times and reloaded scheduler.")
        self.show_frame("dashboard")

    def load_times_into_settings_entries(self):
        """
        Populates the settings view entry fields with the currently loaded prayer times.
        """
        for name, entry in self.prayer_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self.prayer_times.get(name, "00:00"))

    def update_dashboard_display(self):
        """
        Updates the clock, countdown, and prayer time highlights on the dashboard every second.
        """
        self.clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        next_prayer, countdown = get_next_prayer_info(self.prayer_times)
        if next_prayer != "N/A":
            self.countdown_label.configure(text=f"Next prayer: {next_prayer} in {countdown}")
        else:
            self.countdown_label.configure(text="No prayer times set.")

        for name, (name_label, time_label) in self.prayer_labels.items():
            time_label.configure(text=self.prayer_times.get(name, "00:00"))
            text_color = "cyan" if name == next_prayer else "white"
            name_label.configure(text_color=text_color)
            time_label.configure(text_color=text_color)

        self.app.after(1000, self.update_dashboard_display)

    def process_scheduler_queue(self):
        """
        Checks the queue for notification requests from the scheduler service.
        """
        try:
            message = self.scheduler.notification_queue.get_nowait()
            msg_type, data = message
            if msg_type == 'show_notification':
                prayer_name = data
                logging.info(f"GUI received request to show notification for {prayer_name}")
                show_notification_popup(
                    prayer_name=prayer_name,
                    offered_callback=lambda: self.scheduler.acknowledge_prayer(prayer_name),
                    snooze_callback=lambda: self.scheduler.snooze_prayer(prayer_name)
                )
        except queue.Empty:
            pass  # No message in queue, which is normal
        finally:
            self.app.after(100, self.process_scheduler_queue)

    # --- Window and System Tray Management ---

    def hide_window(self):
        """Hides the main window to the system tray."""
        self.app.withdraw()
        logging.info("Window hidden to system tray.")

    def schedule_show_window(self):
        """Thread-safe method to request the main thread to show the window."""
        self.app.after(0, self._show_window_on_main_thread)

    def _show_window_on_main_thread(self):
        """Shows the main window. This method must only be called by the main thread."""
        self.app.deiconify()
        self.app.lift()
        self.app.focus_force()
        logging.info("Window shown from system tray.")