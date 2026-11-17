"use client";

import { useEffect, useState } from "react";

import { getRepos, getReposMeta, type RepoItem, type ReposMeta } from "@/lib/api";

const LEVELS = [
  { id: "beginner", label: "Beginner", hint: "small codebases, easy to get oriented in" },
  { id: "intermediate", label: "Intermediate", hint: "mid-size projects" },
  { id: "advanced", label: "Advanced", hint: "large, complex repositories" },
] as const;

type Level = (typeof LEVELS)[number]["id"];

const NAMES: Record<string, string> = {
  javascript: "JavaScript",
  typescript: "TypeScript",
  python: "Python",
};
const label = (l: string) => NAMES[l] ?? l.charAt(0).toUpperCase() + l.slice(1);

type Result = { key: string; repos: RepoItem[]; total: number };

export default function RepoFinder({ onPick }: { onPick: (repo: string) => void }) {
  const [meta, setMeta] = useState<ReposMeta | null>(null);
  const [metaFailed, setMetaFailed] = useState(false);
  const [language, setLanguage] = useState("");
  const [level, setLevel] = useState<Level>("beginner");
  const [result, setResult] = useState<Result | null>(null);
  const [failedKey, setFailedKey] = useState<string | null>(null);

  useEffect(() => {
    getReposMeta()
      .then((m) => {
        setMeta(m);
        const p = new URLSearchParams(window.location.search);
        const l = p.get("language");
        const lv = p.get("level");
        setLanguage(
          l && m.languages.includes(l)
            ? l
            : m.languages.includes("python")
              ? "python"
              : (m.languages[0] ?? ""),
        );
        if (lv && LEVELS.some((x) => x.id === lv)) setLevel(lv as Level);
      })
      .catch(() => setMetaFailed(true));
  }, []);

  const key = meta && language ? `${language}|${level}` : "";

  useEffect(() => {
    if (!key) return;
    let cancelled = false;
    getRepos(language, level)
      .then((r) => {
        if (!cancelled) setResult({ key, repos: r.repos, total: r.total });
      })
      .catch(() => {
        if (!cancelled) setFailedKey(key);
      });
    return () => {
      cancelled = true;
    };
  }, [key, language, level]);

  useEffect(() => {
    if (key) window.history.replaceState(null, "", `?language=${language}&level=${level}`);
  }, [key, language, level]);

  const shown = result?.key === key ? result : null;
  const loading = Boolean(key) && !shown && failedKey !== key;
  const failed = metaFailed || (Boolean(key) && failedKey === key);
  const max = shown ? Math.max(...shown.repos.map((r) => r.score), 0.0001) : 1;
  const hint = LEVELS.find((l) => l.id === level)?.hint;

  return (
    <section className="mt-10">
      <h2 className="font-mono text-sm text-emerald-400">find a repository</h2>
      <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Language"
          disabled={!meta}
          className="rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-3 font-mono text-sm text-zinc-300 outline-none disabled:opacity-50"
        >
          {(meta?.languages ?? []).map((l) => (
            <option key={l} value={l}>
              {label(l)}
            </option>
          ))}
        </select>
        <div
          role="group"
          aria-label="Experience level"
          className="flex overflow-hidden rounded-lg border border-zinc-800"
        >
          {LEVELS.map((l) => (
            <button
              key={l.id}
              type="button"
              aria-pressed={level === l.id}
              onClick={() => setLevel(l.id)}
              className={`px-4 py-3 text-sm transition ${
                level === l.id
                  ? "bg-emerald-500 text-zinc-950"
                  : "bg-zinc-900/60 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>
      <p className="mt-2 font-mono text-xs text-zinc-600">
        {hint}. Level is based on repository size; only actively maintained repos are shown.
      </p>

      {failed && (
        <p
          role="alert"
          className="mt-4 rounded-lg border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-300"
        >
          The repository finder is unavailable right now. You can still rank any repository below.
        </p>
      )}
      {loading && <p className="mt-4 font-mono text-sm text-zinc-500">Finding repositories...</p>}

      {shown &&
        (shown.repos.length === 0 ? (
          <p className="mt-4 text-sm text-zinc-400">No active repositories match yet.</p>
        ) : (
          <>
            <ol className="mt-4 divide-y divide-zinc-800/80 rounded-xl border border-zinc-800 bg-zinc-900/30">
              {shown.repos.map((r, idx) => (
                <li key={r.repo} className="p-4 sm:p-5">
                  <div className="flex items-start gap-4">
                    <span className="w-6 pt-0.5 font-mono text-sm text-zinc-600">
                      {String(idx + 1).padStart(2, "0")}
                    </span>
                    <div className="min-w-0 flex-1">
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-zinc-100 hover:text-emerald-400"
                      >
                        {r.repo}
                      </a>
                      <p className="mt-1 line-clamp-2 text-sm text-zinc-400">
                        {r.description || "No description."}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-xs text-zinc-500">
                        <span>★ {r.stars.toLocaleString()}</span>
                        <span>{r.prs_90d} PRs merged / 90d</span>
                        <span>{r.open_issues} open issues</span>
                        {r.good_first_issues > 0 && (
                          <span>{r.good_first_issues} labeled good first issue</span>
                        )}
                      </div>
                      <div className="mt-3 flex items-center gap-3">
                        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                          <div
                            className="h-full rounded-full bg-emerald-500"
                            style={{ width: `${(r.score / max) * 100}%` }}
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => onPick(r.repo)}
                          className="rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:border-emerald-500 hover:text-emerald-400"
                        >
                          Rank its issues →
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
            <p className="mt-2 font-mono text-xs text-zinc-600">
              Bars show fit relative to this list, not a probability. Or rank any repository below.
            </p>
          </>
        ))}
    </section>
  );
}