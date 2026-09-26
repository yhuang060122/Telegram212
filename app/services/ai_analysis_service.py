import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.domain.analytics import PortfolioAnalytics
from app.domain.report import Report
from app.domain.research import ResearchContext
from app.logger import log

load_dotenv()

SYSTEM_PROMPT = open(
    "prompts/analyst.md",
    encoding="utf-8",
).read()


class AIAnalysisService:
    MODELS = [
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def analyze(
            self,
            context: ResearchContext,
            history: list[dict],
            analytics: PortfolioAnalytics,
    ) -> Report | None:

        payload = {
            "portfolio": context.portfolio.model_dump(),
            "analytics": analytics.model_dump(),
            "news": [n.model_dump() for n in context.news],
            "earnings": [e.model_dump() for e in context.earnings],
            "macro": context.macro.model_dump(),
            "history": history,
        }

        for model in self.MODELS:

            try:
                log.info("Analyze", f"Trying model: {model}")

                chat = self.client.chats.create(
                    model=model,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=Report,
                        temperature=0.2,
                    ),
                )

                response = chat.send_message(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + json.dumps(
                        payload,
                        ensure_ascii=False,
                    )
                )

                if response.parsed is None:
                    raise ValueError("Empty structured response")

                log.info("Analyze", f"Model {model} succeeded")
                return response.parsed

            except (ValidationError, ValueError) as e:
                log.warning("Analyze", f"{model} returned invalid JSON: {e}")

            except Exception as e:
                time.sleep(2)
                log.warning("Analyze", f"{model} failed: {e}", )

        log.error("Analyze", "All Gemini models failed.")
        return None
