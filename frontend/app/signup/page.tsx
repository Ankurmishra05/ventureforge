import type { Metadata } from "next";

import { AuthForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export const metadata: Metadata = {
  title: "Signup | VentureForge",
  description: "Create a VentureForge account and start generating protected startup briefs."
};

export default function SignupPage() {
  return (
    <AuthShell
      eyebrow="Signup"
      title="Create your VentureForge account"
      description="Register with email and password to unlock authenticated startup generation and future saved workflows."
      footer={<>Registration returns a JWT immediately so the frontend can continue without a second login step.</>}
    >
      <AuthForm mode="signup" />
    </AuthShell>
  );
}
