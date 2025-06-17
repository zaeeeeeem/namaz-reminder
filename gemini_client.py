import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# --- Setup ---

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    logging.critical("GEMINI_API_KEY not found in .env file. Please add it.")
    genai = None
else:
    genai.configure(api_key=API_KEY)


SYSTEM_INSTRUCTION = """You are a helpful and knowledgeable Islamic assistant. 
Your purpose is to provide accurate and respectful answers based on the Quran and Sunnah.
- Always be polite and encouraging.
- If you are asked about a complex fiqh (jurisprudence) issue, provide a general answer and advise the user to consult a qualified local scholar for specific rulings.
- Do not engage in debates about sects or controversial topics.
- Your knowledge base is mainstream Islamic teachings.
- If you don't know an answer, say so honestly rather than guessing.
- Keep answers concise and easy to understand.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

def get_ai_response(user_prompt: str) -> str:
    if not genai:
        return "The AI assistant is not configured. Please check the API key."

    try:
        logging.info(f"Sending prompt to Gemini: '{user_prompt[:30]}...'")
        response = model.generate_content(user_prompt)
        logging.info("Received response from Gemini.")
        return response.text
    except Exception as e:
        logging.error(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I am unable to respond at the moment. Please try again later."