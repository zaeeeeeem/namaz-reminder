import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------------------
# Load Environment Configuration
# ------------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ------------------------------
# Initialize Gemini Client
# ------------------------------

if not API_KEY:
    logging.critical("GEMINI_API_KEY not found in .env file. Gemini AI will be disabled.")
    genai = None
    model = None
else:
    genai.configure(api_key=API_KEY)

    # Define AI system instructions
    SYSTEM_INSTRUCTION = """
    You are a helpful and knowledgeable Islamic assistant.
    Your purpose is to provide accurate and respectful answers based on the Quran and Sunnah.

    Guidelines:
    1. Always be polite and encouraging
    2. For complex fiqh issues:
       - Provide general answers
       - Recommend consulting local scholars
    3. Avoid sectarian debates
    4. Stick to mainstream Islamic teachings
    5. Admit when you don't know something
    6. Keep answers concise and clear
    """

    # Create model instance
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )


# ------------------------------
# Core AI Function
# ------------------------------

def get_ai_response(user_prompt: str) -> str:
    """
    Generate a Gemini AI response based on user input.

    Args:
        user_prompt (str): The question/message from the user.

    Returns:
        str: AI response or an error message.
    """
    if not genai or not model:
        return "The AI assistant is not configured. Please check the API key."

    try:
        logging.info(f"Sending prompt to Gemini: '{user_prompt[:30]}...'")
        response = model.generate_content(user_prompt)
        logging.info("Received response from Gemini.")
        return response.text

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "Sorry, I’m unable to respond right now. Please try again later."
