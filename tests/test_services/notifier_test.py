import unittest
from unittest.mock import patch, MagicMock

from app.services import notifier


class TestNotifier(unittest.TestCase):

    @patch("app.services.notifier.os.path.exists", return_value=False)
    @patch("app.services.notifier.utils.logging.warning")
    @patch("app.services.notifier.config")
    def test_play_azan_sound_missing_file(self, mock_config, mock_log, mock_exists):
        mock_config.AZAN_SOUND_FILE = "nonexistent.mp3"
        notifier.play_azan_sound()
        mock_log.assert_called_with("Audio file not found at: nonexistent.mp3")

    @patch("app.services.notifier.pygame.mixer.music.stop")
    @patch("app.services.notifier.pygame.mixer.music.get_busy", return_value=True)
    @patch("app.services.notifier.pygame.mixer.get_init", return_value=True)
    @patch("app.services.notifier.utils.logging.info")
    def test_stop_azan_sound(self, mock_log, mock_get_init, mock_get_busy, mock_stop):
        notifier.stop_azan_sound()
        mock_stop.assert_called_once()
        mock_log.assert_called_with("Azan sound stopped.")

    @patch("app.services.notifier.pygame.mixer.music.play")
    @patch("app.services.notifier.pygame.mixer.music.load")
    @patch("app.services.notifier.pygame.mixer.init")
    @patch("app.services.notifier.pygame.mixer.get_init", return_value=False)
    @patch("app.services.notifier.os.path.exists", return_value=True)
    @patch("app.services.notifier.config")
    @patch("app.services.notifier.utils.logging.info")
    def test_play_azan_sound_success(
        self, mock_log, mock_config, mock_exists, mock_get_init, mock_init, mock_load, mock_play
    ):
        mock_config.AZAN_SOUND_FILE = "dummy.mp3"
        notifier.play_azan_sound()
        mock_load.assert_called_with("dummy.mp3")
        mock_play.assert_called_once()
        mock_log.assert_called_with("Azan sound started playing.")

    @patch("app.services.notifier.ctk.CTkToplevel")
    @patch("app.services.notifier._create_popup_widgets")
    @patch("app.services.notifier._center_popup_window")
    @patch("app.services.notifier.threading.Thread")
    def test_show_notification_popup_creates_window(
        self, mock_thread, mock_center, mock_create, mock_popup
    ):
        mock_popup_instance = MagicMock()
        mock_popup.return_value = mock_popup_instance

        notifier.show_notification_popup("Fajr", lambda: None, lambda: None)

        mock_popup.assert_called_once()
        mock_popup_instance.title.assert_called_with("Fajr Reminder")
        mock_center.assert_called_once()
        mock_create.assert_called_once()
        mock_popup_instance.focus_force.assert_called_once()


if __name__ == "__main__":
    unittest.main()
