type ConfidenceBadgeProps = {
  score: number;
};

export function ConfidenceBadge({ score }: ConfidenceBadgeProps) {
  const tone =
    score >= 80
      ? "border-accent/30 bg-accent/10 text-accent"
      : score >= 65
        ? "border-amber-400/30 bg-amber-400/10 text-amber-200"
        : "border-rose-400/30 bg-rose-400/10 text-rose-200";

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${tone}`}
    >
      Confidence {score}%
    </span>
  );
}
