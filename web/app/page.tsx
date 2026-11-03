import { Leaderboard } from "@/components/leaderboard";

export default function Page() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-16">
      <nav aria-label="Sections" className="mb-8 flex gap-4 text-sm">
        <a href="./" aria-current="page" className="font-medium text-fg">
          Leaderboard
        </a>
        <a href="./examples/" className="text-muted">
          Examples
        </a>
      </nav>
      <header className="mb-10">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Rojak-Lingo</h1>
        <p className="mt-3 max-w-2xl text-lg text-muted">
          A benchmark for Malaysian code-switching across English, Bahasa Malaysia, Mandarin, Cantonese and Manglish,
          and a small fine-tune trained to close the gap.
        </p>
      </header>
      <Leaderboard />
      <footer className="mt-16 border-t border-line pt-6 text-sm text-muted">
        <p>
          Gold items are hand-written and held out from training. Instruct is scored by programmatic checks, intent by
          label match, normalize and translate by chrF against one reference. With a small gold set, treat gaps of a
          few points as noise.
        </p>
        <p className="mt-3">Built for the Meta Global AI Developer Hackathon.</p>
      </footer>
    </main>
  );
}
