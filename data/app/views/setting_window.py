import tkinter as tk
from tkinter import ttk


class SettingsWindow:
    """Window for configuring application settings."""

    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Settings")
        self.setup_ui()

    def setup_ui(self):
        # Location settings
        loc_frame = ttk.LabelFrame(self.top, text="Location Settings")
        loc_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(loc_frame, text="Latitude:").grid(row=0, column=0, sticky="e")
        self.lat_entry = ttk.Entry(loc_frame)
        self.lat_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(loc_frame, text="Longitude:").grid(row=1, column=0, sticky="e")
        self.lon_entry = ttk.Entry(loc_frame)
        self.lon_entry.grid(row=1, column=1, padx=5, pady=2)

        # Notification settings
        notif_frame = ttk.LabelFrame(self.top, text="Notification Settings")
        notif_frame.pack(fill=tk.X, padx=10, pady=5)

        self.sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notif_frame, text="Enable Sound",
                        variable=self.sound_var).pack(anchor="w")

        # Save button
        ttk.Button(self.top, text="Save Settings",
                   command=self.save_settings).pack(pady=10)

    def save_settings(self):
        # Save logic here
        self.top.destroy()