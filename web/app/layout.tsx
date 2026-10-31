import "./globals.css";

export const metadata = {
  title: "Rojak-Lingo Leaderboard",
  description: "Malaysian code-switching benchmark: base vs fine-tune vs Muse Spark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-neutral-50 text-neutral-900 antialiased">{children}</body>
    </html>
  );
}
