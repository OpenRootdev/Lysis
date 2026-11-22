"use client";

import { useEffect, useState } from "react";
import { safeGithubUrl } from "@/lib/safeUrl";
import AboutSection from "@/components/AboutSection";
import Link from "next/link";

import {
  API,
  parseRepo,
  getModel,
  rank,
  sendVote,
  type Issue,
  type ModelMeta,
  type RankResponse,
} from "@/lib/api";

import Image from "next/image";
import RepoFinder from "@/components/RepoFinder";
import AuthButton from "@/components/AuthButton";
import HistoryButton from "@/components/HistoryButton";
import { logActivity } from "@/lib/activity";

export default function Home() {
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

  async function run(input: string) {
    const name = parseRepo(input);

    if (!/^[\w.-]+\/[\w.-]+$/.test(name)) {
      setError("Enter a repository as owner/name, for example psf/requests.");
      return;
    }

    setLoading(true);
    setSlow(false);
    setError(null);

    const timer = setTimeout(() => setSlow(true), 4000);

    try {
      const res = await rank(name, 10);
      setData(res);
      try {
        sessionStorage.setItem("lysis:last", JSON.stringify(res));
      } catch {
        /* storage unavailable */
      }
      void logActivity({ kind: "rank", repo: res.repo });
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

    void logActivity({
      kind: "vote",
      repo: data.repo,
      issue_number: issue.number,
      helpful: up,
    });

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

  const btn =
    "inline-flex h-9 w-9 items-center justify-center rounded-md border border-zinc-800 text-zinc-300 hover:border-emerald-400 hover:text-emerald-400";
  return (
    <main className="app-shell mx-auto flex w-full max-w-5xl flex-col px-4 pb-4 pt-6 sm:px-5 sm:pt-8">
      <header className="shrink-0">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1 font-mono text-sm text-emerald-400">
            <Image
              src="/lysis.svg"
              alt=""
              width={25}
              draggable={false}
              height={25}
              className="pointer-events-none h-8 w-8 select-none rounded-sm"
            />
            lysis
            <span className="text-zinc-600">/</span>
            <span className="text-zinc-500">v0.1</span>
          </div>
          <div className="flex items-center gap-2">
            {data && !loading && data.insights && (
              <Link
                href="/insights"
                aria-label="How it works"
                title="How it works"
                className={btn}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 11v5M12 8h.01" />
                </svg>
              </Link>
            )}
            <HistoryButton />
            <AuthButton />
          </div>
        </div>

        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-zinc-50 sm:text-3xl lg:text-4xl">
          Find the issues a beginner can actually finish.
        </h1>

        <p className="hide-short mt-3 max-w-xl text-sm text-zinc-400 sm:mt-4 sm:text-base">
          Lysis ranks a repository&apos;s open issues by how likely a first-time
          contributor is to get a PR merged, learned from thousands of real
          outcomes instead of labels.
        </p>
      </header>

      <RepoFinder
        onPick={(name) => void run(name)}
        onClear={() => {
          setData(null);
          setError(null);
        }}
      >
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
              <p className="text-zinc-400">
                No open, unassigned issues found for {data.repo}.
              </p>
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
                              href={safeGithubUrl(issue.url)}
                              onClick={() =>
                                void logActivity({
                                  kind: "open",
                                  repo: data.repo,
                                  issue_number: issue.number,
                                })
                              }
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium text-zinc-100 hover:text-emerald-400"
                            >
                              {issue.full_title}
                            </a>

                            <div className="mt-1 font-mono text-xs text-zinc-500">
                              #{issue.number}
                            </div>

                            <div className="mt-3 flex items-center gap-3">
                              <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                                <div
                                  className="h-full rounded-full bg-emerald-500"
                                  style={{
                                    width: `${(issue.score / max) * 100}%`,
                                  }}
                                />
                              </div>

                              <span className="w-12 text-right font-mono text-xs text-emerald-400">
                                {issue.score.toFixed(3)}
                              </span>
                            </div>

                            {issue.why && (
                              <p className="mt-3 text-sm leading-relaxed text-zinc-400">
                                {issue.why}
                              </p>
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

                              {chosen && (
                                <span className="text-zinc-600">thanks</span>
                              )}
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
        <AboutSection />
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
            <Link href="/privacy" className="hover:text-zinc-400">
              privacy
            </Link>
          </div>
        </footer>
      </RepoFinder>
    </main>
  );
}
