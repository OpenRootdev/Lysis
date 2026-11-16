"use client";

import { FormEvent, useEffect, useState } from "react";

import { API, getModel, rank, sendVote, type Issue, type ModelMeta, type RankResponse } from "@/lib/api";

const EXAMPLES = ["psf/requests", "pallets/flask", "expressjs/express"];

function parseRepo(input: string): string {
  return input
    .trim()
    .replace(/^https?:\/\/(www\.)?github\.com\//i, "")
    .replace(/\.git$/i, "")
    .split("/")
    .slice(0, 2)
    .join("/");
}

export default function Home() {
  const [repo, setRepo] = useState("psf/requests");
  const [top, setTop] = useState(10);
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RankResponse | null>(null);
  const [meta, setMeta] = useState<ModelMeta | null>(null);
  const [votes, setVotes] = useState<Record<string, "up" | "down">>({});

  useEffect(() => {
    getModel()
      .then(setMeta)
      .catch(() => setMeta(null));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const name = parseRepo(repo);
    if (!/^[\w.-]+\/[\w.-]+$/.test(name)) {
      setError("Enter a repository as owner/name, for example psf/requests.");
      return;
    }
    setRepo(name);
    setLoading(true);
    setSlow(false);
    setError(null);
    const timer = setTimeout(() => setSlow(true), 4000);
    try {
      setData(await rank(name, top));
      setVotes({});
    } catch (err) {
      setData(null);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      clearTimeout(timer);
      setLoading(false);
    }
  }

  async function vote(issue: Issue, up: boolean) {
    if (!data) return;
    const key = `${data.repo}#${issue.number}`;
    setVotes((v) => ({ ...v, [key]: up ? "up" : "down" }));
    try {
      await sendVote({
        repo: data.repo,
        issue_number: issue.number,
        score: issue.score,
        helpful: up,
        model_date: data.model_date,
      });
    } catch {
      setVotes((v) => {
        const next = { ...v };
        delete next[key];
        return next;
      });
      setError("Could not save your vote. Try again.");
    }
  }

  const max = data ? Math.max(...data.issues.map((i) => i.score), 0.0001) : 1;

  return (
    <main className="mx-auto max-w-3xl px-5 pb-24 pt-16">
      <header>
        <div className="flex items-center gap-2 font-mono text-sm text-emerald-400">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
          lysis
          <span className="text-zinc-600">/</span>
          <span className="text-zinc-500">v0.1</span>
        </div>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight text-zinc-50 sm:text-5xl">
          Find the issues a beginner can actually finish.
        </h1>
        <p className="mt-4 max-w-xl text-zinc-400">
          Lysis ranks a repository&apos;s open issues by how likely a first-time contributor is to
          get a PR merged, learned from thousands of real outcomes instead of labels.
        </p>
      </header>

      <form onSubmit={onSubmit} className="mt-10 flex flex-col gap-3 sm:flex-row">
        <div className="flex flex-1 items-center rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 focus-within:border-emerald-500/60">
          <span className="font-mono text-sm text-zinc-500">github.com/</span>
          <input
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            spellCheck={false}
            autoCapitalize="off"
            placeholder="owner/repo"
            aria-label="Repository"
            className="w-full bg-transparent px-1 py-3 font-mono text-sm text-zinc-100 outline-none placeholder:text-zinc-600"
          />
        </div>
        <select
          value={top}
          onChange={(e) => setTop(Number(e.target.value))}
          aria-label="Number of issues"
          className="rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-3 font-mono text-sm text-zinc-300 outline-none"
        >
          {[5, 10, 20, 30].map((n) => (
            <option key={n} value={n}>
              top {n}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-500 px-5 py-3 text-sm font-medium text-zinc-950 transition hover:bg-emerald-400 disabled:opacity-60"
        >
          {loading ? "Ranking..." : "Rank issues"}
        </button>
      </form>

      <div className="mt-3 flex flex-wrap items-center gap-2 font-mono text-xs text-zinc-500">
        try
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => setRepo(ex)}
            className="rounded border border-zinc-800 px-2 py-0.5 hover:border-zinc-600 hover:text-zinc-300"
          >
            {ex}
          </button>
        ))}
      </div>

      {loading && (
        <p className="mt-8 font-mono text-sm text-zinc-500">
          {slow
            ? "Waking the API, the first request can take up to a minute..."
            : "Fetching issues and ranking..."}
        </p>
      )}

      {error && (
        <p
          role="alert"
          className="mt-8 rounded-lg border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-300"
        >
          {error}
        </p>
      )}

      {data && !loading && (
        <section className="mt-10">
          {data.issues.length === 0 ? (
            <p className="text-zinc-400">No open, unassigned issues found for {data.repo}.</p>
          ) : (
            <>
              <div className="flex items-baseline justify-between font-mono text-xs text-zinc-500">
                <span>
                  {data.issues.length} issues · {data.repo}
                </span>
                <span>higher score = better fit</span>
              </div>
              <ol className="mt-3 divide-y divide-zinc-800/80 rounded-xl border border-zinc-800 bg-zinc-900/30">
                {data.issues.map((issue, idx) => {
                  const chosen = votes[`${data.repo}#${issue.number}`];
                  return (
                    <li key={issue.number} className="p-4 sm:p-5">
                      <div className="flex items-start gap-4">
                        <span className="w-6 pt-0.5 font-mono text-sm text-zinc-600">
                          {String(idx + 1).padStart(2, "0")}
                        </span>
                        <div className="min-w-0 flex-1">
                          <a
                            href={issue.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium text-zinc-100 hover:text-emerald-400"
                          >
                            {issue.full_title}
                          </a>
                          <div className="mt-1 font-mono text-xs text-zinc-500">#{issue.number}</div>
                          <div className="mt-3 flex items-center gap-3">
                            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                              <div
                                className="h-full rounded-full bg-emerald-500"
                                style={{ width: `${(issue.score / max) * 100}%` }}
                              />
                            </div>
                            <span className="w-12 text-right font-mono text-xs text-emerald-400">
                              {issue.score.toFixed(3)}
                            </span>
                          </div>
                          {issue.why && (
                            <p className="mt-3 text-sm leading-relaxed text-zinc-400">{issue.why}</p>
                          )}
                          <div className="mt-3 flex items-center gap-2 text-xs text-zinc-500">
                            <span>Good starter issue?</span>
                            {(["up", "down"] as const).map((v) => (
                              <button
                                key={v}
                                type="button"
                                disabled={Boolean(chosen)}
                                onClick={() => vote(issue, v === "up")}
                                aria-label={v === "up" ? "Yes" : "No"}
                                className={`rounded border px-2 py-0.5 transition ${
                                  chosen === v
                                    ? "border-emerald-500 text-emerald-400"
                                    : "border-zinc-800 hover:border-zinc-600 disabled:opacity-40"
                                }`}
                              >
                                {v === "up" ? "👍" : "👎"}
                              </button>
                            ))}
                            {chosen && <span className="text-zinc-600">thanks</span>}
                          </div>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ol>
            </>
          )}
        </section>
      )}

      <footer className="mt-16 border-t border-zinc-800 pt-6 font-mono text-xs text-zinc-600">
        {meta
          ? `model ${meta.trained_at.slice(0, 10)} · ${meta.n_train.toLocaleString()} issues · CV AP ${meta.cv.ap} · AUC ${meta.cv.auc}`
          : "model info unavailable"}
        <div className="mt-2 flex gap-4">
          <a
            href="https://github.com/OpenRootdev/Lysis"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-zinc-400"
          >
            source
          </a>
          <a
            href={`${API}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-zinc-400"
          >
            api docs
          </a>
        </div>
      </footer>
    </main>
  );
}