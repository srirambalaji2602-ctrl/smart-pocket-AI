import json
import re

from io import BytesIO
from typing import Any

from PIL import Image

from .recommendation_service import (
    home_fallback,
    jewelry_fallback,
    party_fallback,
)

from ..config import get_settings


settings = get_settings()


try:

    from google import genai
    from google.genai import types

except ImportError:

    genai = None
    types = None


class GeminiRecommendationService:

    def __init__(self):

        self.client = None

        if (
            settings.gemini_api_key
            and genai
        ):

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    @property
    def enabled(self):

        return self.client is not None

    def _extract_json(
        self,
        text: str,
    ):

        if not text:
            return None

        cleaned = text.strip()

        if cleaned.startswith("```"):

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL,
            )

            if match:

                try:

                    return json.loads(
                        match.group(0)
                    )

                except json.JSONDecodeError:

                    return None

        return None

    def _normalize(
        self,
        data: dict,
        fallback: dict,
    ):

        data.setdefault(
            "planner",
            fallback["planner"],
        )

        data.setdefault(
            "budget",
            fallback["budget"],
        )

        data.setdefault(
            "allocated_total",
            fallback["allocated_total"],
        )

        data.setdefault(
            "summary",
            fallback["summary"],
        )

        data.setdefault(
            "tips",
            fallback["tips"],
        )

        data.setdefault(
            "allocations",
            fallback["allocations"],
        )

        data.setdefault(
            "recommendations",
            [],
        )

        data["ai_used"] = True

        normalized = []

        for item in data.get(
            "recommendations",
            [],
        ):

            try:

                price = float(
                    item.get(
                        "estimated_price",
                        item.get(
                            "price",
                            0,
                        ),
                    )
                )

                quantity = max(
                    1,
                    int(
                        item.get(
                            "quantity",
                            1,
                        )
                    ),
                )

                normalized.append({

                    "category":
                        str(
                            item.get(
                                "category",
                                "General",
                            )
                        ),

                    "name":
                        str(
                            item.get(
                                "name",
                                "Recommended option",
                            )
                        ),

                    "estimated_price":
                        max(
                            0,
                            price,
                        ),

                    "quantity":
                        quantity,

                    "platform":
                        str(
                            item.get(
                                "platform",
                                "Amazon",
                            )
                        ),

                    "reason":
                        str(
                            item.get(
                                "reason",
                                (
                                    "Fits the stated "
                                    "budget and preferences."
                                ),
                            )
                        ),

                    "search_url":
                        str(
                            item.get(
                                "search_url",
                                "",
                            )
                        ),
                })

            except (
                TypeError,
                ValueError,
            ):

                continue

        data["recommendations"] = (
            normalized
            or fallback["recommendations"]
        )

        if not data.get(
            "allocated_total"
        ):

            data["allocated_total"] = round(
                sum(
                    item["estimated_price"]
                    * item["quantity"]
                    for item in normalized
                ),
                2,
            )

        return data

    def _prompt(
        self,
        planner: str,
        payload: dict,
    ):

        return f"""
You are PocketSmart AI, a practical
budget recommendation assistant.

Planner:
{planner}

User input:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Return ONLY valid JSON.

Use this structure:

{{
  "planner": "{planner}",
  "budget": number,
  "allocated_total": number,
  "summary": "short explanation",
  "tips": [
    "tip 1",
    "tip 2"
  ],
  "allocations": {{
    "category": number
  }},
  "recommendations": [
    {{
      "category": "category",
      "name": "generic product/service name",
      "estimated_price": number,
      "quantity": 1,
      "platform": "Amazon",
      "reason": "why it fits"
    }}
  ]
}}

Rules:

1. Keep estimated total at or below
the user's budget where practical.

2. Never invent live stock.

3. Never invent live price.

4. Never invent ratings.

5. Never invent reviews.

6. Never invent delivery dates.

7. Never invent vendor availability.

8. Use generic product/service names.

9. Keep recommendations practical.

10. Explain that prices are estimates.
"""

    def generate(
        self,
        planner: str,
        payload: dict,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ):

        fallback_map = {

            "home":
                home_fallback,

            "party":
                party_fallback,

            "jewelry":
                jewelry_fallback,
        }

        fallback = fallback_map[
            planner
        ](payload)

        if not self.enabled:

            return fallback

        try:

            prompt = self._prompt(
                planner,
                payload,
            )

            contents: list[Any] = [
                prompt
            ]

            if (
                image_bytes
                and planner == "jewelry"
            ):

                image = Image.open(
                    BytesIO(image_bytes)
                )

                contents.append(
                    image
                )

            response = (
                self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=1800,
                        response_mime_type="application/json",
                    ),
                )
            )

            parsed = self._extract_json(
                response.text
            )

            if not parsed:

                return fallback

            return self._normalize(
                parsed,
                fallback,
            )

        except Exception:

            return fallback


gemini_service = GeminiRecommendationService()