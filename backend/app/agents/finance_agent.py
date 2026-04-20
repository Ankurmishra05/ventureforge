from app.services.llm import ask_llm_with_provider
from app.utils.json_parser import parse_json_safely


def run_finance_agent(idea: str):
    prompt = f"""
Create realistic startup financial plan for: {idea}

Return ONLY valid JSON:
{{
  "business_model": "...",
  "monthly_price_usd": 0,
  "year1_revenue_projection": 0,
  "break_even_month": 0,
  "confidence_score": 0
}}
"""

    result, provider_used = ask_llm_with_provider(prompt, temperature=0.3)

    try:
        data = parse_json_safely(result)
    except Exception:
        data = {
            "business_model": "Subscription",
            "monthly_price_usd": 10,
            "year1_revenue_projection": 50000,
            "break_even_month": 10,
            "confidence_score": 60,
        }

    return {"data": data, "provider_used": provider_used}
