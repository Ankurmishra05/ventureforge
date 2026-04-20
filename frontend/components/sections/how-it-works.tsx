import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";

const steps = [
  {
    title: "Drop in an idea",
    description:
      "Start with a raw concept, problem statement, or market hunch. VentureForge converts it into a structured brief."
  },
  {
    title: "Run the venture engine",
    description:
      "Specialized workflows handle validation, branding, financial framing, and launch sequencing in parallel."
  },
  {
    title: "Ship with confidence",
    description:
      "Leave with strategic outputs your team can execute immediately, from landing page copy to investor narrative."
  }
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="px-6 py-24 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="How It Works"
          title="A faster path from concept to conviction"
          description="The workflow is deliberately simple so speed does not come at the cost of strategic quality."
        />

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {steps.map((step, index) => (
            <Reveal key={step.title} delay={index * 0.1}>
              <div className="relative overflow-hidden rounded-[1.75rem] border border-white/10 bg-panel p-8">
                <div className="absolute right-0 top-0 h-24 w-24 rounded-full bg-highlight/15 blur-2xl" />
                <span className="text-sm font-medium uppercase tracking-[0.3em] text-slate-500">
                  Step {index + 1}
                </span>
                <h3 className="mt-6 font-display text-2xl font-semibold text-white">
                  {step.title}
                </h3>
                <p className="mt-4 text-base leading-7 text-slate-300">
                  {step.description}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
