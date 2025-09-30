from google.generativeai import GenerativeModel, list_models
# This is the correct way to import the library
import google.generativeai as genai


# Replace with your actual API key
genai.configure(api_key="AIzaSyAZvyVxAdpE9kae87_JohNJm5TsEpeg37w") 

for m in list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)