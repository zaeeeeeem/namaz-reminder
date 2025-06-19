import queue
import threading
from PIL import Image
import pystray
import sys

from gui import NamazReminderApp
from scheduler import ReminderScheduler
from utils import logging
from config import ASSETS_DIR

# --- Global variables that MUST be updated by main() ---
app_instance = None
scheduler_instance = None
icon_instance = None

def main():
    global app_instance, scheduler_instance, icon_instance

    logging.info("Starting Namaz Reminder App...")

    # 1. Initialize background services
    notification_queue = queue.Queue()
    scheduler_instance = ReminderScheduler(notification_queue)
    scheduler_instance.start()

    # 2. Define the actions for the tray icon
    def show_window_action(icon, item):
        logging.info("show_window_action called.")
        # This function will now find the correct global app_instance
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

    try:
        icon_image = Image.open(f"{ASSETS_DIR}/icon.png")
    except FileNotFoundError:
        logging.error("icon.png not found in assets folder!")
        icon_image = None

    menu = pystray.Menu(
        pystray.MenuItem("Show", show_window_action, default=True),
        pystray.MenuItem("Quit", quit_app_action)
    )
    icon_instance = pystray.Icon("NamazReminder", icon_image, "Namaz Reminder", menu)
    threading.Thread(target=icon_instance.run, daemon=True).start()
    logging.info("System tray icon thread started.")

    app_instance = NamazReminderApp(scheduler_instance)

    logging.info("Application has been closed.")


if __name__ == "__main__":
    main()