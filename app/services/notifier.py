# app/services/notifier.py

"""
This module handles all user-facing notifications, including the
display of the prayer time popup and the playback of the Azan sound.
"""

import customtkinter as ctk
import pygame
import threading
import os

from app.utils import config
from app.utils import utils


# --- Sound Management Functions ---

def play_azan_sound():
    """
    Initializes pygame mixer and plays the Azan sound in a background thread.
    This function handles errors gracefully if the sound file is missing or corrupt.
    """
    if not os.path.exists(config.AZAN_SOUND_FILE):
        utils.logging.warning(f"Audio file not found at: {config.AZAN_SOUND_FILE}")
        return

    try:
        # Initialize the mixer if it's not already
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(config.AZAN_SOUND_FILE)
        pygame.mixer.music.play()
        utils.logging.info("Azan sound started playing.")
    except Exception as e:
        utils.logging.error(f"Failed to play Azan sound: {e}")


def stop_azan_sound():
    """
    Stops any currently playing sound via the pygame mixer.
    """
    try:
        # Check if the mixer is initialized and if music is playing
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            utils.logging.info("Azan sound stopped.")
    except Exception as e:
        utils.logging.error(f"Failed to stop Azan sound: {e}")


# --- Notification Popup Window ---

def show_notification_popup(prayer_name, offered_callback, snooze_callback):
    """
    The main function to create and display a popup notification for a specific prayer.

    Args:
        prayer_name (str): The name of the prayer (e.g., 'Fajr', 'Isha').
        offered_callback (callable): The function to call when 'Offered' is clicked.
        snooze_callback (callable): The function to call when 'Snooze' is clicked or the window is closed.
    """
    # Start the Azan sound in a separate thread to not block the UI
    threading.Thread(target=play_azan_sound, daemon=True).start()

    # Create the top-level window for the popup
    popup = ctk.CTkToplevel()
    popup.title(f"{prayer_name} Reminder")
    popup.geometry("350x180")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)  # Keep the popup on top of all other windows

    # --- Event Handlers ---
    # These functions are defined here to have access to the popup and callback variables.
    def on_offered():
        """Handles the 'Offered' button click event."""
        stop_azan_sound()
        if offered_callback:
            offered_callback()
        popup.destroy()

    def on_snooze():
        """Handles the 'Snooze' button click and the window close event."""
        stop_azan_sound()
        if snooze_callback:
            snooze_callback()
        popup.destroy()

    # Assign the handler to the window's close ('X') button
    popup.protocol("WM_DELETE_WINDOW", on_snooze)

    # --- UI Construction ---
    _create_popup_widgets(popup, prayer_name, on_offered, on_snooze)
    _center_popup_window(popup)
    popup.focus_force()  # Grab the user's attention


def _create_popup_widgets(parent, prayer_name, offered_command, snooze_command):
    """
    Creates and packs all the widgets (labels, buttons) inside the popup window.

    Args:
        parent (ctk.CTkToplevel): The popup window to place widgets in.
        prayer_name (str): The name of the prayer to display.
        offered_command (callable): The command for the 'Offered' button.
        snooze_command (callable): The command for the 'Snooze' button.
    """
    main_label = ctk.CTkLabel(parent, text=f"It's time for {prayer_name} prayer!", font=ctk.CTkFont(size=18))
    main_label.pack(pady=20, padx=20)

    button_frame = ctk.CTkFrame(parent, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="x")

    offered_button = ctk.CTkButton(button_frame, text="Offered", command=offered_command, height=40)
    offered_button.pack(side="left", expand=True, padx=(0, 5))

    snooze_button = ctk.CTkButton(button_frame, text="Not Yet (Snooze)", command=snooze_command, height=40)
    snooze_button.pack(side="right", expand=True, padx=(5, 0))


def _center_popup_window(popup):
    """
    Calculates the correct coordinates to center the popup on the screen.

    Args:
        popup (ctk.CTkToplevel): The window to be centered.
    """
    # Ensure window size is calculated before positioning
    popup.update_idletasks()

    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()

    popup_width = popup.winfo_width()
    popup_height = popup.winfo_height()

    x = (screen_width / 2) - (popup_width / 2)
    y = (screen_height / 2) - (popup_height / 2)

    popup.geometry(f"+{int(x)}+{int(y)}")