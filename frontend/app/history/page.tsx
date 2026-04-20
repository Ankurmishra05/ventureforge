"use client";

import { useEffect, useState } from "react";
import axios from "axios";

import { fetchCurrentUser } from "@/lib/api";

const baseURL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

type HistoryItem = {
  generation_id: number;
  idea: string;
  audience: string;
  provider_used: string;
  created_at: string;
};

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        await fetchCurrentUser();

        const token = localStorage.getItem("ventureforge_auth");

        const res = await axios.get(`${baseURL}/startup-history`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        console.log("History:", res.data);

        setHistory(res.data.items ?? []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-4xl font-bold">Your Startup History</h1>

        {loading && <p>Loading...</p>}

        {!loading && history.length === 0 && <p>No history found.</p>}

        <div className="grid gap-6 md:grid-cols-2">
          {history.map((item) => (
            <div
              key={item.generation_id}
              className="rounded-2xl border border-white/10 bg-white/5 p-6"
            >
              <h2 className="text-2xl font-semibold">{item.idea}</h2>
              <p className="mt-2 text-slate-300">
                Audience: {item.audience}
              </p>
              <p className="mt-2 text-slate-400">
                Provider: {item.provider_used}
              </p>
              <p className="mt-4 text-xs text-slate-500">
                {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}