import unittest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import customtkinter as ctk

from app.services import prayer_calendar
from app.utils import config


class TestPrayerCalendarService(unittest.TestCase):

    def setUp(self):
        # Setup a test data file path
        self.test_file = "test_prayer_status.json"
        config.PRAYER_STATUS_FILE = self.test_file

    def tearDown(self):
        # Clean up the test file if it was created
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_status_data_returns_dict(self):
        with open(self.test_file, "w") as f:
            json.dump({"2025-06-20-Fajr": "Completed"}, f)

        result = prayer_calendar._load_status_data()
        self.assertIsInstance(result, dict)
        self.assertIn("2025-06-20-Fajr", result)

    def test_load_status_data_returns_empty_on_missing_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        result = prayer_calendar._load_status_data()
        self.assertEqual(result, {})

    def test_save_status_data_creates_file(self):
        data = {"2025-06-20-Fajr": "Completed"}
        prayer_calendar._save_status_data(data)

        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file) as f:
            saved = json.load(f)
        self.assertEqual(saved, data)

    def test_should_disable_button_logic(self):
        today = datetime.now().date()
        future_date = today + timedelta(days=1)
        past_date = today - timedelta(days=1)
        now_time_str = datetime.now().strftime("%H:%M")
        early_time_str = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")

        # Future date = disabled
        self.assertTrue(prayer_calendar._should_disable_button(future_date, today, now_time_str))
        # Past date = not disabled
        self.assertFalse(prayer_calendar._should_disable_button(past_date, today, now_time_str))
        # Today, time not reached = disabled
        self.assertTrue(prayer_calendar._should_disable_button(today, today, early_time_str))
        # Today, empty time = disabled
        self.assertTrue(prayer_calendar._should_disable_button(today, today, ""))
        # Today, time already passed = not disabled
        self.assertFalse(prayer_calendar._should_disable_button(today, today, now_time_str))

    @patch("app.services.prayer_calendar._load_status_data", return_value={})
    @patch("app.services.prayer_calendar.calendar_view.build_calendar_frame")
    def test_open_calendar_view_structure(self, mock_build_calendar, mock_load):
        # Use real CTk root to avoid frame creation errors
        root = ctk.CTk()
        root.withdraw()

        def fake_get_times():
            return {name: "05:00" for name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]}

        switch_mock = MagicMock()

        frame = prayer_calendar.open_calendar_view(root, fake_get_times, switch_mock)

        self.assertIsInstance(frame, ctk.CTkFrame)
        mock_build_calendar.assert_called_once()

        root.destroy()


if __name__ == '__main__':
    unittest.main()
