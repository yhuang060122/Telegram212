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

    def analyze(self, context, history):

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=SYSTEM_PROMPT),
                        types.Part.from_text(
                            text=str({
                                "context": context,
                                "history": history
                            })
                        )
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Report,
                temperature=0.2,
            ),
        )

        return response.parsed