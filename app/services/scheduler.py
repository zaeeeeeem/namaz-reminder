# app/services/scheduler.py

"""
This module contains the ReminderScheduler class, which runs in a separate
thread to monitor prayer times and manage notifications without blocking the UI.
"""

import threading
import time
from datetime import datetime, timedelta

# Import the refactored utility and configuration modules
from app.utils import utils
from app.utils import config

class ReminderScheduler(threading.Thread):
    """
    A thread-based scheduler for managing prayer time reminders and snoozes.
    """

    def __init__(self, notification_queue):
        """
        Initializes the scheduler thread.

        Args:
            notification_queue (queue.Queue): A thread-safe queue for sending
                                              notification events to the GUI thread.
        """
        super().__init__(daemon=True)
        self.notification_queue = notification_queue
        self._stop_event = threading.Event()

        self.reminders_today = {}       # Dict of active prayer times for the current day
        self.snoozed_reminders = {}     # Dict of prayers currently in a snoozed state
        self.last_checked_date = None   # The date of the last prayer time refresh

        self.reload_times()

    def reload_times(self):
        """
        Refreshes prayer times from the user's file and resets the daily schedule.
        """
        all_times = utils.load_prayer_times()
        self.reminders_today = {
            name: time_str for name, time_str in all_times.items() if time_str
        }
        self.last_checked_date = datetime.now().date()
        utils.logging.info(f"Scheduler reloaded times for {self.last_checked_date}: {self.reminders_today}")

    def run(self):
        """
        The main background loop that continuously monitors for prayer times.
        This method is executed when the thread starts.
        """
        utils.logging.info("Reminder scheduler thread started.")
        while not self._stop_event.is_set():
            now = datetime.now()

            self._check_for_day_change(now)
            self._check_regular_reminders(now)
            self._check_snoozed_reminders(now)

            time.sleep(config.SCHEDULER_CHECK_INTERVAL_SECONDS)

        utils.logging.info("Scheduler thread has stopped.")

    def _check_for_day_change(self, now):
        """
        Checks if the calendar day has changed since the last check and reloads times if so.

        Args:
            now (datetime): The current datetime.
        """
        if now.date() > self.last_checked_date:
            utils.logging.info("Midnight passed. Resetting reminders for new day.")
            self.reload_times()

    def _check_regular_reminders(self, now):
        """
        Iterates through today's prayer times and triggers a notification if the time matches.

        Args:
            now (datetime): The current datetime.
        """
        current_time_str = now.strftime('%H:%M')
        # Iterate over a copy of the items to allow for safe deletion
        for prayer_name, time_str in list(self.reminders_today.items()):
            if time_str == current_time_str:
                self._trigger_notification(prayer_name)
                # Remove the prayer from the list to prevent multiple notifications
                del self.reminders_today[prayer_name]

    def _check_snoozed_reminders(self, now):
        """
        Checks if any snoozed reminders have expired and re-triggers them.

        Args:
            now (datetime): The current datetime.
        """
        # Iterate over a copy of the items to allow for safe deletion
        for prayer_name, snooze_until_dt in list(self.snoozed_reminders.items()):
            if now >= snooze_until_dt:
                self._trigger_notification(prayer_name)
                del self.snoozed_reminders[prayer_name]

    def _trigger_notification(self, prayer_name):
        """
        Places a notification request into the queue for the GUI to process.

        Args:
            prayer_name (str): The name of the prayer to notify about.
        """
        utils.logging.info(f"Time for {prayer_name}. Sending notification request.")
        self.notification_queue.put(('show_notification', prayer_name))
        utils.log_user_action("notified", prayer_name)

    def snooze_prayer(self, prayer_name):
        """
        Snoozes a given prayer for the default duration defined in config.

        Args:
            prayer_name (str): The name of the prayer to snooze.
        """
        snooze_until = datetime.now() + timedelta(minutes=config.DEFAULT_SNOOZE_MINUTES)
        self.snoozed_reminders[prayer_name] = snooze_until
        utils.logging.info(f"{prayer_name} snoozed until {snooze_until.strftime('%H:%M:%S')}")
        utils.log_user_action("snoozed", prayer_name, {"snooze_until": snooze_until.strftime('%H:%M')})

    def acknowledge_prayer(self, prayer_name):
        """
        Logs that a prayer has been marked as 'Offered' by the user.

        Args:
            prayer_name (str): The name of the acknowledged prayer.
        """
        utils.logging.info(f"{prayer_name} acknowledged as 'Offered'.")
        utils.log_user_action("offered", prayer_name)

    def stop(self):
        """
        Signals the scheduler thread to stop its execution loop gracefully.
        """
        self._stop_event.set()

    def get_today_times(self):
        """
        Provides a safe copy of the prayer times scheduled for today.

        Returns:
            dict: A copy of the reminders_today dictionary.
        """
        return self.reminders_today.copy()