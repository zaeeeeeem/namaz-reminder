import threading
import time
from datetime import datetime, timedelta
from app.utils.utils import load_prayer_times, log_user_action, logging
from app.utils.config import DEFAULT_SNOOZE_MINUTES, SCHEDULER_CHECK_INTERVAL_SECONDS


class ReminderScheduler(threading.Thread):
    """Thread-based scheduler for managing prayer time reminders and snoozes."""

    def __init__(self, notification_queue):
        """
        Initialize the scheduler thread.

        Args:
            notification_queue: Queue for sending notifications to the GUI thread.
        """
        super().__init__(daemon=True)
        self.notification_queue = notification_queue
        self._stop_event = threading.Event()

        self.reminders_today = {}       # Active prayer times for today
        self.snoozed_reminders = {}     # Currently snoozed prayers
        self.last_checked_date = None   # Date of last prayer time refresh

        self.reload_times()

    def reload_times(self):
        """Refresh and load today's prayer times from storage."""
        all_times = load_prayer_times()
        self.reminders_today = {
            name: time_str
            for name, time_str in all_times.items()
            if time_str
        }
        self.last_checked_date = datetime.now().date()
        logging.info(f"Scheduler reloaded times for {self.last_checked_date}: {self.reminders_today}")

    def run(self):
        """Main background loop for monitoring and triggering reminders."""
        logging.info("Reminder scheduler thread started.")
        while not self._stop_event.is_set():
            now = datetime.now()

            self._check_for_day_change(now)
            self._check_regular_reminders(now)
            self._check_snoozed_reminders(now)

            time.sleep(SCHEDULER_CHECK_INTERVAL_SECONDS)

        logging.info("Scheduler thread has stopped.")

    def _check_for_day_change(self, now):
        """Reset reminders if the day has changed."""
        if now.date() > self.last_checked_date:
            logging.info("Midnight passed. Resetting reminders for new day.")
            self.reload_times()

    def _check_regular_reminders(self, now):
        """Check if it's time to trigger regular prayer reminders."""
        current_time_str = now.strftime('%H:%M')
        for prayer_name, time_str in list(self.reminders_today.items()):
            if time_str == current_time_str:
                self._trigger_notification(prayer_name)
                del self.reminders_today[prayer_name]

    def _check_snoozed_reminders(self, now):
        """Check if any snoozed prayer reminders should be triggered."""
        for prayer_name, snooze_until in list(self.snoozed_reminders.items()):
            if now >= snooze_until:
                self._trigger_notification(prayer_name)
                del self.snoozed_reminders[prayer_name]

    def _trigger_notification(self, prayer_name):
        """Send a prayer notification event to the UI."""
        logging.info(f"Time for {prayer_name}. Sending notification request.")
        self.notification_queue.put(('show_notification', prayer_name))
        log_user_action("notified", prayer_name)

    def snooze_prayer(self, prayer_name):
        """
        Snooze a prayer reminder for a default duration.

        Args:
            prayer_name: Name of the prayer to snooze.
        """
        snooze_time = datetime.now() + timedelta(minutes=DEFAULT_SNOOZE_MINUTES)
        self.snoozed_reminders[prayer_name] = snooze_time
        logging.info(f"{prayer_name} snoozed until {snooze_time.strftime('%H:%M:%S')}")
        log_user_action("snoozed", prayer_name, {"snooze_until": snooze_time.strftime('%H:%M')})
        self.notification_queue.put(('update_status', None))

    def acknowledge_prayer(self, prayer_name):
        """
        Acknowledge that a prayer has been offered.

        Args:
            prayer_name: Name of the prayer being acknowledged.
        """
        logging.info(f"{prayer_name} acknowledged as 'Offered'.")
        log_user_action("offered", prayer_name)
        self.notification_queue.put(('update_status', None))

    def stop(self):
        """Gracefully stop the scheduler thread."""
        self._stop_event.set()

    def get_today_times(self):
        """Return a copy of today's prayer times."""
        return self.reminders_today.copy()
