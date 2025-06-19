import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# --- Configuration Section ---
# Get API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI only if API key exists
if not API_KEY:
    logging.critical("GEMINI_API_KEY not found in .env file. Please add it.")
    genai = None  # Disable AI functionality if no API key
else:
    genai.configure(api_key=API_KEY)  # Configure Gemini with the API key

# --- AI Behavior Settings ---
# System instructions that define how the AI should respond
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

# --- AI Model Initialization ---
# Create the Gemini model instance with our configuration
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',  # Using the lightweight Gemini model
    system_instruction=SYSTEM_INSTRUCTION  # Apply our behavior guidelines
)


# --- Core Function ---
def get_ai_response(user_prompt: str) -> str:
    """
    Get a response from the Gemini AI assistant for a given user prompt.

    Args:
        user_prompt (str): The question/message from the user

    Returns:
        str: The AI's response or an error message if something goes wrong
    """

    # Check if AI is properly configured
    if not genai:
        return "The AI assistant is not configured. Please check the API key."

    try:
        # Log the beginning of the request (first 30 chars for privacy)
        logging.info(f"Sending prompt to Gemini: '{user_prompt[:30]}...'")

        # Get response from Gemini
        response = model.generate_content(user_prompt)
        logging.info("Received response from Gemini.")

        return response.text

    except Exception as e:
        # Handle any errors that occur during the API call
        logging.error(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I am unable to respond at the moment. Please try again later."