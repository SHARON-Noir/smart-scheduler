import ollama
import json
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def parse_event(text: str) -> dict:
    today = date.today().strftime("%Y-%m-%d")

    prompt = f"""Extract event details from this text and reply in JSON only.
No explanation, no extra text, no markdown, just raw JSON.

Today's date is {today}. Use this if user says 'today' or 'tomorrow'.

Text: {text}

Reply in this exact format:
{{
  "title": "event name here",
  "date": "YYYY-MM-DD",
  "time": "HH:MM"
}}

If you cannot find a date use null. If you cannot find a time use null."""

    try:
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response['message']['content'].strip()

        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        print(f"JSON parse failed. Raw output: {raw}")
        return None
    except Exception as e:
        print(f"Ollama error: {e}")
        return None