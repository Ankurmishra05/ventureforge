import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";

const features = [
  {
    title: "Research that closes the loop",
    description:
      "Unify market sizing, competitor signals, and founder insight into one decision-ready command center."
  },
  {
    title: "Positioning with strategic depth",
    description:
      "Generate messaging, offer architecture, and differentiation tailored to your ICP before launch."
  },
  {
    title: "Execution plans that ship",
    description:
      "Turn strategy into sprint-ready tasks across product, GTM, and fundraising without losing context."
  }
];

export function FeaturesSection() {
  return (
    <section id="features" className="px-6 py-24 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Features"
          title="Everything a serious founder needs in one premium workflow"
          description="VentureForge is designed for teams moving from idea to traction without fragmented tools or low-signal outputs."
        />

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Reveal key={feature.title} delay={index * 0.08}>
              <article className="h-full rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-8 shadow-glow">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/20 to-highlight/20 text-sm font-semibold text-accent">
                  0{index + 1}
                </div>
                <h3 className="mt-8 font-display text-2xl font-semibold text-white">
                  {feature.title}
                </h3>
                <p className="mt-4 text-base leading-7 text-slate-300">
                  {feature.description}
                </p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
