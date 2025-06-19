import customtkinter as ctk
from PIL import Image
import logging


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, prayer_times, **kwargs):
        super().__init__(master, **kwargs)
        self.prayer_times = prayer_times
        self.prayer_entries = {}
        self.create_widgets()

    def create_widgets(self):
        try:
            pil_image = Image.open("assets/icon.png")
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
            ctk.CTkLabel(self, image=ctk_image, text="").pack(pady=(10, 0))
        except FileNotFoundError:
            logging.warning("icon.png not found in assets")

        title = ctk.CTkLabel(self, text="Set Times", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)

        for name in self.prayer_times:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(pady=8, padx=40, fill="x")

            ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=16), width=80, anchor="w").pack(side="left")

            entry = ctk.CTkEntry(row_frame, font=ctk.CTkFont(size=14), justify="center", width=100)
            entry.pack(side="right")
            self.prayer_entries[name] = entry

    def load_times(self):
        for name, entry in self.prayer_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self.prayer_times.get(name, "00:00"))

    def get_entries(self):
        return {name: entry.get() for name, entry in self.prayer_entries.items()}