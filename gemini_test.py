import google.generativeai as genai
import os

# Replace this with your real API key from https://aistudio.google.com/app/apikey
os.environ["GOOGLE_API_KEY"] = "AIzaSyBev6saIEwXc01y_2cQe6pAJ8g-1OX_hnk"

# Configure the API client
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# List available Gemini models
for m in genai.list_models():
    print(m.name)
