import customtkinter as ctk
import pygame
import threading
import os
from config import AZAN_SOUND_FILE
from utils import logging


# --------------------------
# Sound Management Functions
# --------------------------

def play_azan_sound():
    """
    Play the Azan sound in a background thread.
    Handles file existence and playback exceptions gracefully.
    """
    if not os.path.exists(AZAN_SOUND_FILE):
        logging.warning(f"Audio file not found at: {AZAN_SOUND_FILE}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(AZAN_SOUND_FILE)
        pygame.mixer.music.play()
        logging.info("Azan sound started playing.")
    except Exception as e:
        logging.error(f"Failed to play Azan sound: {e}")


def stop_azan_sound():
    """
    Stop the currently playing Azan sound if mixer is initialized.
    """
    try:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            logging.info("Azan sound stopped.")
    except Exception as e:
        logging.error(f"Failed to stop Azan sound: {e}")


# --------------------------
# Notification Popup Window
# --------------------------

def show_notification_popup(prayer_name, offered_callback, snooze_callback):
    """
    Show a popup notification for the specified prayer.

    Args:
        prayer_name (str): Name of the prayer (e.g., 'Fajr', 'Isha')
        offered_callback (callable): Called when 'Offered' is clicked
        snooze_callback (callable): Called when 'Snooze' is clicked
    """
    # Start background thread for Azan sound
    threading.Thread(target=play_azan_sound, daemon=True).start()

    # Create a popup window
    popup = ctk.CTkToplevel()
    popup.title(f"{prayer_name} Reminder")
    popup.geometry("350x180")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    # ----------------------
    # Button Handlers
    # ----------------------

    def on_offered():
        """Handler for when 'Offered' is clicked."""
        stop_azan_sound()
        if offered_callback:
            offered_callback()
        popup.destroy()

    def on_snooze():
        """Handler for when 'Snooze' is clicked or window is closed."""
        stop_azan_sound()
        if snooze_callback:
            snooze_callback()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_snooze)

    # ----------------------
    # UI Elements
    # ----------------------

    # Main message
    main_label = ctk.CTkLabel(
        popup,
        text=f"It's time for {prayer_name} prayer!",
        font=ctk.CTkFont(size=18)
    )
    main_label.pack(pady=20, padx=20)

    # Button layout
    button_frame = ctk.CTkFrame(popup, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="x")

    # Offered Button
    offered_button = ctk.CTkButton(
        button_frame,
        text="Offered",
        command=on_offered,
        height=40
    )
    offered_button.pack(side="left", expand=True, padx=(0, 5))

    # Snooze Button
    snooze_button = ctk.CTkButton(
        button_frame,
        text="Not Yet (Snooze)",
        command=on_snooze,
        height=40
    )
    snooze_button.pack(side="right", expand=True, padx=(5, 0))

    # ----------------------
    # Window Positioning
    # ----------------------

    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width / 2) - (popup.winfo_width() / 2)
    y = (screen_height / 2) - (popup.winfo_height() / 2)
    popup.geometry(f"+{int(x)}+{int(y)}")

    popup.focus_force()
