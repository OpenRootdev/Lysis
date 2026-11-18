import { supabase } from "@/lib/supabase";

export type ActivityKind = "rank" | "open" | "vote";

export type ActivityEvent = {
  kind: ActivityKind;
  repo: string;
  issue_number?: number;
  helpful?: boolean;
};

// Fire-and-forget. Silent for guests and never breaks the UI.
export async function logActivity(e: ActivityEvent) {
  if (!supabase) return;
  try {
    const { data } = await supabase.auth.getSession();
    if (!data.session) return;
    await supabase.from("activity").insert({
      kind: e.kind,
      repo: e.repo.slice(0, 140),
      issue_number: e.issue_number ?? null,
      helpful: e.helpful ?? null,
    });
  } catch {
    /* ignore */
  }
}