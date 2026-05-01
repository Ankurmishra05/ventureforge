"use client";

import axios from "axios";
import { FormEvent, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/dashboard/error-state";
import { LoadingState } from "@/components/dashboard/loading-state";
import { ResultCard } from "@/components/dashboard/result-card";
import { RevenueChart } from "@/components/dashboard/revenue-chart";
import { clearAuthSession, generateStartup, predictFutureFunding } from "@/lib/api";
import type {
  FutureFundingPredictionResponse,
  StartupResponse
} from "@/lib/types";

const initialForm = {
  idea: "",
  audience: ""
};

const initialPredictionForm = {
  founded_year: "2010",
  category: "enterprise",
  country: "USA",
  state: "CA",
  city: "San Francisco",
  description: "",
  early_latest_round_type: "series_a",
  early_num_funding_rounds: "1",
  early_total_raised_usd: "1000000",
  early_avg_raised_usd: "1000000",
  early_max_raised_usd: "1000000",
  early_avg_participants: "2",
  early_max_participants: "2"
};

export function DashboardShell() {
  const router = useRouter();

  const [form, setForm] = useState(initialForm);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requiresAuth, setRequiresAuth] = useState(false);
  const [result, setResult] = useState<StartupResponse | null>(null);
  const [predictionForm, setPredictionForm] = useState(initialPredictionForm);
  const [predictionResult, setPredictionResult] =
    useState<FutureFundingPredictionResponse | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  function handleLogout() {
    clearAuthSession();
    router.push("/login");
  }

  const averageConfidence = useMemo(() => {
    if (!result) return null;

    const total =
      result.research.confidence_score +
      result.branding.confidence_score +
      result.finance.confidence_score;

    return Math.round(total / 3);
  }, [result]);

  async function runGeneration() {
    setIsLoading(true);
    setError(null);
    setRequiresAuth(false);
    setResult(null);

    try {
      const data = await generateStartup({
        idea: form.idea.trim(),
        audience: form.audience.trim() || "general users"
      });

      setResult(data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail =
          typeof err.response?.data === "string"
            ? err.response.data
            : typeof err.response?.data?.detail === "string"
              ? err.response.data.detail
              : "The API is unavailable or returned an invalid response.";

        setRequiresAuth(err.response?.status === 401);
        setError(detail);
      } else {
        setError("Something unexpected happened while contacting the API.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runGeneration();
  }

  async function retryGeneration() {
    await runGeneration();
  }

  async function handlePredictionSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPredictionError(null);
    setPredictionResult(null);
    setIsPredicting(true);

    try {
      const data = await predictFutureFunding({
        founded_year: Number(predictionForm.founded_year),
        category: predictionForm.category.trim(),
        country: predictionForm.country.trim() || undefined,
        state: predictionForm.state.trim() || undefined,
        city: predictionForm.city.trim() || undefined,
        description: predictionForm.description.trim(),
        early_latest_round_type:
          predictionForm.early_latest_round_type.trim() || undefined,
        early_num_funding_rounds: Number(predictionForm.early_num_funding_rounds),
        early_total_raised_usd: Number(predictionForm.early_total_raised_usd),
        early_avg_raised_usd: Number(predictionForm.early_avg_raised_usd),
        early_max_raised_usd: Number(predictionForm.early_max_raised_usd),
        early_avg_participants: Number(predictionForm.early_avg_participants),
        early_max_participants: Number(predictionForm.early_max_participants)
      });

      setPredictionResult(data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail =
          typeof err.response?.data === "string"
            ? err.response.data
            : typeof err.response?.data?.detail === "string"
              ? err.response.data.detail
              : "The prediction API is unavailable or returned an invalid response.";
        setPredictionError(detail);
      } else {
        setPredictionError("Something unexpected happened while scoring the startup.");
      }
    } finally {
      setIsPredicting(false);
    }
  }

  async function exportPdf() {
    if (!result) return;

    const response = await axios.post(
      "http://127.0.0.1:8000/export/pdf",
      {
        idea: result.idea,
        startup_name: result.branding.startup_name,
        tagline: result.branding.tagline,
        market_need: result.research.market_need,
        business_model: result.finance.business_model,
        revenue: result.finance.year1_revenue_projection
      },
      { responseType: "blob" }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = "ventureforge_report.pdf";
    link.click();
  }

  async function exportPitch() {
    if (!result) return;

    const response = await axios.post(
      "http://127.0.0.1:8000/export/pitch",
      {
        idea: result.idea,
        startup_name: result.branding.startup_name,
        tagline: result.branding.tagline,
        market_need: result.research.market_need,
        business_model: result.finance.business_model,
        revenue: result.finance.year1_revenue_projection
      },
      { responseType: "blob" }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = "ventureforge_pitch.pptx";
    link.click();
  }

  return (
    <div className="min-h-screen bg-hero-radial px-6 py-10 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex justify-end">
          <button
            onClick={handleLogout}
            className="rounded-full border border-white/10 px-5 py-2 text-sm text-white hover:bg-white/10"
          >
            Logout
          </button>
        </div>

        <div className="grid gap-8 xl:grid-cols-[420px_minmax(0,1fr)]">
          <motion.aside
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="h-fit rounded-[2rem] border border-white/10 bg-panel/80 p-7 shadow-glow backdrop-blur"
          >
            <p className="text-sm uppercase tracking-[0.3em] text-accent">
              Dashboard
            </p>

            <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight text-white">
              Forge a startup brief in one pass
            </h1>

            <p className="mt-4 text-base leading-7 text-slate-300">
              Submit a startup concept and audience. VentureForge will generate
              market research, branding, finance, and strategic decisions.
            </p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="idea" className="text-sm font-medium text-slate-200">
                  Startup idea
                </label>

                <textarea
                  id="idea"
                  value={form.idea}
                  onChange={(e) =>
                    setForm((current) => ({
                      ...current,
                      idea: e.target.value
                    }))
                  }
                  rows={5}
                  placeholder="Describe the product, problem, and business angle."
                  className="mt-2 w-full rounded-3xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-white outline-none placeholder:text-slate-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="audience" className="text-sm font-medium text-slate-200">
                  Target audience
                </label>

                <input
                  id="audience"
                  type="text"
                  value={form.audience}
                  onChange={(e) =>
                    setForm((current) => ({
                      ...current,
                      audience: e.target.value
                    }))
                  }
                  placeholder="Founders, creators, B2B teams, students..."
                  className="mt-2 w-full rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !form.idea.trim()}
                className="inline-flex w-full items-center justify-center rounded-full bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 disabled:opacity-60"
              >
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>

            <div className="mt-10 border-t border-white/10 pt-8">
              <p className="text-sm uppercase tracking-[0.3em] text-accent">
                ML Scoring
              </p>
              <h2 className="mt-4 font-display text-2xl font-semibold text-white">
                Score future funding probability
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Uses the trained Kaggle-based benchmark model with early-stage features.
              </p>

              <form className="mt-6 space-y-4" onSubmit={handlePredictionSubmit}>
                <input
                  value={predictionForm.description}
                  onChange={(e) =>
                    setPredictionForm((current) => ({
                      ...current,
                      description: e.target.value
                    }))
                  }
                  placeholder="Company description"
                  className="w-full rounded-3xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                />

                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    value={predictionForm.category}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        category: e.target.value
                      }))
                    }
                    placeholder="Category"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.founded_year}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        founded_year: e.target.value
                      }))
                    }
                    placeholder="Founded year"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.country}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        country: e.target.value
                      }))
                    }
                    placeholder="Country"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.state}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        state: e.target.value
                      }))
                    }
                    placeholder="State"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.city}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        city: e.target.value
                      }))
                    }
                    placeholder="City"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_latest_round_type}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_latest_round_type: e.target.value
                      }))
                    }
                    placeholder="Latest early round type"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_num_funding_rounds}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_num_funding_rounds: e.target.value
                      }))
                    }
                    placeholder="Early rounds"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_total_raised_usd}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_total_raised_usd: e.target.value
                      }))
                    }
                    placeholder="Early total raised USD"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_avg_raised_usd}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_avg_raised_usd: e.target.value
                      }))
                    }
                    placeholder="Early average raised USD"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_max_raised_usd}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_max_raised_usd: e.target.value
                      }))
                    }
                    placeholder="Early max raised USD"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_avg_participants}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_avg_participants: e.target.value
                      }))
                    }
                    placeholder="Early average participants"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                  <input
                    value={predictionForm.early_max_participants}
                    onChange={(e) =>
                      setPredictionForm((current) => ({
                        ...current,
                        early_max_participants: e.target.value
                      }))
                    }
                    placeholder="Early max participants"
                    className="rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isPredicting || !predictionForm.category.trim()}
                  className="inline-flex w-full items-center justify-center rounded-full border border-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:opacity-60"
                >
                  {isPredicting ? "Scoring..." : "Score Future Funding"}
                </button>
              </form>
            </div>
          </motion.aside>

          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.08 }}
            className="space-y-8"
          >
            {isLoading && <LoadingState />}

            {!isLoading && error && (
              <ErrorState
                message={error}
                onRetry={retryGeneration}
                requiresAuth={requiresAuth}
              />
            )}

            {!isLoading && !error && result && (
              <>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={exportPdf}
                    className="rounded-full bg-accent px-5 py-2 text-sm font-semibold text-slate-950"
                  >
                    Export PDF
                  </button>

                  <button
                    onClick={exportPitch}
                    className="rounded-full border border-white/10 px-5 py-2 text-sm text-white"
                  >
                    Pitch Deck
                  </button>

                  <button
                    onClick={retryGeneration}
                    className="rounded-full border border-white/10 px-5 py-2 text-sm text-white"
                  >
                    Regenerate
                  </button>
                </div>

                <div className="grid gap-6 md:grid-cols-4">
                  <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-6">
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-500">
                      Startup
                    </p>
                    <h2 className="mt-4 text-2xl font-semibold text-white">
                      {result.branding.startup_name || result.idea}
                    </h2>
                    <p className="mt-3 text-sm text-slate-300">
                      {result.branding.tagline}
                    </p>
                  </div>

                  <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-6">
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-500">
                      Audience
                    </p>
                    <p className="mt-4 text-lg font-semibold text-white">
                      {result.research.target_audience}
                    </p>
                  </div>

                  <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-6">
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-500">
                      Confidence
                    </p>
                    <p className="mt-4 text-3xl font-semibold text-accent">
                      {averageConfidence ?? 0}%
                    </p>
                  </div>

                  <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-6">
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-500">
                      AI Verdict
                    </p>
                    <p className="mt-4 text-2xl font-bold text-white">
                      {result.decision?.verdict || "N/A"}
                    </p>
                    <p className="mt-3 text-sm text-slate-300">
                      Risk: {result.decision?.risk_score ?? 0}%
                    </p>
                  </div>
                </div>

                <div className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_360px]">
                  <div className="space-y-6">
                    <ResultCard
                      title="Market Research"
                      confidenceScore={result.research.confidence_score}
                    >
                      <p>{result.research.market_need}</p>
                    </ResultCard>

                    <ResultCard
                      title="Branding"
                      confidenceScore={result.branding.confidence_score}
                    >
                      <p>{result.branding.startup_name}</p>
                      <p>{result.branding.tagline}</p>
                    </ResultCard>

                    <ResultCard
                      title="Finance"
                      confidenceScore={result.finance.confidence_score}
                    >
                      <p>{result.finance.business_model}</p>
                      <p>${result.finance.monthly_price_usd}</p>
                    </ResultCard>

                    <ResultCard
                      title="Strategic Decision"
                      confidenceScore={result.decision?.confidence_score ?? 0}
                    >
                      <p>{result.decision?.reason}</p>
                      <p className="mt-2 text-accent">
                        Pivot: {result.decision?.suggested_pivot}
                      </p>
                    </ResultCard>
                  </div>

                  <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-7 shadow-glow">
                    <h2 className="text-2xl font-semibold text-white">
                      Revenue Chart
                    </h2>

                    <div className="mt-8">
                      <RevenueChart
                        monthlyPrice={result.finance.monthly_price_usd}
                        yearOneRevenue={result.finance.year1_revenue_projection}
                        breakEvenMonth={result.finance.break_even_month}
                      />
                    </div>
                  </div>
                </div>
              </>
            )}

            {!isPredicting && predictionError && (
              <div className="rounded-[1.5rem] border border-rose-500/20 bg-rose-500/10 p-5 text-sm text-rose-100">
                {predictionError}
              </div>
            )}

            {predictionResult && (
              <div className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_320px]">
                <ResultCard title="Future Funding Prediction" confidenceScore={Math.round(predictionResult.predicted_probability * 100)}>
                  <div className="space-y-4 text-sm text-slate-200">
                    <p className="text-3xl font-semibold text-white">
                      {Math.round(predictionResult.predicted_probability * 100)}%
                    </p>
                    <p>
                      Decision threshold: {Math.round(predictionResult.selected_threshold * 100)}%
                    </p>
                    <p>
                      Model verdict: {predictionResult.predicted_label === 1 ? "Likely future funding" : "Below funding threshold"}
                    </p>
                    <p className="text-slate-400">
                      Model: {predictionResult.model_version}
                    </p>
                  </div>
                </ResultCard>

                <ResultCard title="Top Drivers" confidenceScore={Math.round(predictionResult.predicted_probability * 100)}>
                  <div className="space-y-3 text-sm text-slate-200">
                    {predictionResult.explanation.map((item) => (
                      <div
                        key={item.feature}
                        className="rounded-2xl border border-white/10 bg-slate-950/40 p-4"
                      >
                        <p className="font-semibold text-white">{item.feature}</p>
                        <p className="mt-1 text-slate-300">
                          {item.direction} score by about {Math.round(item.impact * 100)} points
                        </p>
                        <p className="mt-1 text-slate-500">
                          Value: {String(item.value ?? "unknown")}
                        </p>
                      </div>
                    ))}
                  </div>
                </ResultCard>
              </div>
            )}

            {!isLoading && !error && !result && !predictionResult && (
              <div className="flex min-h-[520px] items-center justify-center rounded-[2rem] border border-dashed border-white/10 bg-white/[0.03] p-10 text-center">
                <div className="max-w-xl">
                  <h2 className="text-3xl font-semibold text-white">
                    Generate a structured venture snapshot
                  </h2>
                  <p className="mt-4 text-slate-300">
                    The dashboard will populate research, branding, finance,
                    confidence, decisions, and charts once the request completes.
                  </p>
                </div>
              </div>
            )}
          </motion.section>
        </div>
      </div>
    </div>
  );
}
