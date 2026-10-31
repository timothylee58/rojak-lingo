import { TASKS, loadLeaderboard } from "./leaderboard";

export default function Page() {
  const board = loadLeaderboard();
  const models = board ? Object.values(board.models) : [];

  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-3xl font-semibold">Rojak-Lingo</h1>
      <p className="mt-2 text-neutral-600">
        Malaysian code-switching benchmark. Same prompts, same metrics, every model.
      </p>

      {models.length === 0 ? (
        <p className="mt-8 rounded border border-dashed p-6 text-neutral-500">
          No results yet. Run <code>make eval &amp;&amp; make report</code>.
        </p>
      ) : (
        <div className="mt-8 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b text-neutral-500">
              <tr>
                <th className="py-2 pr-4">Model</th>
                {TASKS.map((t) => (
                  <th key={t.task} className="py-2 pr-4">{t.label}</th>
                ))}
                <th className="py-2">Items</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.model} className="border-b last:border-0">
                  <td className="py-2 pr-4 font-medium">{m.model}</td>
                  {TASKS.map((t) => {
                    const v = m.metrics[t.task]?.[t.metric];
                    return (
                      <td key={t.task} className="py-2 pr-4 tabular-nums">
                        {v === undefined ? "–" : v.toFixed(3)}
                      </td>
                    );
                  })}
                  <td className="py-2 tabular-nums">
                    {m.n_items}
                    {m.n_draft_items > 0 && (
                      <span className="ml-1 text-amber-600">({m.n_draft_items} draft)</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-4 text-xs text-neutral-500">Generated {board!.generated}</p>
        </div>
      )}
    </main>
  );
}
