# app/views/chatbot_view.py

import customtkinter as ctk
import threading

# Assuming gemini_client will be in the new services directory
from app.services import gemini_client


class ChatbotView:
    """
    Manages the UI and logic for the AI chatbot view, encapsulating its state and methods.
    """

    def __init__(self, parent, app_controller):
        """
        Initializes the ChatbotView class.

        Args:
            parent (ctk.CTk): The parent widget (the main app window).
            app_controller (MainView): The main application controller to call its methods.
        """
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.app_controller = app_controller
        self._build_widgets()

    def _build_widgets(self):
        """
        Creates and configures all the widgets for the chatbot UI.
        """
        title = ctk.CTkLabel(self.frame, text="Islamic Assistant", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        self.chat_history = ctk.CTkTextbox(self.frame, state="disabled", font=ctk.CTkFont(size=14), wrap="word")
        self.chat_history.pack(pady=10, padx=20, fill="both", expand=True)

        self._create_input_area()

        back_button = ctk.CTkButton(self.frame, text="Back to Dashboard", fg_color="#555", hover_color="#444",
                                    command=lambda: self.app_controller.show_frame("dashboard"))
        back_button.pack(pady=10, padx=20)

        self._add_message_to_chat("Assalamu Alaikum! How can I help you today?", "AI")

    def _create_input_area(self):
        """
        Creates the frame containing the text entry and send button.
        """
        input_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        input_frame.pack(pady=10, padx=20, fill="x")

        self.chat_entry = ctk.CTkEntry(input_frame, font=ctk.CTkFont(size=14), placeholder_text="Ask a question...")
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_entry.bind("<Return>", self._on_send_message_event)

        self.send_button = ctk.CTkButton(input_frame, text="Send", width=80, command=self._send_message)
        self.send_button.pack(side="right")

    def _add_message_to_chat(self, message: str, sender: str):
        """
        Adds a message from either the 'User' or 'AI' to the chat history box.

        Args:
            message (str): The content of the message.
            sender (str): The originator of the message, e.g., "You" or "AI".
        """
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")  # Auto-scroll to the bottom

    def _on_send_message_event(self, event):
        """Handles the <Return> key press to send a message."""
        self._send_message()

    def _send_message(self):
        """
        Gets user input, displays it, and starts the background thread to get an AI response.
        """
        user_input = self.chat_entry.get().strip()
        if not user_input:
            return

        self._add_message_to_chat(user_input, "You")
        self.chat_entry.delete(0, "end")

        self.send_button.configure(state="disabled", text="Typing...")
        self.chat_entry.configure(state="disabled")

        threading.Thread(target=self._fetch_ai_response, args=(user_input,), daemon=True).start()

    def _fetch_ai_response(self, user_input):
        """
        Calls the Gemini service in a background thread to avoid freezing the UI.

        Args:
            user_input (str): The prompt to send to the AI.
        """
        response_text = gemini_client.get_ai_response(user_input)
        # Schedule the UI update to run on the main thread
        self.frame.after(0, self._update_ui_with_response, response_text)

    def _update_ui_with_response(self, response_text):
        """
        Displays the AI's response in the chat and re-enables input. This runs on the main thread.

        Args:
            response_text (str): The text received from the AI service.
        """
        self._add_message_to_chat(response_text, "AI")
        self.send_button.configure(state="normal", text="Send")
        self.chat_entry.configure(state="normal")


def create_chatbot_view(parent, app_controller):
    """
    A factory function that creates an instance of the ChatbotView and returns its main frame.

    Args:
        parent (ctk.CTk): The parent widget (the main app window).
        app_controller (MainView): The instance of the main application controller.

    Returns:
        ctk.CTkFrame: The fully constructed chatbot view frame.
    """
    chatbot = ChatbotView(parent, app_controller)
    return chatbot.frame