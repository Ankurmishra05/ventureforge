from pydantic import BaseModel


class StartupRequest(BaseModel):
    idea: str
    audience: str = "general users"


class FutureFundingPredictionRequest(BaseModel):
    founded_year: int
    category: str
    country: str | None = None
    state: str | None = None
    city: str | None = None
    description: str = ""
    early_latest_round_type: str | None = None
    early_num_funding_rounds: int = 0
    early_total_raised_usd: float = 0
    early_avg_raised_usd: float = 0
    early_max_raised_usd: float = 0
    early_avg_participants: float = 0
    early_max_participants: float = 0


class FutureFundingPredictionResponse(BaseModel):
    predicted_probability: float
    predicted_label: int
    selected_threshold: float
    model_version: str
    task: str
    features_used: dict
    explanation: list[dict]


class ResearchResponse(BaseModel):
    market_need: str
    target_audience: str
    pain_points: list[str]
    opportunity_score: float
    confidence_score: float


class BrandingResponse(BaseModel):
    startup_name: str
    tagline: str
    brand_tone: str
    confidence_score: float


class FinanceResponse(BaseModel):
    business_model: str
    monthly_price_usd: float
    year1_revenue_projection: float
    break_even_month: int
    confidence_score: float


class MLSignalResponse(BaseModel):
    predicted_verdict: str
    predicted_risk_score: float
    build_probability: float
    pivot_probability: float
    avoid_probability: float
    model_version: str
    training_sample_count: int


class DecisionResponse(BaseModel):
    verdict: str
    risk_score: float
    reason: str
    suggested_pivot: str
    confidence_score: float
    ml_signal: MLSignalResponse | None = None


class StartupResponse(BaseModel):
    idea: str
    user_email: str
    research: ResearchResponse
    branding: BrandingResponse
    finance: FinanceResponse
    decision: DecisionResponse
