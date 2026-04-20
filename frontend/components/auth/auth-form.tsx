"use client";

import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import {
  login,
  persistAuthSession,
  register
} from "@/lib/api";

type AuthMode = "login" | "signup";

type AuthFormProps = {
  mode: AuthMode;
};

const config = {
  login: {
    submitLabel: "Sign in",
    altLabel: "Need an account?",
    altHref: "/signup",
    altAction: "Create one"
  },
  signup: {
    submitLabel: "Create account",
    altLabel: "Already registered?",
    altHref: "/login",
    altAction: "Sign in"
  }
};

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: ""
  });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const payload =
        mode === "login"
          ? await login({
              email: form.email.trim(),
              password: form.password
            })
          : await register({
              email: form.email.trim(),
              full_name: form.fullName.trim(),
              password: form.password
            });

      persistAuthSession(payload);
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === "string" ? detail : "Authentication failed.");
      } else {
        setError("Authentication failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const modeConfig = config[mode];

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {mode === "signup" ? (
        <div>
          <label htmlFor="fullName" className="text-sm font-medium text-slate-200">
            Full name
          </label>
          <input
            id="fullName"
            type="text"
            value={form.fullName}
            onChange={(event) =>
              setForm((current) => ({ ...current, fullName: event.target.value }))
            }
            className="mt-2 w-full rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-accent/50"
            placeholder="Ada Lovelace"
            minLength={2}
            required
          />
        </div>
      ) : null}

      <div>
        <label htmlFor="email" className="text-sm font-medium text-slate-200">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={form.email}
          onChange={(event) =>
            setForm((current) => ({ ...current, email: event.target.value }))
          }
          className="mt-2 w-full rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-accent/50"
          placeholder="founder@ventureforge.ai"
          required
        />
      </div>

      <div>
        <label htmlFor="password" className="text-sm font-medium text-slate-200">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={form.password}
          onChange={(event) =>
            setForm((current) => ({ ...current, password: event.target.value }))
          }
          className="mt-2 w-full rounded-full border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-accent/50"
          placeholder="Minimum 8 characters"
          minLength={8}
          required
        />
      </div>

      {error ? (
        <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex w-full items-center justify-center rounded-full bg-accent px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-[#7bf4db] disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? "Please wait..." : modeConfig.submitLabel}
      </button>

      <p className="text-sm text-slate-400">
        {modeConfig.altLabel}{" "}
        <Link href={modeConfig.altHref} className="text-accent transition hover:text-white">
          {modeConfig.altAction}
        </Link>
      </p>
    </form>
  );
}
