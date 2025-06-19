# app/views/settings_view.py

import customtkinter as ctk
from PIL import Image

# Note: These imports will be relative to the new app structure
from app.utils.config import PRAYER_NAMES, ASSETS_DIR
from app.utils.utils import logging # Assuming logging is configured in the new utils.py

def create_settings_view(parent, app_controller):
    """
    Creates and returns the settings frame for inputting prayer times.

    Args:
        parent (ctk.CTk): The parent widget (the main app window).
        app_controller (MainView): The instance of the main application view to access its methods and attributes.
    """
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # --- Display Icon ---
    _add_icon_image(frame)

    # --- Title ---
    title = ctk.CTkLabel(frame, text="Set Times", font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=10)

    # --- Time Entry Fields ---
    # The dictionary of entry widgets is stored on the app_controller so it can be accessed
    # by the load_times_into_settings_entries() method.
    app_controller.prayer_entries = {}
    _create_prayer_time_entries(frame, app_controller)

    # --- Action Buttons ---
    _create_action_buttons(frame, app_controller)

    return frame


def _add_icon_image(parent):
    """
    Loads and displays the application icon at the top of the frame.

    Args:
        parent (ctk.CTkFrame): The frame to display the icon in.
    """
    try:
        pil_image = Image.open(f"{ASSETS_DIR}/icon.png")
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))
        image_label = ctk.CTkLabel(parent, image=ctk_image, text="")
        image_label.pack(pady=(10, 0))
    except FileNotFoundError:
        logging.warning("icon.png not found in assets. Skipping image on settings page.")
    except Exception as e:
        logging.error(f"Error loading image on settings page: {e}")


def _create_prayer_time_entries(parent, app_controller):
    """
    Creates and lays out the labeled entry widgets for each prayer time.

    Args:
        parent (ctk.CTkFrame): The parent frame for the entry widgets.
        app_controller (MainView): The main application controller to store the entry widgets.
    """
    for name in PRAYER_NAMES:
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(pady=8, padx=40, fill="x")

        name_label = ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=16), width=80, anchor="w")
        name_label.pack(side="left")

        entry = ctk.CTkEntry(row_frame, font=ctk.CTkFont(size=14), justify="center", width=100)
        entry.pack(side="right")
        app_controller.prayer_entries[name] = entry


def _create_action_buttons(parent, app_controller):
    """
    Creates the 'Save' and 'Back' buttons for the settings view.

    Args:
        parent (ctk.CTkFrame): The parent frame for the buttons.
        app_controller (MainView): The main application controller to link commands.
    """
    button_frame = ctk.CTkFrame(parent, fg_color="transparent")
    button_frame.pack(pady=20, padx=40, fill="x")

    # The save command is a method on the main app_controller
    save_button = ctk.CTkButton(button_frame, text="Save", command=app_controller.save_new_times)
    save_button.pack(side="left", expand=True, padx=(0, 5))

    # The back command uses the app_controller's frame switching method
    back_button = ctk.CTkButton(button_frame, text="Back", fg_color="#555", hover_color="#444",
                                command=lambda: app_controller.show_frame("dashboard"))
    back_button.pack(side="right", expand=True, padx=(5, 0))