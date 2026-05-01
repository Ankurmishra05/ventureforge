export type StartupRequest = {
  idea: string;
  audience: string;
};

export type FutureFundingPredictionRequest = {
  founded_year: number;
  category: string;
  country?: string;
  state?: string;
  city?: string;
  description: string;
  early_latest_round_type?: string;
  early_num_funding_rounds: number;
  early_total_raised_usd: number;
  early_avg_raised_usd: number;
  early_max_raised_usd: number;
  early_avg_participants: number;
  early_max_participants: number;
};

export type FutureFundingPredictionResponse = {
  predicted_probability: number;
  predicted_label: number;
  selected_threshold: number;
  model_version: string;
  task: string;
  features_used: Record<string, string | number | null>;
  explanation: Array<{
    feature: string;
    value: string | number | null;
    direction: string;
    impact: number;
  }>;
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
  decision: {
    verdict: string;
    risk_score: number;
    reason: string;
    suggested_pivot: string;
    confidence_score: number;
    ml_signal?: {
      predicted_verdict: string;
      predicted_risk_score: number;
      build_probability: number;
      pivot_probability: number;
      avoid_probability: number;
      model_version: string;
      training_sample_count: number;
    } | null;
  };
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
