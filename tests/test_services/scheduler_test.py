import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.services.scheduler import ReminderScheduler


class TestReminderScheduler(unittest.TestCase):

    def setUp(self):
        self.mock_queue = MagicMock()
        self.scheduler = ReminderScheduler(self.mock_queue)

    @patch("app.services.scheduler.utils.load_prayer_times")
    def test_reload_times_loads_correct_data(self, mock_load_prayer_times):
        mock_load_prayer_times.return_value = {
            "Fajr": "04:30",
            "Dhuhr": "",
            "Asr": "15:15"
        }
        self.scheduler.reload_times()
        self.assertEqual(self.scheduler.reminders_today, {
            "Fajr": "04:30",
            "Asr": "15:15"
        })

    @patch("app.services.scheduler.utils.logging.info")
    def test_acknowledge_prayer_logs_action(self, mock_logging_info):
        self.scheduler.acknowledge_prayer("Asr")
        mock_logging_info.assert_any_call("Asr acknowledged as 'Offered'.")

    @patch("app.services.scheduler.utils.logging.info")
    @patch("app.services.scheduler.utils.log_user_action")
    def test_trigger_notification_puts_item_in_queue(self, mock_log_user_action, mock_logging_info):
        self.scheduler._trigger_notification("Maghrib")
        self.mock_queue.put.assert_called_once_with(('show_notification', 'Maghrib'))
        mock_log_user_action.assert_called_once_with("notified", "Maghrib")

    def test_get_today_times_returns_copy(self):
        self.scheduler.reminders_today = {"Fajr": "05:00"}
        result = self.scheduler.get_today_times()
        self.assertEqual(result, {"Fajr": "05:00"})
        self.assertIsNot(result, self.scheduler.reminders_today)

    @patch("app.services.scheduler.utils.logging.info")
    @patch("app.services.scheduler.utils.log_user_action")
    def test_snooze_prayer_adds_correct_time(self, mock_log_user_action, mock_logging_info):
        from app.utils import config  # dynamic import to get default snooze minutes

        fixed_now = datetime(2025, 6, 20, 2, 0)

        with patch("app.services.scheduler.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            self.scheduler.snooze_prayer("Fajr")

            self.assertIn("Fajr", self.scheduler.snoozed_reminders)
            snoozed_until = self.scheduler.snoozed_reminders["Fajr"]
            expected = fixed_now + timedelta(minutes=config.DEFAULT_SNOOZE_MINUTES)

            delta_seconds = abs((snoozed_until - expected).total_seconds())
            self.assertLessEqual(delta_seconds, 1, f"Expected ~{expected}, got {snoozed_until}")

    @patch("app.services.scheduler.utils.load_prayer_times")
    @patch("app.services.scheduler.utils.logging.info")
    def test_check_for_day_change_reload(self, mock_logging_info, mock_load_times):
        # simulate today's date and next day
        self.scheduler.last_checked_date = datetime(2025, 6, 19).date()
        mock_load_times.return_value = {"Fajr": "04:00"}

        self.scheduler._check_for_day_change(datetime(2025, 6, 20, 0, 0))
        self.assertEqual(self.scheduler.last_checked_date, datetime(2025, 6, 20).date())


if __name__ == "__main__":
    unittest.main()
