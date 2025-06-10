# gui.py

import customtkinter as ctk
import queue
from datetime import datetime

from utils import load_prayer_times, save_prayer_times, get_next_prayer_info, logging
from config import PRAYER_NAMES


# We will create notifier.py in the next phase
from notifier import show_notification_popup

class NamazReminderApp:
    def __init__(self, scheduler):
        self.scheduler = scheduler

        # --- App Setup ---
        self.app = ctk.CTk()
        self.app.title("Namaz Reminder")
        self.app.geometry("400x480")
        self.app.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # --- State Management ---
        # **CRITICAL FIX**: Load times at startup and store them. This is our single source of truth.
        self.prayer_times = load_prayer_times()

        # --- Frame Management ---
        self.frames = {}
        self.create_dashboard_frame()
        self.create_settings_frame()

        self.show_frame("dashboard")

        # --- Start Real-time Updates ---
        self.update_dashboard_display()
        self.process_scheduler_queue()

        # Start the main application loop
        self.app.mainloop()

    def create_dashboard_frame(self):
        """Builds the main dashboard screen with the clock, countdown, and prayer list."""
        frame = ctk.CTkFrame(self.app, fg_color="transparent")

        title = ctk.CTkLabel(frame, text="Namaz Reminder", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(20, 10))

        self.clock_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=40, family="Consolas"))
        self.clock_label.pack(pady=10)

        self.countdown_label = ctk.CTkLabel(frame, text="Loading...", font=ctk.CTkFont(size=16), text_color="cyan")
        self.countdown_label.pack(pady=(0, 20))

        times_grid = ctk.CTkFrame(frame)
        times_grid.pack(pady=10, padx=20, fill="x")

        self.prayer_labels = {}
        for i, name in enumerate(PRAYER_NAMES):
            # Left side (Prayer Name)
            name_label = ctk.CTkLabel(times_grid, text=name, font=ctk.CTkFont(size=16, weight="bold"))
            name_label.grid(row=i, column=0, sticky="w", padx=15, pady=8)
            # Right side (Prayer Time)
            time_label = ctk.CTkLabel(times_grid, text=self.prayer_times.get(name, "00:00"), font=ctk.CTkFont(size=16))
            time_label.grid(row=i, column=1, sticky="e", padx=15, pady=8)
            self.prayer_labels[name] = (name_label, time_label)

        times_grid.columnconfigure(0, weight=1)  # <-- WRONG
        times_grid.columnconfigure(1, weight=1)  # <-- CORRECT

        set_times_button = ctk.CTkButton(frame, text="Set Prayer Times", command=lambda: self.show_frame("settings"))
        
        set_times_button.pack(pady=20, padx=40, fill="x")

        self.frames["dashboard"] = frame

    def create_settings_frame(self):
        """Builds the settings screen where the user can input prayer times."""
        frame = ctk.CTkFrame(self.app, fg_color="transparent")

        title = ctk.CTkLabel(frame, text="Set Times", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        self.prayer_entries = {}
        for name in PRAYER_NAMES:
            row_frame = ctk.CTkFrame(frame, fg_color="transparent")
            row_frame.pack(pady=8, padx=40, fill="x")

            name_label = ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=16), width=80, anchor="w")
            name_label.pack(side="left")

            entry = ctk.CTkEntry(row_frame, font=ctk.CTkFont(size=14), justify="center", width=100)
            entry.pack(side="right")
            self.prayer_entries[name] = entry

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=20, padx=40, fill="x")

        save_button = ctk.CTkButton(button_frame, text="Save", command=self.save_new_times)
        save_button.pack(side="left", expand=True, padx=(0, 5))

        back_button = ctk.CTkButton(button_frame, text="Back", fg_color="#555", hover_color="#444",
                                    command=lambda: self.show_frame("dashboard"))
        back_button.pack(side="right", expand=True, padx=(5, 0))

        self.frames["settings"] = frame

    def show_frame(self, frame_name):
        """Brings the requested frame to the front."""
        # **CRITICAL FIX**: Before showing settings, load the current times into the entry fields.
        if frame_name == "settings":
            self.load_times_into_settings_entries()

        for frame in self.frames.values():
            frame.pack_forget()  # Hide all frames
        self.frames[frame_name].pack(fill="both", expand=True)  # Show the one we want

    def load_times_into_settings_entries(self):
        """Ensures the settings page always shows the most recently saved times."""
        for name, entry in self.prayer_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self.prayer_times.get(name, "00:00"))

    def save_new_times(self):
        """Reads values from settings entries, saves them, and updates the app."""
        new_times = {}
        for name, entry in self.prayer_entries.items():
            time_str = entry.get()
            # Basic validation
            try:
                datetime.strptime(time_str, '%H:%M')
                new_times[name] = time_str
            except ValueError:
                logging.error(f"Invalid time format for {name}: {time_str}. Not saving.")
                # You could show a messagebox here for better UX
                return

        # Save to file
        save_prayer_times(new_times)
        # Update the app's internal state
        self.prayer_times = new_times
        # Tell the scheduler to use the new times
        self.scheduler.reload_times()
        logging.info("GUI saved new times and reloaded scheduler.")
        # Go back to the dashboard
        self.show_frame("dashboard")

    def update_dashboard_display(self):
        """Runs every second to update the clock, countdown, and prayer highlights."""
        # Update Clock
        self.clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        # Update Countdown and Highlight
        next_prayer, countdown = get_next_prayer_info(self.prayer_times)
        if next_prayer != "N/A":
            self.countdown_label.configure(text=f"Next prayer: {next_prayer} in {countdown}")
        else:
            self.countdown_label.configure(text="No prayer times set.")

        # Update highlights and times on dashboard
        for name, (name_label, time_label) in self.prayer_labels.items():
            time_label.configure(text=self.prayer_times.get(name, "00:00"))
            if name == next_prayer:
                name_label.configure(text_color="cyan")
                time_label.configure(text_color="cyan")
            else:
                name_label.configure(text_color="white")
                time_label.configure(text_color="white")

        # Schedule the next update
        self.app.after(1000, self.update_dashboard_display)

    def process_scheduler_queue(self):
        """Checks the queue for messages from the scheduler thread."""
        try:
            message = self.scheduler.notification_queue.get_nowait()
            msg_type, data = message

            if msg_type == 'show_notification':
                prayer_name = data
                logging.info(f"GUI received request to show notification for {prayer_name}")
                # This is where we will call the notifier popup in the next phase
                # For now, let's just log it.
                show_notification_popup(
                    prayer_name=prayer_name,
                    offered_callback=lambda: self.scheduler.acknowledge_prayer(prayer_name),
                    snooze_callback=lambda: self.scheduler.snooze_prayer(prayer_name)
                )

            elif msg_type == 'update_status':
                # This message type can be used to force a UI refresh if needed
                # The 1-second loop already handles most cases, but this is good practice
                pass

        except queue.Empty:
            pass  # No message in queue
        finally:
            # Check again after a short delay
            self.app.after(100, self.process_scheduler_queue)