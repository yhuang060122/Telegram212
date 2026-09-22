from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.schema import Report
from pydantic import ValidationError
import os
import json
import time
from app.logger import log

load_dotenv()

SYSTEM_PROMPT = open(
    "prompts/analyst.md",
    encoding="utf-8"
).read()

class Analyst:

    MODELS = [
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def analyze(self, context, history) -> Report | None:

        payload = {
            "context": context,
            "history": history,
        }

        for model in self.MODELS:
            for attempt in range(2):
                try:
                    log.info("Analyze", "Trying model: %s", model)

                    self.chat = self.client.chats.create(
                        model=model,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=Report,
                            temperature=0.2,
                        ),
                    )

                    response = self.chat.send_message(
                        message=f"{SYSTEM_PROMPT}\n\n{json.dumps(payload, ensure_ascii=False, default=str)}"
                    )

                    if response.parsed is None:
                        raise ValueError("Empty structured response")

                    log.info("Analyze", "Model %s succeeded", model)
                    return response.parsed

                except (ValidationError, ValueError) as e:
                    log.warning("Analyze", "%s returned invalid JSON: %s", model, e)

                except Exception as e:
                    if attempt == 0:
                        time.sleep(2)   # 等 2 秒再试一次
                    else:
                        log.warning("Analyze", "%s failed twice", model)

        log.error("Analyze", "All Gemini models failed.")
        return None