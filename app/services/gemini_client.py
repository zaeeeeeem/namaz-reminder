# app/services/gemini_client.py
"""
This service module handles all communication with the Google Gemini AI.
It is responsible for initializing the client with the proper system
instructions and for fetching responses to user prompts.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from app.utils import utils

def _initialize_ai_model():
    """
    Sets up and configures the Gemini generative model.

    This function loads the API key from the environment, sets the system
    instructions for the AI's personality and behavior, and initializes
    the model object.

    Returns:
        genai.GenerativeModel: An initialized model object, or None if setup fails.
    """
    # Load environment variables from a .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        utils.logging.critical("GEMINI_API_KEY not found in .env file. AI service will be disabled.")
        return None

    try:
        genai.configure(api_key=api_key)

        # Define the persona and rules for the AI assistant
        system_instruction = """
        You are a helpful and knowledgeable Islamic assistant.
        Your purpose is to provide accurate and respectful answers based on the Quran and Sunnah.

        Guidelines:
        1. Always be polite, respectful, and encouraging.
        2. For complex Fiqh (jurisprudence) issues, provide a general answer and strongly advise the user to consult a qualified local scholar for specific rulings.
        3. Politely decline to engage in sectarian debates or controversial topics.
        4. Base your knowledge on mainstream, orthodox Islamic teachings.
        5. If you do not know an answer, admit it honestly rather than fabricating information.
        6. Keep answers concise, clear, and easy to understand for a general audience.
        """

        # Create and return the model instance
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        utils.logging.info("Gemini AI model initialized successfully.")
        return model

    except Exception as e:
        utils.logging.error(f"Failed to initialize Gemini AI model: {e}")
        return None

# --- Module-level Initialization ---
# The model is initialized once when the module is first imported.
model = _initialize_ai_model()


def get_ai_response(user_prompt: str) -> str:
    """
    Generates a response from the Gemini AI based on the user's input.

    Args:
        user_prompt (str): The question or message from the user.

    Returns:
        str: The text response from the AI, or an error message if something goes wrong.
    """
    # Check if the model was initialized successfully
    if not model:
        return "The AI assistant is not configured. Please verify the API key and setup."

    try:
        utils.logging.info(f"Sending prompt to Gemini: '{user_prompt[:40]}...'")
        response = model.generate_content(user_prompt)
        utils.logging.info("Received response from Gemini.")
        return response.text

    except Exception as e:
        utils.logging.error(f"An error occurred during Gemini API call: {e}")
        return "Sorry, I am unable to respond at the moment. Please try again later."