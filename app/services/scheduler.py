import threading
import time
from datetime import datetime, timedelta
from utils import load_prayer_times, log_user_action, logging
from config import DEFAULT_SNOOZE_MINUTES, SCHEDULER_CHECK_INTERVAL_SECONDS


class ReminderScheduler(threading.Thread):
    """Thread-based scheduler for managing prayer time reminders and snoozes."""

    def __init__(self, notification_queue):
        """
        Initialize the scheduler thread.

        Args:
            notification_queue: Queue for sending notifications to the GUI thread
        """
        super().__init__(daemon=True)
        self.notification_queue = notification_queue
        self._stop_event = threading.Event()  # Thread control flag

        # Reminder tracking
        self.reminders_today = {}  # Active prayer times for today
        self.snoozed_reminders = {}  # Currently snoozed prayers
        self.last_checked_date = None  # Date of last prayer time refresh

        self.reload_times()  # Load initial prayer times

    def reload_times(self):
        """Refresh prayer times for the current day."""
        all_times = load_prayer_times()
        self.reminders_today = {name: time_str
                                for name, time_str in all_times.items()
                                if time_str}
        self.last_checked_date = datetime.now().date()
        logging.info(f"Scheduler reloaded times for {self.last_checked_date}: {self.reminders_today}")

    def run(self):
        """Main scheduler loop running in background thread."""
        logging.info("Reminder scheduler thread started.")

        while not self._stop_event.is_set():
            now = datetime.now()

            # SECTION 1: DAILY RESET CHECK
            if now.date() > self.last_checked_date:
                logging.info("Midnight passed. Resetting reminders for new day.")
                self.reload_times()

            current_time_str = now.strftime('%H:%M')

            # SECTION 2: CHECK REGULAR PRAYER TIMES
            for prayer_name, time_str in list(self.reminders_today.items()):
                if time_str == current_time_str:
                    self._trigger_notification(prayer_name)
                    del self.reminders_today[prayer_name]  # Prevent re-trigger

            # SECTION 3: CHECK SNOOZED REMINDERS
            for prayer_name, snooze_until_dt in list(self.snoozed_reminders.items()):
                if now >= snooze_until_dt:
                    self._trigger_notification(prayer_name)
                    del self.snoozed_reminders[prayer_name]

            time.sleep(SCHEDULER_CHECK_INTERVAL_SECONDS)

        logging.info("Scheduler thread has stopped.")

    def _trigger_notification(self, prayer_name):
        """Internal method to handle notification triggering."""
        logging.info(f"Time for {prayer_name}. Sending notification request.")
        self.notification_queue.put(('show_notification', prayer_name))
        log_user_action("notified", prayer_name)

    def snooze_prayer(self, prayer_name):
        """
        Snooze a prayer reminder for the default duration.

        Args:
            prayer_name: Name of the prayer to snooze
        """
        snooze_time = datetime.now() + timedelta(minutes=DEFAULT_SNOOZE_MINUTES)
        self.snoozed_reminders[prayer_name] = snooze_time
        logging.info(f"{prayer_name} snoozed until {snooze_time.strftime('%H:%M:%S')}")
        log_user_action("snoozed", prayer_name, {"snooze_until": snooze_time.strftime('%H:%M')})
        self.notification_queue.put(('update_status', None))

    def acknowledge_prayer(self, prayer_name):
        """
        Mark a prayer as completed/offered.

        Args:
            prayer_name: Name of the prayer being acknowledged
        """
        logging.info(f"{prayer_name} acknowledged as 'Offered'.")
        log_user_action("offered", prayer_name)
        self.notification_queue.put(('update_status', None))

    def stop(self):
        """Gracefully stop the scheduler thread."""
        self._stop_event.set()

    def get_today_times(self):
        """Get copy of today's prayer times."""
        return self.reminders_today.copy()