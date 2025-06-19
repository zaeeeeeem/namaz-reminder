# main.py
"""
The main entry point for the Namaz Reminder application.

This script initializes all the core components, including the background scheduler,
the system tray icon, and the main graphical user interface (GUI), then starts
the application's main event loop.
"""

import queue
import threading
import sys
from PIL import Image
import pystray

# Import the refactored MainView class and services
from app.views.main_view import MainView
from app.services.scheduler import ReminderScheduler
from app.utils import utils
from app.utils import config

# --- Global instances to be shared across the application ---
# These are populated by the main() function.
app_instance = None
scheduler_instance = None
icon_instance = None


def initialize_scheduler():
    """
    Creates the communication queue and starts the background scheduler thread.

    Returns:
        ReminderScheduler: An initialized and started instance of the scheduler.
    """
    notification_queue = queue.Queue()
    scheduler = ReminderScheduler(notification_queue)
    scheduler.start()
    utils.logging.info("Reminder scheduler service started.")
    return scheduler


def create_tray_icon(on_show_callback, on_quit_callback):
    """
    Creates and runs the system tray icon in a separate thread.

    Args:
        on_show_callback (callable): The function to call when 'Show' is clicked.
        on_quit_callback (callable): The function to call when 'Quit' is clicked.

    Returns:
        pystray.Icon: An initialized and running instance of the tray icon.
    """
    try:
        icon_image = Image.open(config.APP_ICON_PNG)
    except FileNotFoundError:
        utils.logging.error(f"{config.APP_ICON_PNG} not found! Tray icon will be invisible.")
        icon_image = None

    menu = pystray.Menu(
        pystray.MenuItem("Show", on_show_callback, default=True),
        pystray.MenuItem("Quit", on_quit_callback)
    )
    icon = pystray.Icon("NamazReminder", icon_image, "Namaz Reminder", menu)

    threading.Thread(target=icon.run, daemon=True).start()
    utils.logging.info("System tray icon thread started.")
    return icon


def main():
    """
    The primary function that orchestrates the application startup.
    """
    global app_instance, scheduler_instance, icon_instance

    utils.logging.info("Starting Namaz Reminder App...")

    # 1. Start background services
    scheduler_instance = initialize_scheduler()

    # 2. Define the actions for the system tray icon
    def show_window_action(icon, item):
        """A wrapper function to safely call the show window method on the GUI instance."""
        utils.logging.info("'Show' action triggered from system tray.")
        try:
            if app_instance:
                app_instance.schedule_show_window()
            else:
                utils.logging.warning("app_instance is None; cannot show window.")
        except Exception as e:
            utils.logging.error(f"Error in show_window_action: {e}", exc_info=True)

    def quit_app_action(icon, item):
        """A wrapper function to gracefully stop all application threads and exit."""
        utils.logging.info("'Quit' action triggered from system tray.")
        if scheduler_instance:
            scheduler_instance.stop()
        if icon_instance:
            icon_instance.stop()
        if app_instance:
            app_instance.app.quit()  # Stops the tkinter mainloop
        sys.exit(0)

    # 3. Create the system tray icon
    icon_instance = create_tray_icon(show_window_action, quit_app_action)

    # 4. Initialize and run the main GUI. This is a blocking call.
    # The script will pause here until the application is quit.
    app_instance = MainView(scheduler_instance)

    utils.logging.info("Application has been closed.")


if __name__ == "__main__":
    # This ensures the main() function is called only when the script is executed directly
    main()