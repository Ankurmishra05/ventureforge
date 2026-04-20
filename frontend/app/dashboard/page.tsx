import type { Metadata } from "next";

import { DashboardShell } from "@/components/dashboard/dashboard-shell";

export const metadata: Metadata = {
  title: "VentureForge Dashboard",
  description: "Generate startup research, branding, and finance plans from the VentureForge API."
};

export default function DashboardPage() {
  return <DashboardShell />;
}
