"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge, Card } from "@/components/ui/card";
import { MODEL_ORDER, TASKS, modelStyle } from "@/lib/config";
import type { Digest, DigestItem } from "@/lib/types";
import { cn } from "@/lib/utils";

type State =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ready"; data: Digest };

const BINARY_TASKS = new Set(["intent", "instruct"]);

function rank(item: DigestItem): number {
  const scores = Object.values(item.outputs).map((o) => o.score);
  if (scores.length === 0) return 0;
  if (BINARY_TASKS.has(item.task)) {
    return scores.filter((s) => s < 1).length; // more failures first
  }
  return scores.reduce((a, b) => a + b, 0) / scores.length; // lower chrF first
}

function ScoreBadge({ task, score }: { task: string; score: number }) {
  if (BINARY_TASKS.has(task)) {
    const pass = score >= 1;
    return (
      <span className={cn("font-mono text-sm font-semibold tabular-nums", pass ? "text-fg" : "text-ft")}>
        {pass ? "PASS" : "FAIL"}
      </span>
    );
  }
  return <span className="font-mono text-sm tabular-nums">{(score * 100).toFixed(1)}</span>;
}

function ItemCard({ item }: { item: DigestItem }) {
  const models = [
    ...MODEL_ORDER.filter((m) => m in item.outputs),
    ...Object.keys(item.outputs).filter((m) => !MODEL_ORDER.includes(m)).sort(),
  ];
  return (
    <Card>
      <p className="font-medium">{item.prompt}</p>
      <p className="mt-1 text-sm text-muted">
        <span className="font-mono text-xs">{item.id}</span> · Reference: {item.reference}
      </p>
      <div className="mt-3 space-y-2 border-t border-line pt-3">
        {models.map((m) => {
          const o = item.outputs[m];
          return (
            <div key={m} className="flex items-start justify-between gap-3 text-sm">
              <p>
                <span className={cn("mr-1.5 inline-block h-2 w-2 rounded-full", modelStyle(m).color)} aria-hidden />
                <span className="text-muted">{modelStyle(m).label}: </span>
                {o.output || <span className="text-muted">no output</span>}
              </p>
              <ScoreBadge task={item.task} score={o.score} />
            </div>
          );
        })}
      </div>
    </Card>
  );
}

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export function Examples() {
  const [state, setState] = useState<State>({ status: "loading" });
  const [tab, setTab] = useState<string>(TASKS[0].key);
  useEffect(() => {
    if (new URLSearchParams(window.location.search).has("sample")) {
      setState({ status: "error" });
      return;
    }
    fetch(`${BASE}/examples.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<Digest>;
      })
      .then((data) => {
        setState({ status: "ready", data });
        if (!data.items.some((i) => i.task === tab)) {
          setTab(data.items[0]?.task ?? tab);
        }
      })
      .catch(() => setState({ status: "error" }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const items = useMemo(() => {
    if (state.status !== "ready") return [];
    return state.data.items
      .filter((i) => i.task === tab)
      .sort((a, b) => rank(b) - rank(a) || (a.id < b.id ? -1 : 1));
  }, [state, tab]);
  const tasks =
    state.status === "ready"
      ? TASKS.filter((t) => state.data.items.some((i) => i.task === t.key))
      : [];

  if (state.status === "loading") {
    return <p className="text-muted">Loading examples…</p>;
  }
  if (state.status === "error") {
    return (
      <div role="status" className="rounded-lg border border-line bg-card px-4 py-3 text-sm text-muted">
        No per-item examples here. Run <code className="font-mono">make web-data</code> then rebuild,
        or open this page without <code className="font-mono">?sample</code> — the preview covers the
        leaderboard layout only.
      </div>
    );
  }

  return (
    <div>
      <div role="tablist" aria-label="Tasks" className="mb-6 flex flex-wrap gap-2">
        {tasks.map((t) => {
          const n =
            state.status === "ready"
              ? state.data.items.filter((i) => i.task === t.key).length
              : 0;
          const active = t.key === tab;
          return (
            <button
              key={t.key}
              role="tab"
              aria-selected={active}
              onClick={() => setTab(t.key)}
              className={cn(
                "rounded-full border border-line px-3 py-1 text-sm",
                active ? "bg-fg font-medium text-bg" : "text-muted",
              )}
            >
              {t.title} · {n}
            </button>
          );
        })}
      </div>
      <p className="mb-4 text-sm text-muted">
        Worst first: most failed models for intent and instruct, lowest average chrF otherwise.
      </p>
      <div className="space-y-4">
        {items.map((item) => (
          <ItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
