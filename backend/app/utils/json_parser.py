import json
import re

def parse_json_safely(text: str):
    text = text.strip()

    # Remove markdown code fences
    text = text.replace("```json", "").replace("```", "")

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)