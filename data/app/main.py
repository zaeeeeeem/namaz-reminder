import queue
import threading
import sys
from PIL import Image
import pystray
from gui import NamazReminderApp
from scheduler import ReminderScheduler
from utils import logging
from config import ASSETS_DIR

# --- Global Variables ---
# These are initialized in main() and used throughout the application
app_instance = None  # Holds the main GUI application instance
scheduler_instance = None  # Holds the prayer time scheduler instance
icon_instance = None  # Holds the system tray icon instance


def main():
    """Main entry point for the Namaz Reminder application."""
    global app_instance, scheduler_instance, icon_instance

    # --- Initialization Phase ---
    logging.info("Starting Namaz Reminder App...")

    # 1. SETUP NOTIFICATION SYSTEM
    # Create a queue for communication between scheduler and GUI
    notification_queue = queue.Queue()

    # Initialize and start the prayer time scheduler
    scheduler_instance = ReminderScheduler(notification_queue)
    scheduler_instance.start()
    logging.info("Prayer time scheduler started.")

    # 2. SETUP SYSTEM TRAY ICON
    def setup_tray_icon():
        """Configure and start the system tray icon with its menu."""

        # Define menu actions
        def show_window_action(icon, item):
            """Callback for showing the main application window."""
            logging.info("Show window menu item selected.")
            if app_instance:
                app_instance.schedule_show_window()
            else:
                logging.warning("App instance not available to show window.")

        def quit_app_action(icon, item):
            """Callback for clean application shutdown."""
            logging.info("Initiating application shutdown...")
            # Stop services in proper order
            if scheduler_instance:
                scheduler_instance.stop()
            if icon_instance:
                icon_instance.stop()
            if app_instance:
                app_instance.app.quit()
            sys.exit(0)

        # Load icon image
        try:
            icon_image = Image.open(f"{ASSETS_DIR}/icon.png")
        except FileNotFoundError:
            logging.error("Icon image not found! Using default.")
            icon_image = Image.new('RGB', (64, 64), color='red')  # Fallback

        # Create menu structure
        menu = pystray.Menu(
            pystray.MenuItem("Show", show_window_action, default=True),
            pystray.MenuItem("Quit", quit_app_action)
        )

        # Create and start icon in separate thread
        icon_instance = pystray.Icon(
            "NamazReminder",
            icon_image,
            "Namaz Reminder",
            menu
        )
        threading.Thread(target=icon_instance.run, daemon=True).start()
        logging.info("System tray icon initialized.")

    # 3. START GUI APPLICATION
    setup_tray_icon()
    app_instance = NamazReminderApp(scheduler_instance)
    logging.info("Main application window initialized.")

    # Application will run until closed by user via tray icon
    logging.info("Application running in background...")


if __name__ == "__main__":
    # Entry point when script is run directly
    main()