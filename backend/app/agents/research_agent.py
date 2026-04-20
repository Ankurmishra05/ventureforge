from app.services.llm import ask_llm
from app.services.web_research import get_market_context
from app.utils.json_parser import parse_json_safely

def run_research_agent(idea, audience):
    context = get_market_context(idea)

    prompt = f"""
Analyze startup idea: {idea}
Audience: {audience}

Live Context:
Trend Summary: {context["trend_summary"]}
Competitors: {", ".join(context["competitors"])}
Pricing Examples: {", ".join(context["pricing_examples"])}

Return ONLY valid JSON:
{{
  "market_need": "...",
  "target_audience": "...",
  "pain_points": ["..."],
  "opportunity_score": 0,
  "confidence_score": 0
}}
"""

    result = ask_llm(prompt, temperature=0.3)

    try:
        return parse_json_safely(result)
    except:
        return {
            "market_need": context["trend_summary"],
            "target_audience": audience,
            "pain_points": ["High competition", "Customer acquisition"],
            "opportunity_score": 7,
            "confidence_score": 70
        }