import json
import re

from app.services.llm import ask_llm
from app.services.ml import predict_startup_signal


def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def run_decision_agent(idea: str, research: dict, finance: dict):
    ml_signal = predict_startup_signal(idea, research.get("target_audience", "general users"))
    ml_context = ""
    if ml_signal is not None:
        ml_context = f"""
Baseline ML Signal:
- Predicted Verdict: {ml_signal["predicted_verdict"]}
- Predicted Risk Score: {ml_signal["predicted_risk_score"]}
- Build Probability: {ml_signal["build_probability"]}
- Pivot Probability: {ml_signal["pivot_probability"]}
- Avoid Probability: {ml_signal["avoid_probability"]}
"""

    prompt = f"""
You are a world-class startup investor.

Analyze the startup and return ONLY valid JSON.
No markdown. No explanation outside JSON.

Startup Idea: {idea}

Market Need: {research.get("market_need")}
Opportunity Score: {research.get("opportunity_score")}
Business Model: {finance.get("business_model")}
Revenue Projection: {finance.get("year1_revenue_projection")}
{ml_context}

Rules:
- verdict must be BUILD or PIVOT or AVOID
- risk_score must be 0 to 100
- confidence_score must be 0 to 100
- suggested_pivot must be useful and specific

Return JSON exactly in this format:

{{
  "verdict": "BUILD",
  "risk_score": 25,
  "reason": "Strong market demand with clear monetization.",
  "suggested_pivot": "AI resume coach for healthcare professionals",
  "confidence_score": 92
}}
"""

    try:
        raw = ask_llm(prompt)
        cleaned = extract_json(raw)
        data = json.loads(cleaned)

        return {
            "verdict": str(data.get("verdict", "PIVOT")).upper(),
            "risk_score": float(data.get("risk_score", 50)),
            "reason": str(data.get("reason", "Moderate opportunity.")),
            "suggested_pivot": str(
                data.get("suggested_pivot", "Target a niche audience")
            ),
            "confidence_score": float(data.get("confidence_score", 80)),
            "ml_signal": ml_signal,
        }

    except Exception:
        score = research.get("opportunity_score", 5)

        if score >= 8:
            verdict = "BUILD"
            risk = 25
        elif score >= 6:
            verdict = "PIVOT"
            risk = 50
        else:
            verdict = "AVOID"
            risk = 75

        return {
            "verdict": verdict,
            "risk_score": risk,
            "reason": "Heuristic evaluation based on market opportunity score.",
            "suggested_pivot": "Focus on a niche with urgent pain points.",
            "confidence_score": 78,
            "ml_signal": ml_signal,
        }
