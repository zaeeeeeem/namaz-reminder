import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from app.views import dashboard_view


class TestDashboardView(unittest.TestCase):
    def setUp(self):
        """
        Runs before every test. Creates a root CTk window and a mock controller with needed attributes.
        """
        self.root = ctk.CTk()
        self.app_controller = MagicMock()
        self.app_controller.prayer_times = {
            "Fajr": "04:30",
            "Dhuhr": "12:15",
            "Asr": "15:45",
            "Maghrib": "19:10",
            "Isha": "20:30"
        }

    @patch("app.views.dashboard_view.PRAYER_NAMES", ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"])
    def test_create_dashboard_view_renders_properly(self):
        """
        Verifies the main dashboard frame is rendered with all labels and buttons.
        """
        frame = dashboard_view.create_dashboard_view(self.root, self.app_controller)

        # Confirm it's a CTkFrame instance
        self.assertIsInstance(frame, ctk.CTkFrame)

        # Confirm the controller got clock and countdown labels assigned
        self.assertTrue(hasattr(self.app_controller, "clock_label"))
        self.assertTrue(hasattr(self.app_controller, "countdown_label"))

        # Confirm prayer labels were created
        self.assertTrue(hasattr(self.app_controller, "prayer_labels"))
        self.assertIn("Fajr", self.app_controller.prayer_labels)
        fajr_label = self.app_controller.prayer_labels["Fajr"]
        self.assertEqual(fajr_label[1].cget("text"), "04:30")

    @patch("app.views.dashboard_view.PRAYER_NAMES", ["Fajr", "Dhuhr"])
    def test_prayer_labels_grid_structure(self):
        """
        Ensures that the prayer_labels dictionary is filled correctly with name and time label pairs.
        """
        frame = dashboard_view.create_dashboard_view(self.root, self.app_controller)

        labels = self.app_controller.prayer_labels
        self.assertIn("Fajr", labels)
        self.assertIn("Dhuhr", labels)

        # Each value should be a tuple of (name_label, time_label)
        self.assertEqual(len(labels["Fajr"]), 2)
        self.assertIsInstance(labels["Fajr"][0], ctk.CTkLabel)
        self.assertIsInstance(labels["Fajr"][1], ctk.CTkLabel)

        # Check initial time value for Dhuhr
        self.assertEqual(labels["Dhuhr"][1].cget("text"), "12:15")


if __name__ == '__main__':
    unittest.main()
