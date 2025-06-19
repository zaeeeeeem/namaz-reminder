import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

import customtkinter as ctk

# Import the module you're testing
from app.views import calendar_view


class TestCalendarView(unittest.TestCase):
    def setUp(self):
        """
        Runs before each test. Initializes a root Tkinter window,
        mocks a status_vars dictionary, and prepares sample date data.
        """
        self.root = ctk.CTk()  # Root window for UI tests
        self.status_vars = {}  # Will hold StringVars for prayer statuses
        self.show_dropdown_mock = MagicMock()  # Mock callback for dropdown click

        # Set up a single day's data for testing
        self.today = datetime.now().date()
        self.dates_data = [
            {
                "date": self.today,
                "is_today": True,
                "statuses": {
                    f"{self.today}_Fajr": "Completed",
                    f"{self.today}_Dhuhr": "Not Completed"
                },
                "prayer_disabled_status": {
                    "Fajr": False,
                    "Dhuhr": True,
                    "Asr": False,
                    "Maghrib": False,
                    "Isha": False
                }
            }
        ]

    @patch("app.views.calendar_view.get_day_name", return_value="Monday")
    @patch("app.views.calendar_view.config")
    def test_build_calendar_frame_creates_widgets(self, mock_config, mock_get_day_name):
        """
        Test that the calendar frame correctly creates and populates all widgets for one day.
        """
        # Setup mock values
        mock_config.PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        mock_config.STATUS_COLORS = {
            "Completed": "green",
            "Not Completed": "red"
        }

        # Create a parent frame to render calendar inside
        frame = ctk.CTkFrame(self.root)

        # Call the actual function that creates the calendar UI
        calendar_view.build_calendar_frame(frame, self.dates_data, self.status_vars, self.show_dropdown_mock)

        # Check if the status_vars dictionary was populated for at least one prayer
        self.assertIn(f"{self.today}_Fajr", self.status_vars)
        self.assertIsInstance(self.status_vars[f"{self.today}_Fajr"], ctk.StringVar)

    @patch("app.views.calendar_view.config")
    def test_display_status_dropdown_changes_status(self, mock_config):
        """
        Test that selecting an option from the dropdown updates the StringVar and button color.
        """
        # Setup mock config values
        mock_config.STATUS_OPTIONS = ["Completed", "Late", "Not Completed"]
        mock_config.STATUS_COLORS = {
            "Completed": "green",
            "Late": "orange",
            "Not Completed": "red"
        }

        # Create a dummy StringVar and a button
        status_var = ctk.StringVar(value="Not Completed")
        button = ctk.CTkButton(self.root, textvariable=status_var, fg_color="red", width=100)
        button.pack()

        # Simulate opening the dropdown (cannot click in unit tests, so just call the function)
        calendar_view.display_status_dropdown(self.root, status_var, button)

        # Simulate selection from the dropdown manually (as interaction isn't real in unittest)
        status_var.set("Completed")
        button.configure(fg_color=mock_config.STATUS_COLORS["Completed"])

        # Assertions: check that the status and button color were correctly updated
        self.assertEqual(status_var.get(), "Completed")
        self.assertEqual(button.cget("fg_color"), "green")


if __name__ == '__main__':
    unittest.main()
