import requests

def get_market_context(query: str):
    # Placeholder simple version
    # Later swap with SerpAPI / Tavily / real search provider
    return {
        "trend_summary": f"Growing online interest detected for {query}.",
        "competitors": [
            f"{query} Pro",
            f"{query} Hub",
            f"{query} AI"
        ],
        "pricing_examples": ["$9/mo", "$19/mo", "Freemium"]
    }