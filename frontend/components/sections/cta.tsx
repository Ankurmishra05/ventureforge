import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/ui/reveal";

export function CtaSection() {
  return (
    <section id="cta" className="px-6 pb-24 pt-8 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-5xl">
        <Reveal>
          <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/8 to-white/[0.03] p-10 shadow-glow sm:p-14">
            <div className="max-w-3xl">
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-accent">
                Ready to move
              </p>
              <h2 className="mt-5 font-display text-3xl font-semibold tracking-tight text-white sm:text-5xl">
                Replace scattered founder tooling with one focused venture workspace
              </h2>
              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
                Start generating strategy, positioning, and launch plans that are built to ship.
              </p>
            </div>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Button href="/dashboard">Try Now</Button>
              <Button href="#demo" variant="secondary">
                View Demo
              </Button>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
