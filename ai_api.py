import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def ask_gemini_vision(prompt: str, base64_image: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        {"text": prompt},
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64_image
            }
        }
    ])
    return response.text
