export type StartupRequest = {
  idea: string;
  audience: string;
};

export type ResearchResult = {
  market_need: string;
  target_audience: string;
  pain_points: string[];
  opportunity_score: number;
  confidence_score: number;
};

export type BrandingResult = {
  startup_name: string;
  tagline: string;
  brand_tone: string;
  confidence_score: number;
};

export type FinanceResult = {
  business_model: string;
  monthly_price_usd: number;
  year1_revenue_projection: number;
  break_even_month: number;
  confidence_score: number;
};

export type StartupResponse = {
  idea: string;
  user_email: string;
  research: ResearchResult;
  branding: BrandingResult;
  finance: FinanceResult;
};

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: AuthUser;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  full_name: string;
  password: string;
};
