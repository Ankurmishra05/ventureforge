import time
import json
from app.workflows.orchestrator import generate_startup_plan

TEST_CASES = [
    {"idea": "AI resume coach", "audience": "job seekers"},
    {"idea": "AI tax assistant", "audience": "freelancers"},
    {"idea": "Mental wellness app", "audience": "remote workers"},
    {"idea": "SaaS for restaurants", "audience": "small businesses"},
]

def score_output(result):
    score = 0

    # 1. Market depth
    if len(result["research"]["market_need"]) > 50:
        score += 2

    # 2. Branding creativity
    if len(result["branding"]["startup_name"]) > 3:
        score += 1
    if len(result["branding"]["tagline"]) > 10:
        score += 1

    # 3. Finance realism
    revenue = result["finance"]["year1_revenue_projection"]
    if 10000 < revenue < 10000000:
        score += 2

    # 4. Decision reasoning quality
    reason = result.get("decision", {}).get("reason", "")
    if len(reason) > 40:
        score += 2

    # 5. Verdict presence
    if result.get("decision", {}).get("verdict") in ["BUILD", "PIVOT", "AVOID"]:
        score += 2

    return score


def run():
    results = []

    for case in TEST_CASES:
        start = time.time()

        output = generate_startup_plan(case["idea"], case["audience"])

        latency = time.time() - start
        quality = score_output(output)

        results.append({
            "idea": case["idea"],
            "latency": round(latency, 2),
            "quality_score": quality,
            "provider": output.get("provider_used")
        })

    print("\n=== Evaluation Results ===\n")
    for r in results:
        print(r)

    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    run()