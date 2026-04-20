from pydantic import BaseModel


class StartupRequest(BaseModel):
    idea: str
    audience: str = "general users"


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


class DecisionResponse(BaseModel):
    verdict: str
    risk_score: float
    reason: str
    suggested_pivot: str
    confidence_score: float


class StartupResponse(BaseModel):
    idea: str
    user_email: str
    research: ResearchResponse
    branding: BrandingResponse
    finance: FinanceResponse
    decision: DecisionResponse