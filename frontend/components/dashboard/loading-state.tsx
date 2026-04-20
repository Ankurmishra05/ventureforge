"use client";

import { motion } from "framer-motion";

const messages = [
  "Scanning market demand",
  "Refining premium branding",
  "Projecting revenue potential"
];

export function LoadingState() {
  return (
    <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-8 shadow-glow">
      <div className="flex items-center gap-4">
        <div className="relative flex h-14 w-14 items-center justify-center">
          <motion.span
            className="absolute h-14 w-14 rounded-full border border-accent/35"
            animate={{ scale: [1, 1.3, 1], opacity: [0.7, 0.15, 0.7] }}
            transition={{ repeat: Number.POSITIVE_INFINITY, duration: 2.2, ease: "easeInOut" }}
          />
          <motion.span
            className="h-4 w-4 rounded-full bg-accent"
            animate={{ scale: [1, 1.4, 1] }}
            transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.2, ease: "easeInOut" }}
          />
        </div>
        <div>
          <h3 className="font-display text-xl font-semibold text-white">
            Generating your venture brief
          </h3>
          <p className="mt-1 text-sm text-slate-400">
            This can take a moment while the API coordinates research, branding, and finance.
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-3">
        {messages.map((message, index) => (
          <motion.div
            key={message}
            initial={{ opacity: 0.3, x: -10 }}
            animate={{ opacity: [0.35, 1, 0.35], x: [0, 10, 0] }}
            transition={{
              repeat: Number.POSITIVE_INFINITY,
              duration: 2.4,
              ease: "easeInOut",
              delay: index * 0.25
            }}
            className="rounded-2xl border border-white/8 bg-slate-950/60 px-4 py-3 text-sm text-slate-300"
          >
            {message}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
