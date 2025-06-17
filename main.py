# main.py

import queue
from gui import NamazReminderApp
from scheduler import ReminderScheduler
from utils import logging


def main():
    logging.info("Starting Namaz Reminder App...")

    notification_queue = queue.Queue()

    scheduler = ReminderScheduler(notification_queue)
    scheduler.start()

    NamazReminderApp(scheduler)

    scheduler.stop()
    logging.info("Application has been closed.")


if __name__ == "__main__":
    main()