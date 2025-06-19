import customtkinter as ctk
from app.utils.config import PRAYER_NAMES


def create_settings_frame(app):
    """Create the settings frame for editing and saving prayer times."""

    frame = ctk.CTkFrame(app.app)

    ctk.CTkLabel(frame, text="Edit Prayer Times", font=("Arial", 16)).pack(pady=10)

    app.prayer_entries = {}
    for name in PRAYER_NAMES:
        ctk.CTkLabel(frame, text=name).pack()
        entry = ctk.CTkEntry(frame)
        entry.pack(pady=(0, 10))
        app.prayer_entries[name] = entry

    # Save button
    ctk.CTkButton(frame, text="Save Times", command=app.save_new_times).pack(pady=10)
    ctk.CTkButton(frame, text="Back to Dashboard", command=lambda: app.show_frame("dashboard")).pack()

    return frame
