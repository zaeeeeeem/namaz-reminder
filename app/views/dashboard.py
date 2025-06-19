import customtkinter as ctk
from datetime import datetime
from app.utils.config import PRAYER_NAMES


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, prayer_times, **kwargs):
        super().__init__(master, **kwargs)
        self.prayer_times = prayer_times
        self.prayer_labels = {}
        self.create_widgets()

    def create_widgets(self):
        title = ctk.CTkLabel(self, text="Namaz Reminder", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(20, 10))

        self.clock_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=40, family="Consolas"))
        self.clock_label.pack(pady=10)

        self.countdown_label = ctk.CTkLabel(self, text="Loading...", font=ctk.CTkFont(size=16), text_color="cyan")
        self.countdown_label.pack(pady=(0, 20))

        times_grid = ctk.CTkFrame(self)
        times_grid.pack(pady=10, padx=20, fill="x")

        for i, name in enumerate(PRAYER_NAMES):
            name_label = ctk.CTkLabel(times_grid, text=name, font=ctk.CTkFont(size=16, weight="bold"))
            name_label.grid(row=i, column=0, sticky="w", padx=15, pady=8)

            time_label = ctk.CTkLabel(times_grid, text=self.prayer_times.get(name, "00:00"),
                                      font=ctk.CTkFont(size=16))
            time_label.grid(row=i, column=1, sticky="e", padx=15, pady=8)

            self.prayer_labels[name] = (name_label, time_label)

        times_grid.columnconfigure(0, weight=1)
        times_grid.columnconfigure(1, weight=1)

    def update_display(self, next_prayer=None):
        self.clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        for name, (name_label, time_label) in self.prayer_labels.items():
            time_label.configure(text=self.prayer_times.get(name, "00:00"))
            if name == next_prayer:
                name_label.configure(text_color="cyan")
                time_label.configure(text_color="cyan")
            else:
                name_label.configure(text_color="white")
                time_label.configure(text_color="white")