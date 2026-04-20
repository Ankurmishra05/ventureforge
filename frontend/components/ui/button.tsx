import Link from "next/link";
import { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  href: string;
  variant?: "primary" | "secondary";
};

const variantClassNames = {
  primary:
    "bg-accent text-slate-950 shadow-[0_14px_30px_rgba(97,240,209,0.25)] hover:-translate-y-0.5 hover:bg-[#7bf4db]",
  secondary:
    "border border-white/12 bg-white/5 text-white hover:-translate-y-0.5 hover:border-white/25 hover:bg-white/10"
};

export function Button({
  children,
  href,
  variant = "primary"
}: ButtonProps) {
  return (
    <Link
      href={href}
      className={`inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-semibold transition duration-300 ${variantClassNames[variant]}`}
    >
      {children}
    </Link>
  );
}
