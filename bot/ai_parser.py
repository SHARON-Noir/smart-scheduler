import ollama
import json
import os
import re
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def parse_event(text: str) -> dict:
    today = date.today()
    tomorrow = today + timedelta(days=1)

    prompt = f"""You are an event extraction assistant. Extract event details from the text below.

RULES:
- Always return valid JSON only
- No markdown, no code blocks, no explanation
- Title must ALWAYS be filled — use the main topic of the message
- If no date found, use today: {today.strftime("%Y-%m-%d")}
- If no time found, use null
- For "today" use {today.strftime("%Y-%m-%d")}
- For "tomorrow" use {tomorrow.strftime("%Y-%m-%d")}

TEXT: {text}

Return ONLY this JSON:
{{"title": "event title here", "date": "YYYY-MM-DD", "time": "HH:MM or null"}}"""

    try:
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response['message']['content'].strip()
        print(f"Raw AI response: {raw}")

        # strip markdown code blocks if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        # find JSON object using regex as fallback
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            raw = match.group()

        result = json.loads(raw)

        # fix null string
        if result.get("time") == "null":
            result["time"] = None

        # if title still empty use original text as fallback
        if not result.get("title"):
            result["title"] = text[:50]

        return result

    except json.JSONDecodeError:
        print(f"JSON parse failed. Raw output: {raw}")
        # last resort fallback
        return {
            "title": text[:50],
            "date": today.strftime("%Y-%m-%d"),
            "time": None
        }
    except Exception as e:
        print(f"Ollama error: {e}")
        return None