"use client";

import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";

const stats = [
  { label: "Ideas validated", value: "12k+" },
  { label: "Go-to-market plans", value: "3.8x" },
  { label: "Time to first brief", value: "8 min" }
];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-6 pb-24 pt-8 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-6">
          <div className="font-display text-lg font-semibold tracking-[0.18em] text-white/90">
            VentureForge
          </div>
          <nav className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
            <a href="#features" className="transition hover:text-white">
              Features
            </a>
            <a href="#how-it-works" className="transition hover:text-white">
              How it works
            </a>
            <a href="#testimonials" className="transition hover:text-white">
              Testimonials
            </a>
            <a href="/login" className="transition hover:text-white">
              Login
            </a>
          </nav>
        </div>

        <div className="grid gap-16 pt-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <motion.span
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-sm font-medium text-accent"
            >
              Founder operating system
            </motion.span>

            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.1 }}
              className="mt-8 max-w-3xl font-display text-5xl font-semibold leading-[1.02] tracking-tight text-white sm:text-6xl lg:text-7xl"
            >
              Build startups at the speed of thought
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.2 }}
              className="mt-6 max-w-2xl text-lg leading-8 text-slate-300"
            >
              VentureForge turns raw ideas into research, positioning, launch plans,
              and investor-ready narratives from a single premium workflow.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.3 }}
              className="mt-10 flex flex-col gap-4 sm:flex-row"
            >
              <Button href="/dashboard">Try Now</Button>
              <Button href="#demo" variant="secondary">
                View Demo
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.4 }}
              className="mt-14 grid gap-4 sm:grid-cols-3"
            >
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur"
                >
                  <div className="text-2xl font-semibold text-white">{stat.value}</div>
                  <div className="mt-1 text-sm text-slate-400">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 24 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.85, delay: 0.15 }}
            className="relative"
          >
            <div className="absolute -inset-6 rounded-[2rem] bg-gradient-to-br from-highlight/25 via-accent/10 to-transparent blur-3xl" />
            <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-panel/80 p-6 shadow-glow backdrop-blur-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div>
                  <p className="text-sm text-slate-400">Workspace</p>
                  <p className="mt-1 text-lg font-semibold text-white">
                    Venture pipeline
                  </p>
                </div>
                <div className="rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
                  Live
                </div>
              </div>

              <div className="mt-6 space-y-4">
                {[
                  "Market map generated from 38 signals",
                  "Positioning refined for B2B founder audience",
                  "Launch sequence drafted with acquisition channels"
                ].map((item, index) => (
                  <div
                    key={item}
                    className="rounded-2xl border border-white/8 bg-white/[0.03] p-4"
                  >
                    <div className="flex items-start gap-4">
                      <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-sm text-white">
                        0{index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-white">{item}</p>
                        <p className="mt-1 text-sm leading-6 text-slate-400">
                          Collaborate with AI agents across research, branding,
                          pricing, and fundraising in one focused loop.
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div id="demo" className="mt-6 rounded-2xl border border-white/8 bg-slate-950/70 p-5">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Confidence score</span>
                  <span className="font-semibold text-accent">94%</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-white/10">
                  <div className="h-2 w-[94%] rounded-full bg-gradient-to-r from-accent to-highlight" />
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-400">
                  Your next venture brief is ready for product, growth, and investor review.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
