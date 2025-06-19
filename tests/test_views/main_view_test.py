import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import queue

# Mocked datetime to control clock
MOCK_TIME = datetime(2025, 6, 19, 12, 0)

with patch("customtkinter.CTk", MagicMock()), \
     patch("customtkinter.CTkFrame", MagicMock()), \
     patch("customtkinter.CTkLabel", MagicMock()), \
     patch("customtkinter.set_appearance_mode"), \
     patch("customtkinter.set_default_color_theme"), \
     patch("customtkinter.CTkFont", MagicMock()):

    from app.views.main_view import MainView


class TestMainView(unittest.TestCase):
    def setUp(self):
        self.scheduler_mock = MagicMock()
        self.scheduler_mock.notification_queue = queue.Queue()

        # Prevent mainloop from blocking tests
        with patch("customtkinter.CTk.mainloop"):
            self.main_view = MainView(self.scheduler_mock)

    @patch("app.views.main_view.create_dashboard_view")
    @patch("app.views.main_view.create_settings_view")
    @patch("app.views.main_view.create_chatbot_view")
    def test_create_all_views(self, mock_chatbot, mock_settings, mock_dashboard):
        mock_dashboard.return_value = MagicMock()
        mock_settings.return_value = MagicMock()
        mock_chatbot.return_value = MagicMock()

        self.main_view._create_all_views()

        self.assertIn("dashboard", self.main_view.frames)
        self.assertIn("settings", self.main_view.frames)
        self.assertIn("chatbot", self.main_view.frames)

    def test_show_frame_switching(self):
        mock_dashboard = MagicMock()
        mock_settings = MagicMock()
        self.main_view.frames = {
            "dashboard": mock_dashboard,
            "settings": mock_settings
        }
        self.main_view.prayer_entries = {
            "Fajr": MagicMock()
        }

        self.main_view.show_frame("settings")
        mock_dashboard.pack_forget.assert_called()
        mock_settings.pack.assert_called()

    def test_save_new_times_valid_input(self):
        entry_mock = MagicMock()
        entry_mock.get.return_value = "12:00"
        self.main_view.prayer_entries = {"Fajr": entry_mock}

        with patch("app.views.main_view.save_prayer_times") as save_mock:
            self.main_view.save_new_times()

            save_mock.assert_called_once_with({"Fajr": "12:00"})
            self.assertEqual(self.main_view.prayer_times["Fajr"], "12:00")

    def test_save_new_times_invalid_input(self):
        entry_mock = MagicMock()
        entry_mock.get.return_value = "invalid"
        self.main_view.prayer_entries = {"Fajr": entry_mock}

        with patch("app.views.main_view.save_prayer_times") as save_mock:
            self.main_view.save_new_times()
            save_mock.assert_not_called()

    def test_load_times_into_settings_entries(self):
        entry_mock = MagicMock()
        self.main_view.prayer_entries = {"Fajr": entry_mock}
        self.main_view.prayer_times = {"Fajr": "05:00"}

        self.main_view.load_times_into_settings_entries()

        entry_mock.delete.assert_called_once_with(0, "end")
        entry_mock.insert.assert_called_once_with(0, "05:00")

    def test_process_scheduler_queue_with_notification(self):
        self.scheduler_mock.notification_queue.put(("show_notification", "Asr"))
        with patch("app.views.main_view.show_notification_popup") as notif_mock:
            self.main_view.process_scheduler_queue()
            notif_mock.assert_called_once()

    def test_hide_window_logs(self):
        with patch.object(self.main_view.app, "withdraw") as mock_withdraw:
            self.main_view.hide_window()
            mock_withdraw.assert_called_once()

    def test_schedule_show_window_executes(self):
        with patch.object(self.main_view.app, "after") as mock_after:
            self.main_view.schedule_show_window()
            mock_after.assert_called()


if __name__ == "__main__":
    unittest.main()
