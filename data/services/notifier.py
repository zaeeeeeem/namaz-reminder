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
    Plays the Azan sound in a background thread.
    Handles file existence check and playback errors.
    """
    # Check if sound file exists
    if not os.path.exists(AZAN_SOUND_FILE):
        logging.warning(f"Audio file not found at: {AZAN_SOUND_FILE}")
        return

    try:
        # Initialize and play sound
        pygame.mixer.init()
        pygame.mixer.music.load(AZAN_SOUND_FILE)
        pygame.mixer.music.play()
        logging.info("Azan sound started playing.")
    except Exception as e:
        logging.error(f"Failed to play sound: {e}")


def stop_azan_sound():
    """
    Stops the currently playing Azan sound.
    Safely handles cases where mixer isn't initialized.
    """
    try:
        # Only stop if actually playing
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            logging.info("Azan sound stopped.")
    except Exception as e:
        logging.error(f"Failed to stop sound: {e}")


# --------------------------
# Notification Popup Window
# --------------------------

def show_notification_popup(prayer_name, offered_callback, snooze_callback):
    """
    Shows a prayer reminder popup with two action buttons.

    Args:
        prayer_name: Name of the prayer (Fajr, Dhuhr, etc.)
        offered_callback: Function to call when 'Offered' is clicked
        snooze_callback: Function to call when 'Snooze' is clicked
    """

    # Start playing sound in background
    threading.Thread(target=play_azan_sound, daemon=True).start()

    # Create popup window
    popup = ctk.CTkToplevel()
    popup.title(f"{prayer_name} Reminder")
    popup.geometry("350x180")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)  # Keep on top of other windows

    # ----------------------
    # Button Action Handlers
    # ----------------------
    def on_offered():
        """Handler for Offered button click"""
        stop_azan_sound()
        if offered_callback:
            offered_callback()
        popup.destroy()

    def on_snooze():
        """Handler for Snooze button click"""
        stop_azan_sound()
        if snooze_callback:
            snooze_callback()
        popup.destroy()

    # Treat window close as snooze
    popup.protocol("WM_DELETE_WINDOW", on_snooze)

    # ------------------
    # UI Elements
    # ------------------

    # Main reminder text
    main_label = ctk.CTkLabel(
        popup,
        text=f"It's time for {prayer_name} prayer!",
        font=ctk.CTkFont(size=18)
    )
    main_label.pack(pady=20, padx=20)

    # Button container
    button_frame = ctk.CTkFrame(popup, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="x")

    # Offered button
    offered_button = ctk.CTkButton(
        button_frame,
        text="Offered",
        command=on_offered,
        height=40
    )
    offered_button.pack(side="left", expand=True, padx=(0, 5))

    # Snooze button
    snooze_button = ctk.CTkButton(
        button_frame,
        text="Not Yet (Snooze)",
        command=on_snooze,
        height=40
    )
    snooze_button.pack(side="right", expand=True, padx=(5, 0))

    # Center the window on screen
    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width / 2) - (popup.winfo_width() / 2)
    y = (screen_height / 2) - (popup.winfo_height() / 2)
    popup.geometry(f"+{int(x)}+{int(y)}")

    # Force focus to the popup
    popup.focus_force()