import { Examples } from "@/components/examples";

export const metadata = {
  title: "Examples · Rojak-Lingo",
  description: "Every gold item with each model's output, side by side.",
};

export default function ExamplesPage() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <nav aria-label="Sections" className="mb-8 flex gap-4 text-sm">
        <a href="./" className="text-muted">
          Leaderboard
        </a>
        <a href="./examples/" aria-current="page" className="font-medium text-fg">
          Examples
        </a>
      </nav>
      <header className="mb-10">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Examples</h1>
        <p className="mt-3 max-w-2xl text-muted">
          Every gold item with each model&apos;s answer, side by side. Scores are per-item:
          pass or fail for intent and instruct, chrF for normalize and translate.
        </p>
      </header>
      <Examples />
    </main>
  );
}
