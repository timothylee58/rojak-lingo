import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rojak-Lingo Leaderboard",
  description: "How well do language models handle Malaysian code-switching?",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
