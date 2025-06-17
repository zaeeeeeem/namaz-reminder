# notifier.py

import customtkinter as ctk
import pygame
import threading
import os

from config import AZAN_SOUND_FILE
from utils import logging

def play_azan_sound():
    """Plays the Azan sound in a separate thread to avoid blocking the UI."""
    if not os.path.exists(AZAN_SOUND_FILE):
        logging.warning(f"Audio file not found at: {AZAN_SOUND_FILE}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(AZAN_SOUND_FILE)
        pygame.mixer.music.play()
        logging.info("Azan sound started playing.")
    except Exception as e:
        logging.error(f"Failed to play sound: {e}")


def stop_azan_sound():
    """Stops the currently playing sound."""
    try:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            logging.info("Azan sound stopped.")
    except Exception as e:
        logging.error(f"Failed to stop sound: {e}")

def show_notification_popup(prayer_name, offered_callback, snooze_callback):
    threading.Thread(target=play_azan_sound, daemon=True).start()

    popup = ctk.CTkToplevel()
    popup.title(f"{prayer_name} Reminder")
    popup.geometry("350x180")
    popup.resizable(False, False)

    popup.attributes("-topmost", True)

    def on_offered():
        stop_azan_sound()
        if offered_callback:
            offered_callback()
        popup.destroy()

    def on_snooze():
        stop_azan_sound()
        if snooze_callback:
            snooze_callback()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_snooze)  # Treat closing as a snooze

    main_label = ctk.CTkLabel(popup, text=f"It's time for {prayer_name} prayer!", font=ctk.CTkFont(size=18))
    main_label.pack(pady=20, padx=20)

    button_frame = ctk.CTkFrame(popup, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="x")

    offered_button = ctk.CTkButton(button_frame, text="Offered", command=on_offered, height=40)
    offered_button.pack(side="left", expand=True, padx=(0, 5))

    snooze_button = ctk.CTkButton(button_frame, text="Not Yet (Snooze)", command=on_snooze, height=40)
    snooze_button.pack(side="right", expand=True, padx=(5, 0))

    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width / 2) - (popup.winfo_width() / 2)
    y = (screen_height / 2) - (popup.winfo_height() / 2)
    popup.geometry(f"+{int(x)}+{int(y)}")

    popup.focus_force()