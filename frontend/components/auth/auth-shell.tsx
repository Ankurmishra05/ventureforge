"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { motion } from "framer-motion";

type AuthShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  footer: ReactNode;
  children: ReactNode;
};

export function AuthShell({
  eyebrow,
  title,
  description,
  footer,
  children
}: AuthShellProps) {
  return (
    <div className="min-h-screen bg-hero-radial px-6 py-10 sm:px-8 lg:px-12">
      <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <motion.section
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="rounded-[2rem] border border-white/10 bg-panel/85 p-8 shadow-glow backdrop-blur-xl sm:p-10"
        >
          <Link
            href="/"
            className="text-sm font-medium uppercase tracking-[0.28em] text-accent transition hover:text-white"
          >
            VentureForge
          </Link>
          <p className="mt-8 text-sm uppercase tracking-[0.28em] text-slate-500">
            {eyebrow}
          </p>
          <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            {title}
          </h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-slate-300">
            {description}
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-5">
              <p className="text-sm text-slate-400">Protected access</p>
              <p className="mt-2 text-sm leading-6 text-white">
                JWT bearer auth secures startup generation and future account-scoped workflows.
              </p>
            </div>
            <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-5">
              <p className="text-sm text-slate-400">Frontend ready</p>
              <p className="mt-2 text-sm leading-6 text-white">
                Tokens are persisted locally and applied automatically to API requests.
              </p>
            </div>
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.08 }}
          className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-glow sm:p-10"
        >
          {children}
          <div className="mt-8 text-sm text-slate-400">{footer}</div>
        </motion.section>
      </div>
    </div>
  );
}
