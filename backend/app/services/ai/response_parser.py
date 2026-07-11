import json
from typing import Any, Dict


class ResponseParser:
    @staticmethod
    def parse_json(response_text: str) -> Dict[str, Any]:
        """
        Parse and sanitize JSON from LLM response text.
        Removes markdown wrappers (e.g. ```json ... ```) if present.
        """
        if not response_text:
            return {}

        cleaned = response_text.strip()

        # Remove markdown code block fences if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Fallback: attempt to find the JSON boundaries
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    pass
            raise ValueError(
                f"AI response is not valid JSON. Failed to parse: {str(e)}"
            ) from e
