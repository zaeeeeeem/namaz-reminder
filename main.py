# main.py

import queue
from gui import NamazReminderApp
from scheduler import ReminderScheduler
from utils import logging


def main():
    """
    The main entry point of the Namaz Reminder application.
    Initializes the scheduler, the GUI, and connects them.
    """
    logging.info("Starting Namaz Reminder App...")

    # 1. Create the communication bridge (a thread-safe queue)
    # This allows the background scheduler to safely send messages to the GUI.
    notification_queue = queue.Queue()

    # 2. Initialize and start the background scheduler thread
    scheduler = ReminderScheduler(notification_queue)
    scheduler.start()

    # 3. Initialize the GUI
    # We pass the scheduler instance to the GUI so it can call methods like reload_times().
    # The GUI's __init__ method will create the window and start the main loop.
    NamazReminderApp(scheduler)

    # 4. This code runs only after the GUI window is closed
    # Stop the scheduler thread gracefully to ensure a clean exit.
    scheduler.stop()
    logging.info("Application has been closed.")


# This standard Python block ensures the main() function is called only when
# you run this file directly.
if __name__ == "__main__":
    main()