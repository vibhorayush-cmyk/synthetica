import type { Metadata } from "next";
import { QueryProvider } from "@/components/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Synthetica — Synthetic Data for Analytics Practice",
  description: "Generate realistic retail and banking datasets for Power BI, SQL, Tableau, Excel, Python, and machine-learning practice.",
  manifest: "/manifest.webmanifest",
  icons: { icon: "/favicon.svg" },
  openGraph: { title: "Synthetica — Synthetic Data for Analytics Practice", description: "Realistic data. Real analytical practice.", type: "website" },
  twitter: { card: "summary", title: "Synthetica", description: "Realistic data. Real analytical practice." },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body><QueryProvider>{children}</QueryProvider></body>
    </html>
  );
}
