import customtkinter as ctk
import threading
from app.services import gemini_client


def create_chatbot_frame(app):
    """Create the AI ChatBot frame."""

    frame = ctk.CTkFrame(app.app)

    ctk.CTkLabel(frame, text="Ask Islamic Questions", font=("Arial", 16)).pack(pady=10)

    input_field = ctk.CTkEntry(frame, width=300, placeholder_text="Ask a question...")
    input_field.pack(pady=5)

    output_text = ctk.CTkTextbox(frame, height=200, width=300, state="disabled")
    output_text.pack(pady=10)

    def get_ai_response():
        question = input_field.get()
        output_text.configure(state="normal")
        output_text.delete("1.0", "end")
        output_text.insert("end", "Thinking...\n")
        output_text.configure(state="disabled")

        def ask():
            try:
                response = gemini_client.ask_gemini(question)
                output_text.configure(state="normal")
                output_text.delete("1.0", "end")
                output_text.insert("end", response)
                output_text.configure(state="disabled")
            except Exception as e:
                output_text.configure(state="normal")
                output_text.delete("1.0", "end")
                output_text.insert("end", f"Error: {str(e)}")
                output_text.configure(state="disabled")

        threading.Thread(target=ask).start()

    ctk.CTkButton(frame, text="Ask", command=get_ai_response).pack()
    ctk.CTkButton(frame, text="Back", command=lambda: app.show_frame("dashboard")).pack(pady=5)

    return frame
