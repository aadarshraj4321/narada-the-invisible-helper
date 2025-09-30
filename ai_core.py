import google.generativeai as genai
from google.api_core import exceptions

def get_ai_response(api_key, prompt):
    """Sends a prompt to the Gemini API and returns the text response."""
    if not api_key:
        return "Error: Gemini API key is not set. Please set it in the settings."
    
    try:
        genai.configure(api_key='AIzaSyAZvyVxAdpE9kae87_JohNJm5TsEpeg37w')
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text
        
    # --- FIX #2: Add more specific error catching ---
    except exceptions.NotFound as e:
        print(f"Gemini API Error (NotFound): {e}")
        return "Error: The AI model was not found. Your google-generativeai library might be outdated. Please run: pip install --upgrade google-generativeai"
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return f"Error: Could not get a response from the AI. Details: {e}"