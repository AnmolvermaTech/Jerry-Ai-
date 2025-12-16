import os
import sys
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

model = None

def initialize_gemini():
    global model
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            print("FATAL: GOOGLE_API_KEY not found.")
            sys.exit()

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Gemini API initialized successfully.")

    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        sys.exit()

def get_gemini_response(query: str) -> str:
    if model is None:
        return "Sorry, the Gemini model is not initialized."

    try:
        formatted_query = f"""
You are Jerry, a friendly AI assistant.

Automatically detect the language style of the user (Hindi, English, or Hinglish mix)
and reply in the SAME style.

Response Rules (important):
- DO NOT use *, **, #, -, _, `, or markdown formatting.
- DO NOT use markdown headings.
- Keep output plain and clean.
- If listing points, use:
  1) point one
  2) point two
- Keep answers short, friendly, and clear.
- If user asks for code, output ONLY inside:

<code>
code here
</code>

User Request:
{query}
"""

        response = model.generate_content(formatted_query, stream=True)

        final_text = ""
        for chunk in response:
            if chunk.text:
                final_text += chunk.text

        final_text = final_text.strip()

        # --- REMOVE MARKDOWN SYMBOLS (safely) ---
        replacements = [
            ("**", ""), ("*", ""), ("###", ""), ("##", ""), ("#", ""),
            ("--", ""), ("_", ""), ("`", "")
        ]
        for old, new in replacements:
            final_text = final_text.replace(old, new)

        # Fix spacing
        final_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', final_text)

        return final_text

    except Exception as e:
        print(f"Error while getting Gemini response: {e}")
        return "Sorry, something went wrong."


def get_gemini_response_stream(query: str):
    if model is None:
        yield "Sorry, the Gemini model is not initialized."
        return

    formatted_query = f"""
You are Jerry, a friendly AI assistant.
Reply in simple clean text (no markdown).

User Request:
{query}
"""

    try:
        response = model.generate_content(formatted_query, stream=True)

        chunk_count = 0
        for chunk in response:
            if chunk.text:
                chunk_count += 1
                yield chunk.text.replace("*", "").replace("#", "").replace("_", "").replace("`", "")

        # 🚨 Gemini streamed NOTHING → fallback
        if chunk_count == 0:
            raise RuntimeError("Empty stream")

    except Exception:
        # 🔁 FALLBACK TO NORMAL RESPONSE
        try:
            text = get_gemini_response(query)
            yield text
        except:
            yield "Sorry, I am having trouble responding right now."

