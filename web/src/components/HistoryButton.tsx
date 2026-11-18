"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { supabase } from "@/lib/supabase";

type Row = {
  id: number;
  created_at: string;
  kind: "rank" | "open" | "vote";
  repo: string;
  issue_number: number | null;
  helpful: boolean | null;
};

const svg = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

function ago(iso: string) {
  const s = Math.max(1, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 3600) return `${Math.max(1, Math.round(s / 60))}m ago`;
  if (s < 86400) return `${Math.round(s / 3600)}h ago`;
  return `${Math.round(s / 86400)}d ago`;
}

function label(r: Row) {
  if (r.kind === "rank") return "Ranked";
  if (r.kind === "open") return r.issue_number ? "Opened issue" : "Opened repo";
  return r.helpful ? "Voted helpful" : "Voted not helpful";
}

export default function HistoryButton() {
  const [signedIn, setSignedIn] = useState(false);
  const [open, setOpen] = useState(false);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setSignedIn(!!data.session));
    const { data } = supabase.auth.onAuthStateChange((_e, s) => {
      setSignedIn(!!s);
      if (!s) {
        setOpen(false);
        setRows(null);
      }
    });
    return () => data.subscription.unsubscribe();
  }, []);

  const load = useCallback(async () => {
    if (!supabase) return;
    setFailed(false);
    const { data, error } = await supabase
      .from("activity")
      .select("id,created_at,kind,repo,issue_number,helpful")
      .order("created_at", { ascending: false })
      .limit(50);
    if (error) setFailed(true);
    else setRows(data as Row[]);
  }, []);

  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    };
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("mousedown", away);
      document.removeEventListener("keydown", esc);
    };
  }, [open]);

  async function wipe() {
    if (!supabase) return;
    if (!confirm) return setConfirm(true);
    const { error } = await supabase.from("activity").delete().gte("id", 0);
    setConfirm(false);
    if (error) setFailed(true);
    else setRows([]);
  }

  if (!supabase || !signedIn) return null;

  return (
    <div className="relative" ref={box}>
      <button
        className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-zinc-800 text-zinc-300 hover:border-emerald-400 hover:text-emerald-400"
        title="Activity log"
        aria-label="Activity log"
        aria-expanded={open}
        onClick={() => {
          setConfirm(false);
          if (!open) void load();
          setOpen((o) => !o);
        }}
      >
        <svg {...svg}>
          <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
          <path d="M3 3v5h5" />
          <path d="M12 7v5l3 2" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-2 w-80 max-w-[calc(100vw-2rem)] rounded-xl border border-zinc-800 bg-zinc-950 shadow-xl">
          <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3 font-mono text-xs text-zinc-400">
            <span>activity log</span>
            {rows && rows.length > 0 && (
              <button
                className={confirm ? "text-red-400" : "hover:text-zinc-200"}
                onClick={() => void wipe()}
              >
                {confirm ? "confirm delete" : "delete all"}
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {failed ? (
              <p className="px-4 py-6 text-sm text-zinc-500">Could not load your activity.</p>
            ) : rows === null ? (
              <p className="px-4 py-6 text-sm text-zinc-500">Loading...</p>
            ) : rows.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-500">
                Nothing yet. Rank a repo, open an issue or vote and it shows up here.
              </p>
            ) : (
              <ul>
                {rows.map((r) => (
                  <li key={r.id} className="border-b border-zinc-900 px-4 py-3 last:border-0">
                    <div className="flex justify-between font-mono text-xs text-zinc-500">
                      <span>{label(r)}</span>
                      <span>{ago(r.created_at)}</span>
                    </div>
                    <a
                      href={`https://github.com/${r.repo}${r.issue_number ? `/issues/${r.issue_number}` : ""}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 block truncate text-sm text-zinc-200 hover:text-emerald-400"
                    >
                      {r.repo}
                      {r.issue_number ? ` #${r.issue_number}` : ""}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
