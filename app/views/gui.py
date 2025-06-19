import customtkinter as ctk
import queue
import threading
from datetime import datetime
from PIL import Image

from app.utils.utils import (
    load_prayer_times,
    save_prayer_times,
    get_next_prayer_info,
    logging
)
from app.services.notifier import show_notification_popup
from app.services.prayer_calendar import open_calendar_view
from app.services import gemini_client
from app.utils.config import PRAYER_NAMES, START_MINIMIZED

from app.views.dashboard import DashboardView  # ✅ New class import
from app.views.settings import create_settings_frame
from app.views.chatbot import create_chatbot_frame


class NamazReminderApp:
    """Main GUI controller for the Namaz Reminder application."""

    def __init__(self, scheduler):
        self.scheduler = scheduler

        self.app = ctk.CTk()
        self.app.title("Namaz Reminder")
        self.app.geometry("400x580")
        self.app.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.prayer_times = load_prayer_times()
        self.frames = {}

        # Use DashboardView class instead of frame function
        dashboard_view = DashboardView(self.app, self.prayer_times)
        self.clock_label = dashboard_view.clock_label
        self.countdown_label = dashboard_view.countdown_label
        self.prayer_labels = dashboard_view.prayer_labels
        self.frames["dashboard"] = dashboard_view

        self.frames["settings"] = create_settings_frame(self)
        self.frames["chatbot"] = create_chatbot_frame(self)

        self.show_frame("dashboard")

        self.update_dashboard_display()
        self.process_scheduler_queue()

        self.app.protocol("WM_DELETE_WINDOW", self.hide_window)

        if START_MINIMIZED:
            self.app.withdraw()

        self.app.mainloop()

    def show_frame(self, frame_name):
        """Show the selected frame and hide others."""
        if frame_name == "settings":
            self.load_times_into_settings_entries()
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[frame_name].pack(fill="both", expand=True)

    def open_calendar_page(self):
        """Open the prayer calendar view."""
        self.frames["calendar"] = open_calendar_view(
            root_frame=self.app,
            get_today_times_callback=self.scheduler.get_today_times,
            switch_to_dashboard=lambda: self.show_frame("dashboard")
        )
        self.show_frame("calendar")

    def load_times_into_settings_entries(self):
        """Load prayer times into entry fields in the settings frame."""
        for name, entry in self.prayer_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self.prayer_times.get(name, "00:00"))

    def save_new_times(self):
        """Validate and save updated prayer times from the settings frame."""
        new_times = {}
        for name, entry in self.prayer_entries.items():
            time_str = entry.get()
            try:
                datetime.strptime(time_str, '%H:%M')
                new_times[name] = time_str
            except ValueError:
                logging.error(f"Invalid time format for {name}: {time_str}. Not saving.")
                return

        save_prayer_times(new_times)
        self.prayer_times = new_times
        self.scheduler.reload_times()
        logging.info("GUI saved new times and reloaded scheduler.")
        self.show_frame("dashboard")

    def update_dashboard_display(self):
        """Update clock and prayer countdown on the dashboard."""
        self.clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        next_prayer, countdown = get_next_prayer_info(self.prayer_times)

        if next_prayer != "N/A":
            self.countdown_label.configure(text=f"Next prayer: {next_prayer} in {countdown}")
        else:
            self.countdown_label.configure(text="No prayer times set.")

        for name, (name_label, time_label) in self.prayer_labels.items():
            time_label.configure(text=self.prayer_times.get(name, "00:00"))
            color = "cyan" if name == next_prayer else "white"
            name_label.configure(text_color=color)
            time_label.configure(text_color=color)

        self.app.after(1000, self.update_dashboard_display)

    def process_scheduler_queue(self):
        """Listen for messages from the scheduler and show notifications."""
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
            pass
        finally:
            self.app.after(100, self.process_scheduler_queue)

    def hide_window(self):
        """Hide the main window to the system tray."""
        self.app.withdraw()
        logging.info("Window hidden to system tray.")

    def schedule_show_window(self):
        """Thread-safe method to request the main thread to show the window."""
        logging.info("Show Window")
        self.app.after(0, self._show_window_on_main_thread)

    def _show_window_on_main_thread(self):
        """Show the main window from system tray."""
        self.app.deiconify()
        self.app.lift()
        self.app.focus_force()
        logging.info("Window shown from system tray.")
