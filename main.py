import queue
import threading
from PIL import Image
import pystray
import sys

from gui import NamazReminderApp
from scheduler import ReminderScheduler
from utils import logging
from config import ASSETS_DIR

# --- Global instances updated by main() ---
app_instance = None
scheduler_instance = None
icon_instance = None

def initialize_scheduler():
    """Initialize and start the background reminder scheduler."""
    notification_queue = queue.Queue()
    scheduler = ReminderScheduler(notification_queue)
    scheduler.start()
    return scheduler

def create_tray_icon(on_show, on_quit):
    """Create and run the system tray icon with menu actions."""
    try:
        icon_image = Image.open(f"{ASSETS_DIR}/icon.png")
    except FileNotFoundError:
        logging.error("icon.png not found in assets folder!")
        icon_image = None

    menu = pystray.Menu(
        pystray.MenuItem("Show", on_show, default=True),
        pystray.MenuItem("Quit", on_quit)
    )
    icon = pystray.Icon("NamazReminder", icon_image, "Namaz Reminder", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    logging.info("System tray icon thread started.")
    return icon

def main():
    """Main entry point for the Namaz Reminder application."""
    global app_instance, scheduler_instance, icon_instance

    logging.info("Starting Namaz Reminder App...")

    # Initialize the reminder scheduler
    scheduler_instance = initialize_scheduler()

    # Define system tray menu actions
    def show_window_action(icon, item):
        logging.info("show_window_action called.")
        try:
            if app_instance:
                app_instance.schedule_show_window()
            else:
                logging.warning("app_instance is still None. Cannot show window.")
        except Exception as e:
            logging.error(f"Error in show_window_action: {e}", exc_info=True)

    def quit_app_action(icon, item):
        logging.info("Quit action triggered from system tray.")
        if scheduler_instance:
            scheduler_instance.stop()
        if icon_instance:
            icon_instance.stop()
        if app_instance:
            app_instance.app.quit()
        sys.exit(0)

    # Initialize system tray icon
    icon_instance = create_tray_icon(show_window_action, quit_app_action)

    # Start the main app GUI
    app_instance = NamazReminderApp(scheduler_instance)

    logging.info("Application has been closed.")

if __name__ == "__main__":
    main()
