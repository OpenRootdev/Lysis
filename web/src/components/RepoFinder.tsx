
"use client";

import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";

import {
  getRepos,
  getReposMeta,
  parseRepo,
  type RepoItem,
  type ReposMeta,
} from "@/lib/api";

const LEVELS = [
  { id: "beginner", label: "Beginner", color: "bg-emerald-500" },
  { id: "intermediate", label: "Intermediate", color: "bg-amber-400" },
  { id: "advanced", label: "Advanced", color: "bg-rose-500" },
] as const;

type Level = (typeof LEVELS)[number]["id"];

const NAMES: Record<string, string> = {
  javascript: "JavaScript",
  typescript: "TypeScript",
  python: "Python",
};

const label = (l: string) =>
  NAMES[l] ?? l.charAt(0).toUpperCase() + l.slice(1);

const REPO_RE = /^[\w.-]+\/[\w.-]+$/;

type Result = { key: string; repos: RepoItem[] };

export default function RepoFinder({
  onPick,
  onClear,
  children,
}: {
  onPick: (repo: string) => void;
  onClear: () => void;
  children?: ReactNode;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [meta, setMeta] = useState<ReposMeta | null>(null);
  const [metaFailed, setMetaFailed] = useState(false);
  const [language, setLanguage] = useState("");
  const [level, setLevel] = useState<Level>("beginner");
  const [q, setQ] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [failedKey, setFailedKey] = useState<string | null>(null);
  const [ranked, setRanked] = useState<string | null>(null);

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

        if (lv && LEVELS.some((x) => x.id === lv)) {
          setLevel(lv as Level);
        }
      })
      .catch(() => setMetaFailed(true));
  }, []);

  const key = meta && language ? `${language}|${level}` : "";

  useEffect(() => {
    if (!key) return;

    let cancelled = false;

    getRepos(language, level, 50)
      .then((r) => {
        if (cancelled) return;
        setResult({ key, repos: r.repos });
        setFailedKey(null);
      })
      .catch(() => {
        if (!cancelled) setFailedKey(key);
      });

    return () => {
      cancelled = true;
    };
  }, [key, language, level]);

  useEffect(() => {
    if (key) {
      window.history.replaceState(
        null,
        "",
        `?language=${language}&level=${level}`,
      );
    }
  }, [key, language, level]);

  const idx = LEVELS.findIndex((l) => l.id === level);
  const cur = LEVELS[idx];
  const parsed = parseRepo(q);
  const direct = REPO_RE.test(parsed) ? parsed : null;
  const loading =
    Boolean(key) && result?.key !== key && failedKey !== key;
  const failed = metaFailed || (Boolean(key) && failedKey === key);

  const rows = result ? result.repos.slice(0, 12) : [];
  const browsing = !q.trim();
  const go = Boolean(direct) && direct !== ranked;

  const max = result
    ? Math.max(...result.repos.map((r) => r.score), 0.0001)
    : 1;

  function change(v: string) {
    setQ(v);
    if (!v.trim()) {
      setRanked(null);
      scrollRef.current?.scrollTo({ top: 0 });
      onClear();
    }
  }

  function pick(name: string) {
    setQ(name);
    setRanked(name);
    scrollRef.current?.scrollTo({ top: 0 });
    onPick(name);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (direct) pick(direct);
  }

  return (
    <section className="mt-6 flex min-h-0 flex-1 flex-col sm:mt-8">
      <form
        onSubmit={onSubmit}
        className="flex shrink-0 items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900/60 py-1.5 pl-4 pr-2 transition-colors focus-within:border-emerald-500/60"
      >
        <span className="font-mono text-xs text-zinc-500 max-[380px]:hidden sm:text-sm">
          github.com/
        </span>

        <input
          value={q}
          onChange={(e) => change(e.target.value)}
          onKeyDown={(e) => e.key === "Escape" && change("")}
          spellCheck={false}
          autoCapitalize="off"
          enterKeyHint="go"
          placeholder="owner/repo"
          aria-label="Repository, owner/repo"
          className="min-w-0 flex-1 bg-transparent py-2.5 font-mono text-sm text-zinc-100 outline-none placeholder:text-zinc-600"
        />

        <button
          type={go ? "submit" : "button"}
          onClick={go ? undefined : () => change("")}
          aria-label={go ? "Find issues" : "Clear"}
          tabIndex={q ? 0 : -1}
          className={`relative h-9 w-9 shrink-0 rounded-lg transition-all duration-200 ${
            q ? "opacity-100" : "pointer-events-none opacity-0"
          } ${
            go
              ? "bg-emerald-500 text-zinc-950 hover:bg-emerald-400"
              : "text-zinc-500 hover:text-zinc-200"
          }`}
        >
          <svg
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
            className={`absolute inset-0 m-auto h-4 w-4 transition-all duration-200 ${
              go ? "scale-75 opacity-0" : "opacity-100"
            }`}
          >
            <path d="M5 5l10 10M15 5L5 15" />
          </svg>

          <svg
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            className={`absolute inset-0 m-auto h-4 w-4 transition-all duration-200 ${
              go ? "opacity-100" : "scale-75 opacity-0"
            }`}
          >
            <path d="M4 10h12M11 5l5 5-5 5" />
          </svg>
        </button>
      </form>

      {!browsing && !direct && (
        <p className="fade-up mt-3 shrink-0 font-mono text-xs text-zinc-600">
          Enter a repository as owner/repo, for example psf/requests.
        </p>
      )}

      <div
        inert={!browsing}
        className={`grid shrink-0 transition-all duration-300 ${
          browsing ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 pt-4">
            <div
              role="radiogroup"
              aria-label="Language"
              className="flex flex-wrap items-center gap-2"
            >
              {(meta?.languages ?? []).map((l) => (
                <button
                  key={l}
                  type="button"
                  role="radio"
                  aria-checked={language === l}
                  onClick={() => setLanguage(l)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors duration-200 ${
                    language === l
                      ? "border-emerald-500/70 bg-emerald-500/10 text-emerald-300"
                      : "border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-200"
                  }`}
                >
                  {label(l)}
                </button>
              ))}
            </div>

            <div
              role="radiogroup"
              aria-label="Experience level"
              title="Level reflects repository size and complexity, not your skill"
              className="flex items-center gap-3 sm:ml-auto"
            >
              <div className="flex gap-1">
                {LEVELS.map((l, i) => (
                  <button
                    key={l.id}
                    type="button"
                    role="radio"
                    aria-checked={level === l.id}
                    aria-label={l.label}
                    onClick={() => setLevel(l.id)}
                    className={`h-4 w-9 rounded-sm transition-colors duration-300 first:rounded-l-full last:rounded-r-full ${
                      i <= idx ? l.color : "bg-zinc-800 hover:bg-zinc-700"
                    }`}
                  />
                ))}
              </div>

              <span className="w-24 font-mono text-xs text-zinc-400">
                {cur.label}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="no-scrollbar fade-bottom mt-4 min-h-0 flex-1 overflow-y-auto pb-6"
      >
        {browsing && failed && (
          <p
            role="alert"
            className="rounded-lg border border-red-900/60 bg-red-950/30 px-4 py-3 text-sm text-red-300"
          >
            The repository finder is unavailable right now. You can still enter
            owner/repo above to rank any repository.
          </p>
        )}

        {browsing && result && (
          <div
            className={`transition-opacity duration-200 ${
              loading ? "opacity-40" : "opacity-100"
            }`}
          >
            {rows.length === 0 ? (
              <p className="text-sm text-zinc-500">No repositories match.</p>
            ) : (
              <ol
                key={result.key}
                className="grid gap-3 sm:grid-cols-2"
              >
                {rows.map((r, i) => (
                  <li
                    key={r.repo}
                    className="fade-up flex flex-col rounded-xl border border-zinc-800 bg-zinc-900/30 p-4"
                    style={{ animationDelay: `${Math.min(i, 8) * 30}ms` }}
                  >
                    <a
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-zinc-100 hover:text-emerald-400"
                    >
                      {r.repo}
                    </a>

                    <p className="mt-1 line-clamp-2 text-xs text-zinc-400 sm:text-sm">
                      {r.description || "No description."}
                    </p>

                    <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[11px] text-zinc-500">
                      <span>★ {r.stars.toLocaleString()}</span>
                      <span>{r.prs_90d} PRs merged / 90d</span>
                      <span>{r.open_issues} open issues</span>

                      {r.good_first_issues > 0 && (
                        <span>
                          {r.good_first_issues} labeled good first issue
                        </span>
                      )}
                    </div>

                    <div className="mt-auto flex items-center gap-3 pt-3">
                      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                        <div
                          className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                          style={{ width: `${(r.score / max) * 100}%` }}
                        />
                      </div>

                      <button
                        type="button"
                        onClick={() => pick(r.repo)}
                        className="shrink-0 rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-200 transition-colors hover:border-emerald-500 hover:text-emerald-400"
                      >
                        Find issues →
                      </button>
                    </div>
                  </li>
                ))}
              </ol>
            )}

            <p className="mt-2 font-mono text-xs text-zinc-600">
              Bars show fit relative to this list, not a probability.
            </p>
          </div>
        )}

        {children}
      </div>
    </section>
  );
}
