from concurrent.futures import ThreadPoolExecutor

from app.agents.research_agent import run_research_agent
from app.agents.branding_agent import run_branding_agent
from app.agents.finance_agent import run_finance_agent
from app.agents.decision_agent import run_decision_agent
from app.utils.score import normalize_score


def generate_startup_plan(idea: str, audience: str):
    with ThreadPoolExecutor(max_workers=3) as executor:
        research_future = executor.submit(run_research_agent, idea, audience)
        branding_future = executor.submit(run_branding_agent, idea)
        finance_future = executor.submit(run_finance_agent, idea)

        research = research_future.result()
        branding = branding_future.result()
        finance = finance_future.result()

    provider_names = [
        research.get("provider_used", "unknown"),
        branding.get("provider_used", "unknown"),
        finance.get("provider_used", "unknown"),
    ]

    unique_providers = sorted(set(provider_names))

    provider_used = (
        unique_providers[0]
        if len(unique_providers) == 1
        else f"mixed:{', '.join(unique_providers)}"
    )

    research_data = research.get("data", research)
    branding_data = branding.get("data", branding)
    finance_data = finance.get("data", finance)

    decision_data = run_decision_agent(
        idea,
        research_data,
        finance_data
    )

    research_data["confidence_score"] = normalize_score(
        research_data.get("confidence_score", 0)
    )

    branding_data["confidence_score"] = normalize_score(
        branding_data.get("confidence_score", 0)
    )

    finance_data["confidence_score"] = normalize_score(
        finance_data.get("confidence_score", 0)
    )

    decision_data["confidence_score"] = normalize_score(
        decision_data.get("confidence_score", 0)
    )

    return {
        "idea": idea,
        "research": research_data,
        "branding": branding_data,
        "finance": finance_data,
        "decision": decision_data,
        "provider_used": provider_used,
    }