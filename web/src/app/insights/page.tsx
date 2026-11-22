"use client";

import {
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import Link from "next/link";
import { getModel, type ModelMeta, type RankResponse } from "@/lib/api";
import { featureHint, featureName } from "@/lib/featureInfo";

function Section({
  title,
  sub,
  children,
}: {
  title: string;
  sub?: string;
  children: ReactNode;
}) {
  return (
    <section className="mt-8 rounded-xl border border-zinc-800 bg-zinc-900/30 p-4 sm:p-5">
      <h2 className="text-base font-semibold text-zinc-100">{title}</h2>
      {sub && <p className="mt-1 text-sm text-zinc-400">{sub}</p>}
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Tile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 p-3">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 font-mono text-lg text-zinc-100">{value}</div>
      <div className="mt-1 text-xs text-zinc-500">{hint}</div>
    </div>
  );
}

const noop = () => () => {};
const readLast = () => {
  try {
    return sessionStorage.getItem("lysis:last") ?? "";
  } catch {
    return "";
  }
};

export default function Insights() {
  const raw = useSyncExternalStore(noop, readLast, () => "loading");
  const data = useMemo<RankResponse | null | undefined>(() => {
    if (raw === "loading") return undefined;
    try {
      return raw ? (JSON.parse(raw) as RankResponse) : null;
    } catch {
      return null;
    }
  }, [raw]);
  const [meta, setMeta] = useState<ModelMeta | null>(null);

  useEffect(() => {
    getModel()
      .then(setMeta)
      .catch(() => setMeta(null));
  }, []);
  const ins = data?.insights;
  const top = data?.issues.slice(0, 5) ?? [];
  const median = ins?.median_score ?? 0;
  const max = Math.max(...top.map((i) => i.score), median, 0.0001);
  const ratio = top[0] && median > 0 ? top[0].score / median : null;
  const withDrivers = top.filter((i) => i.drivers?.length).slice(0, 3);
  const dmax = Math.max(
    0.0001,
    ...withDrivers.flatMap((i) => i.drivers!.map((d) => Math.abs(d.effect))),
  );
  const imp = meta?.importance ? Object.entries(meta.importance) : [];
  const imax = Math.max(0.0001, ...imp.map(([, v]) => v));
  const c = ins?.context;

  return (
    <main className="mx-auto w-full max-w-3xl px-4 pb-16 pt-8 sm:px-5">
      <Link
        href="/"
        className="font-mono text-sm text-emerald-400 hover:text-emerald-300"
      >
        back to search
      </Link>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight text-zinc-50 sm:text-3xl">
        {data && ins ? `How Lysis ranked ${data.repo}` : "How Lysis works"}
      </h1>
      <p className="mt-2 text-sm text-zinc-400">
        Lysis reads a repo&apos;s open issues, turns each one into a handful of
        signals, and scores how likely a first-time contributor is to get a pull
        request merged.
      </p>

      {data === undefined ? null : !data || !ins ? (
        <Section title="No search yet">
          <p className="text-sm text-zinc-400">
            Search for a repository on the home page, then come back here to see
            how its results were scored.
          </p>
        </Section>
      ) : (
        <>
          <Section
            title="Snapshot"
            sub={`${ins.n_scored} of ${ins.n_open} open issues were scored (issues that already have an assignee are skipped). ${ins.n_gfi} carry the good first issue label.`}
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <Tile
                label="Repo age"
                value={
                  c?.repo_age_days == null
                    ? "n/a"
                    : `${(c.repo_age_days / 365).toFixed(1)} yrs`
                }
                hint="Older projects have more settled review habits."
              />
              <Tile
                label="PRs merged, last 90 days"
                value={c?.merged_90d == null ? "n/a" : String(c.merged_90d)}
                hint="Counted from the latest 100 closed PRs."
              />
              <Tile
                label="Days since last merge"
                value={
                  c?.days_since_merge == null
                    ? "n/a"
                    : String(c.days_since_merge)
                }
                hint="Long gaps can mean slow review."
              />
            </div>
          </Section>

          <Section
            title="Top picks vs a typical issue"
            sub={
              ratio
                ? `Your top pick scores ${ratio.toFixed(1)}x the typical issue here. The bigger the gap, the more it stands out.`
                : "Each bar is an issue score. The white line marks the typical issue in this repo."
            }
          >
            <ul className="space-y-3">
              {top.map((i) => (
                <li key={i.number}>
                  <div className="flex justify-between gap-3 text-xs">
                    <span className="truncate text-zinc-300">
                      #{i.number} {i.full_title}
                    </span>
                    <span className="font-mono text-emerald-400">
                      {i.score.toFixed(3)}
                    </span>
                  </div>
                  <div className="relative mt-1 h-2 rounded-full bg-zinc-800">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${(i.score / max) * 100}%` }}
                    />
                    <div
                      className="absolute -top-1 h-4 w-px bg-zinc-200"
                      style={{ left: `${(median / max) * 100}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-zinc-500">
              White line: the typical (median) issue in this repo, score{" "}
              {median.toFixed(3)}. Scores only compare issues within one repo,
              and older issues are discounted.
            </p>
          </Section>

          {withDrivers.length > 0 && (
            <Section
              title="What moved the top scores"
              sub="Compared with a typical issue in this repo. Green raised the score, red lowered it."
            >
              <ul className="space-y-5">
                {withDrivers.map((i) => (
                  <li key={i.number}>
                    <div className="truncate text-sm text-zinc-200">
                      #{i.number} {i.full_title}
                    </div>
                    {i.drivers!.map((d) => (
                      <div
                        key={d.feature}
                        className="mt-2 flex items-center gap-3 text-xs text-zinc-400"
                      >
                        <span className="w-44 shrink-0">
                          {featureName(d.feature)}
                        </span>
                        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                          <div
                            className={`h-full rounded-full ${d.effect >= 0 ? "bg-emerald-500" : "bg-rose-500"}`}
                            style={{
                              width: `${(Math.abs(d.effect) / dmax) * 100}%`,
                            }}
                          />
                        </div>
                        <span className="w-12 text-right font-mono">
                          {d.effect > 0 ? "+" : ""}
                          {d.effect.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-xs text-zinc-500">
                An estimate made by swapping each signal for the typical value
                and measuring the change.
              </p>
            </Section>
          )}
        </>
      )}

      {imp.length > 0 && (
        <Section
          title="What the model relies on overall"
          sub="Across all repos it was trained on, not just this one."
        >
          <ul className="space-y-3">
            {imp.map(([f, v]) => (
              <li key={f}>
                <div className="flex items-center gap-3 text-sm text-zinc-300">
                  <span className="w-48 shrink-0">{featureName(f)}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${(v / imax) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="text-xs text-zinc-500">{featureHint(f)}</div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-zinc-800 p-4">
          <h3 className="text-sm font-semibold text-zinc-100">
            If you are new to open source
          </h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-400">
            <li>
              Start with a high score that carries the good first issue label.
            </li>
            <li>
              Read CONTRIBUTING and comment on the issue before you start.
            </li>
            <li>
              Prefer repos that merged PRs recently, since they will review
              yours.
            </li>
          </ul>
        </div>
        <div className="rounded-xl border border-zinc-800 p-4">
          <h3 className="text-sm font-semibold text-zinc-100">
            If you contribute often
          </h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-400">
            <li>
              Use the gap between the top picks and the median to see how
              selective the ranking is.
            </li>
            <li>
              Check days since last merge before investing time in a repo.
            </li>
            <li>
              Treat scores as a shortlist. Your own interest still decides.
            </li>
          </ul>
        </div>
      </div>

      {meta && (
        <p className="mt-8 font-mono text-xs text-zinc-600">
          model {meta.trained_at.slice(0, 10)} · {meta.n_train.toLocaleString()}{" "}
          training issues · CV AP {meta.cv.ap} · AUC {meta.cv.auc} · measured
          across all repos, not per repo
        </p>
      )}
    </main>
  );
}
