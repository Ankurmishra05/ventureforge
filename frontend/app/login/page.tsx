import type { Metadata } from "next";

import { AuthForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export const metadata: Metadata = {
  title: "Login | VentureForge",
  description: "Sign in to VentureForge to generate protected startup briefs."
};

export default function LoginPage() {
  return (
    <AuthShell
      eyebrow="Login"
      title="Sign in to your founder workspace"
      description="Access protected startup generation, account-linked results, and the full VentureForge dashboard."
      footer={<>Bearer tokens are stored in local storage for client-side API access.</>}
    >
      <AuthForm mode="login" />
    </AuthShell>
  );
}
