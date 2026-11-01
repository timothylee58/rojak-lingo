"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Badge, Card } from "@/components/ui/card";
import { MODEL_ORDER, MODELS, TASKS } from "@/lib/config";
import type { Leaderboard as Data, ModelSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

type Task = (typeof TASKS)[number];
type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: Data };

function useLeaderboard(): State {
  const [state, setState] = useState<State>({ status: "loading" });
  useEffect(() => {
    const sample = new URLSearchParams(window.location.search).has("sample");
    fetch(sample ? "/leaderboard.sample.json" : "/leaderboard.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<Data>;
      })
      .then((data) => setState({ status: "ready", data }))
      .catch((e: Error) => setState({ status: "error", message: e.message }));
  }, []);
  return state;
}

const pct = (v: number) => (v * 100).toFixed(1);

function scoreOf(model: ModelSummary | undefined, task: Task): number | undefined {
  return model?.metrics[task.key]?.[task.metric];
}

function Bar({ value, color, label, name }: { value: number; color: string; label: string; name: string }) {
  const reduce = useReducedMotion();
  const width = `${Math.max(0, Math.min(1, value)) * 100}%`;
  return (
    <div>
      <p className="mb-1 text-xs text-muted">{name}</p>
      <div className="flex items-center gap-3">
        <div className="h-3 flex-1 overflow-hidden rounded-full bg-line" role="img" aria-label={`${label}: ${pct(value)}`}>
          <motion.div
            className={cn("h-full rounded-full", color)}
            initial={{ width: reduce ? width : 0 }}
            animate={{ width }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          />
        </div>
        <span className="w-12 text-right font-mono text-sm tabular-nums">{pct(value)}</span>
      </div>
    </div>
  );
}

function Banner({ children, tone }: { children: React.ReactNode; tone: "warn" | "info" }) {
  return (
    <div
      role="status"
      className={cn(
        "mb-4 rounded-lg border px-4 py-3 text-sm",
        tone === "warn"
          ? "border-amber-500/50 bg-amber-500/10 text-fg"
          : "border-line bg-card text-muted",
      )}
    >
      {children}
    </div>
  );
}

function Delta({ task, models }: { task: Task; models: Record<string, ModelSummary> }) {
  const base = scoreOf(models["base"], task);
  const ft = scoreOf(models["rojak-ft"], task);
  const delta = base !== undefined && ft !== undefined ? (ft - base) * 100 : undefined;
  return (
    <Card>
      <p className="text-sm text-muted">{task.title}</p>
      <p
        className={cn(
          "mt-1 font-mono text-3xl font-semibold tabular-nums",
          delta === undefined ? "text-muted" : delta >= 0 ? "text-ft" : "text-fg",
        )}
      >
        {delta === undefined ? "—" : `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}`}
      </p>
      <p className="mt-1 text-xs text-muted">points vs base · {task.metricLabel}</p>
    </Card>
  );
}

export function Leaderboard() {
  const state = useLeaderboard();

  if (state.status === "loading") {
    return <p className="text-muted">Loading results…</p>;
  }
  if (state.status === "error") {
    return (
      <Banner tone="info">
        No results found ({state.message}). Run <code className="font-mono">make eval && make report</code> then{" "}
        <code className="font-mono">make web-data</code>, or open this page with <code className="font-mono">?sample</code> to
        preview the layout.
      </Banner>
    );
  }

  const { data } = state;
  const models = data.models;
  const present = MODEL_ORDER.filter((m) => models[m]);
  const drafts = Math.max(0, ...Object.values(models).map((m) => m.n_draft_items));

  return (
    <div>
      {data.sample && (
        <Banner tone="warn">
          <strong>Sample data.</strong> These numbers are placeholders to preview the layout, not real results.
        </Banner>
      )}
      {drafts > 0 && !data.sample && (
        <Banner tone="warn">
          {drafts} gold items are still unverified drafts. Verify them before quoting these numbers.
        </Banner>
      )}

      <section aria-labelledby="delta-h" className="mb-12">
        <h2 id="delta-h" className="mb-4 text-xl font-semibold">
          Does fine-tuning help?
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {TASKS.map((t) => (
            <Delta key={t.key} task={t} models={models} />
          ))}
        </div>
      </section>

      <section aria-labelledby="tasks-h" className="mb-12">
        <h2 id="tasks-h" className="mb-4 text-xl font-semibold">
          Scores by task
        </h2>
        <div className="mb-4 flex flex-wrap gap-2">
          {present.map((m) => (
            <Badge key={m}>
              <span className={cn("mr-1.5 inline-block h-2 w-2 rounded-full", MODELS[m].color)} aria-hidden />
              {MODELS[m].label}
            </Badge>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {TASKS.map((task) => (
            <Card key={task.key}>
              <div className="mb-4 flex items-baseline justify-between gap-2">
                <h3 className="font-semibold">{task.title}</h3>
                <span className="font-mono text-xs text-muted">
                  {task.metricLabel} · n={models[present[0]]?.metrics[task.key]?.n ?? "?"}
                </span>
              </div>
              <p className="mb-4 text-sm text-muted">{task.blurb}</p>
              <div className="space-y-3">
                {present.map((m) => {
                  const v = scoreOf(models[m], task);
                  return v === undefined ? null : (
                    <Bar
                      key={m}
                      value={v}
                      color={MODELS[m].color}
                      name={MODELS[m].label}
                      label={`${MODELS[m].label} ${task.title}`}
                    />
                  );
                })}
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section aria-labelledby="table-h">
        <h2 id="table-h" className="mb-4 text-xl font-semibold">
          All numbers
        </h2>
        <div className="overflow-x-auto rounded-xl border border-line bg-card">
          <table className="w-full min-w-[32rem] text-left text-sm">
            <thead className="text-muted">
              <tr className="border-b border-line">
                <th scope="col" className="px-4 py-3 font-medium">Model</th>
                {TASKS.map((t) => (
                  <th key={t.key} scope="col" className="px-4 py-3 text-right font-medium">
                    {t.title} <span className="font-normal">({t.metricLabel})</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {present.map((m) => (
                <tr key={m} className="border-b border-line last:border-0">
                  <th scope="row" className="px-4 py-3 font-medium">{MODELS[m].label}</th>
                  {TASKS.map((t) => {
                    const v = scoreOf(models[m], t);
                    return (
                      <td key={t.key} className="px-4 py-3 text-right font-mono tabular-nums">
                        {v === undefined ? "—" : pct(v)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
