from openai import OpenAI, RateLimitError
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.schema import Report
import os
import json

load_dotenv()

SYSTEM_PROMPT = open(
    "prompts/analyst.md",
    encoding="utf-8"
).read()

class Analyst:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.chat = self.client.chats.create(
            model="gemini-3.5-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Report,
                temperature=0.2,
            ),
        )

    def analyze(self, context, history) -> Report:

        payload = {
            "context": context,
            "history": history,
        }

        response = self.chat.send_message(
            message=f"{SYSTEM_PROMPT}\n\n{json.dumps(payload, ensure_ascii=False, default=str)}"
        )

        return response.parsed