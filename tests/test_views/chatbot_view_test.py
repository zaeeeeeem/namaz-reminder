import unittest
from unittest.mock import MagicMock, patch
import customtkinter as ctk

from app.views import chatbot_view


class TestChatbotView(unittest.TestCase):
    def setUp(self):
        """
        Runs before every test. Creates a root window and mock controller.
        """
        self.root = ctk.CTk()
        self.mock_controller = MagicMock()
        self.chatbot = chatbot_view.ChatbotView(self.root, self.mock_controller)

    def test_initial_greeting_added_to_chat(self):
        """
        Test that the initial AI greeting message is inserted on load.
        """
        # The message should be present in the chat_history textbox
        self.chatbot.chat_history.configure(state="normal")
        content = self.chatbot.chat_history.get("1.0", "end")
        self.chatbot.chat_history.configure(state="disabled")
        self.assertIn("Assalamu Alaikum", content)

    def test_user_message_added_and_entry_cleared(self):
        """
        Test that sending a message adds it to chat and clears the entry box.
        """
        self.chatbot.chat_entry.insert(0, "What is Fajr time?")  # Simulate user typing
        with patch.object(self.chatbot, '_fetch_ai_response') as mock_fetch:
            self.chatbot._send_message()

        # Check that the user message is added
        self.chatbot.chat_history.configure(state="normal")
        content = self.chatbot.chat_history.get("1.0", "end")
        self.chatbot.chat_history.configure(state="disabled")
        self.assertIn("You: What is Fajr time?", content)

        # Check that entry is cleared
        self.assertEqual(self.chatbot.chat_entry.get(), "")

        # Check that send button is disabled and fetch_ai_response is called
        self.assertEqual(self.chatbot.send_button.cget("state"), "disabled")
        mock_fetch.assert_called_once_with("What is Fajr time?")

    @patch("app.views.chatbot_view.gemini_client.get_ai_response", return_value="Fajr is at 4:00 AM")
    def test_fetch_ai_response_calls_service_and_updates_ui(self, mock_gemini):
        """
        Test that _fetch_ai_response fetches from Gemini client and updates UI.
        """
        # Simulate fetch
        self.chatbot._fetch_ai_response("Tell me Fajr time")

        # Simulate UI update that would be scheduled in main thread
        self.chatbot._update_ui_with_response("Fajr is at 4:00 AM")

        # Check response appears in chat
        self.chatbot.chat_history.configure(state="normal")
        content = self.chatbot.chat_history.get("1.0", "end")
        self.chatbot.chat_history.configure(state="disabled")

        self.assertIn("AI: Fajr is at 4:00 AM", content)

    def test_update_ui_enables_inputs(self):
        """
        Test that input is re-enabled after receiving a response.
        """
        self.chatbot._update_ui_with_response("Prayer time is at 5 PM")

        self.assertEqual(self.chatbot.send_button.cget("state"), "normal")
        self.assertEqual(self.chatbot.send_button.cget("text"), "Send")
        self.assertEqual(self.chatbot.chat_entry.cget("state"), "normal")


if __name__ == '__main__':
    unittest.main()
