from app.services.llm import ask_llm_with_provider
from app.utils.json_parser import parse_json_safely


def run_branding_agent(idea: str):
    prompt = f"""
Create premium branding for this startup idea: {idea}

Return ONLY valid JSON:
{{
  "startup_name": "...",
  "tagline": "...",
  "brand_tone": "...",
  "confidence_score": 0
}}
"""

    result, provider_used = ask_llm_with_provider(prompt, temperature=0.8)

    try:
        data = parse_json_safely(result)
    except Exception:
        data = {
            "startup_name": "NovaForge",
            "tagline": "Build smarter",
            "brand_tone": "Bold",
            "confidence_score": 65,
        }

    return {"data": data, "provider_used": provider_used}
