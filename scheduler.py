# scheduler.py

import threading
import time
from datetime import datetime, timedelta

from utils import load_prayer_times, log_user_action, logging
from config import DEFAULT_SNOOZE_MINUTES, SCHEDULER_CHECK_INTERVAL_SECONDS


class ReminderScheduler(threading.Thread):
    def __init__(self, notification_queue):
        super().__init__(daemon=True)
        self.notification_queue = notification_queue
        self._stop_event = threading.Event()
        self.reminders_today = {}
        self.snoozed_reminders = {}
        self.last_checked_date = None
        self.reload_times()

    def reload_times(self):
        all_times = load_prayer_times()
        self.reminders_today = {name: time_str for name, time_str in all_times.items() if time_str}
        self.last_checked_date = datetime.now().date()
        logging.info(f"Scheduler reloaded times for {self.last_checked_date}: {self.reminders_today}")

    def run(self):
        logging.info("Reminder scheduler thread started.")
        while not self._stop_event.is_set():
            now = datetime.now()

            if now.date() > self.last_checked_date:
                logging.info("Midnight passed. Resetting reminders for the new day.")
                self.reload_times()

            current_time_str = now.strftime('%H:%M')

            for prayer_name, time_str in list(self.reminders_today.items()):
                if time_str == current_time_str:
                    logging.info(f"Time for {prayer_name}. Sending notification request.")
                    self.notification_queue.put(('show_notification', prayer_name))
                    log_user_action("notified", prayer_name)
                    del self.reminders_today[prayer_name]

            for prayer_name, snooze_until_dt in list(self.snoozed_reminders.items()):
                if now >= snooze_until_dt:
                    logging.info(f"Snooze time for {prayer_name} is over. Sending notification.")
                    self.notification_queue.put(('show_notification', prayer_name))
                    log_user_action("snooze_fired", prayer_name)
                    del self.snoozed_reminders[prayer_name]

            time.sleep(SCHEDULER_CHECK_INTERVAL_SECONDS)

        logging.info("Scheduler thread has stopped.")

    def snooze_prayer(self, prayer_name):
        """Sets a prayer to be snoozed. Called from the main thread via the App."""
        snooze_time = datetime.now() + timedelta(minutes=DEFAULT_SNOOZE_MINUTES)
        self.snoozed_reminders[prayer_name] = snooze_time
        logging.info(f"{prayer_name} has been snoozed until {snooze_time.strftime('%H:%M:%S')}")
        log_user_action("snoozed", prayer_name, {"snooze_until": snooze_time.strftime('%H:%M')})
        self.notification_queue.put(('update_status', None))

    def acknowledge_prayer(self, prayer_name):
        logging.info(f"{prayer_name} was acknowledged as 'Offered'.")
        log_user_action("offered", prayer_name)
        self.notification_queue.put(('update_status', None))

    def stop(self):
        self._stop_event.set()

    def get_today_times(self):
        return self.reminders_today.copy()
