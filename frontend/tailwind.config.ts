import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: { card: "0 12px 30px rgb(15 23 42 / 0.08)" },
      colors: {
        brand: { 500: "#4f46e5", 600: "#4338ca", 700: "#3730a3" },
      },
    },
  },
  plugins: [],
};

export default config;
