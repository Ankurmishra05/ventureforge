import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#050816",
        panel: "#0b1120",
        accent: "#61f0d1",
        highlight: "#7c8cff",
        muted: "#8a94ad"
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.05), 0 24px 80px rgba(10,14,35,0.65)"
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(circle at top, rgba(124, 140, 255, 0.2), transparent 32%), radial-gradient(circle at 20% 20%, rgba(97, 240, 209, 0.12), transparent 25%)"
      }
    }
  },
  plugins: []
};

export default config;
