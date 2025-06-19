import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from app.views import settings_view


class TestSettingsView(unittest.TestCase):
    def setUp(self):
        self.root = ctk.CTk()
        self.app_controller = MagicMock()
        self.app_controller.prayer_entries = {}

    def test_create_settings_view_structure(self):
        """
        Verifies the settings view is created with prayer entry fields and buttons.
        """
        with patch("app.views.settings_view.PRAYER_NAMES", ["Fajr", "Dhuhr"]), \
             patch("app.views.settings_view._add_icon_image"):
            frame = settings_view.create_settings_view(self.root, self.app_controller)

        self.assertIsInstance(frame, ctk.CTkFrame)
        self.assertIn("Fajr", self.app_controller.prayer_entries)
        self.assertIn("Dhuhr", self.app_controller.prayer_entries)

    @patch("app.views.settings_view.Image.open")
    @patch("app.views.settings_view.ctk.CTkImage")
    @patch("app.views.settings_view.ctk.CTkLabel")
    def test_icon_image_load_success(self, mock_label, mock_ctk_image, mock_pil_open):
        parent = ctk.CTkFrame(self.root)
        settings_view._add_icon_image(parent)
        mock_pil_open.assert_called_once()
        mock_ctk_image.assert_called_once()
        mock_label.assert_called_once()

    @patch("app.views.settings_view.Image.open", side_effect=FileNotFoundError)
    @patch("app.views.settings_view.logging")
    def test_icon_image_file_not_found(self, mock_logger, _):
        parent = ctk.CTkFrame(self.root)
        settings_view._add_icon_image(parent)
        mock_logger.warning.assert_called_with("icon.png not found in assets. Skipping image on settings page.")

    def test_create_prayer_time_entries(self):
        """
        Checks if a CTkEntry is created for each prayer and added to the controller.
        """
        with patch("app.views.settings_view.PRAYER_NAMES", ["Fajr"]):
            parent = ctk.CTkFrame(self.root)
            settings_view._create_prayer_time_entries(parent, self.app_controller)

        self.assertIn("Fajr", self.app_controller.prayer_entries)
        self.assertIsInstance(self.app_controller.prayer_entries["Fajr"], ctk.CTkEntry)

    def test_create_action_buttons_attaches_callbacks(self):
        parent = ctk.CTkFrame(self.root)
        self.app_controller.save_new_times = MagicMock()
        self.app_controller.show_frame = MagicMock()

        settings_view._create_action_buttons(parent, self.app_controller)

        button_frame = parent.winfo_children()[0]
        buttons = button_frame.winfo_children()

        buttons[0].invoke()  # Save
        buttons[1].invoke()  # Back

        self.app_controller.save_new_times.assert_called_once()
        self.app_controller.show_frame.assert_called_once_with("dashboard")


if __name__ == '__main__':
    unittest.main()
