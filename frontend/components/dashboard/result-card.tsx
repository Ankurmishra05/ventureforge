import { ReactNode } from "react";

import { ConfidenceBadge } from "@/components/dashboard/confidence-badge";

type ResultCardProps = {
  title: string;
  confidenceScore: number;
  children: ReactNode;
};

export function ResultCard({
  title,
  confidenceScore,
  children
}: ResultCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-7 shadow-glow">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Analysis</p>
          <h2 className="mt-3 font-display text-2xl font-semibold text-white">{title}</h2>
        </div>
        <ConfidenceBadge score={confidenceScore} />
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}
