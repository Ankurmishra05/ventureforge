import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";

const testimonials = [
  {
    quote:
      "VentureForge compressed two weeks of founder ops into one afternoon and gave us a much sharper story for customers and investors.",
    name: "Elena Park",
    role: "Co-founder, Northstar Labs"
  },
  {
    quote:
      "The quality bar feels premium. We moved from vague idea to launch roadmap with outputs our team could actually use.",
    name: "Marcus Reed",
    role: "CEO, Signal Harbor"
  },
  {
    quote:
      "Most tools generate noise. VentureForge generated direction, sequencing, and conviction when we needed it most.",
    name: "Priya Nair",
    role: "Founder, Atlas Foundry"
  }
];

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="px-6 py-24 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Testimonials"
          title="Trusted by founders building with urgency"
          description="Teams use VentureForge when they need strategic depth, cleaner execution, and less wasted motion."
        />

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <Reveal key={testimonial.name} delay={index * 0.08}>
              <figure className="flex h-full flex-col justify-between rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-8">
                <blockquote className="text-lg leading-8 text-slate-200">
                  &ldquo;{testimonial.quote}&rdquo;
                </blockquote>
                <figcaption className="mt-8 border-t border-white/10 pt-6">
                  <div className="font-semibold text-white">{testimonial.name}</div>
                  <div className="text-sm text-slate-400">{testimonial.role}</div>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
