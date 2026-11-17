export const API = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export type Issue = {
  score: number;
  number: number;
  title: string;
  url: string;
  full_title: string;
  why?: string | null;
};

export type RankResponse = { repo: string; model_date: string; issues: Issue[] };

export type ModelMeta = {
  trained_at: string;
  n_train: number;
  cv: { ap: number; auc: number };
};

export type Vote = {
  repo: string;
  issue_number: number;
  score: number;
  helpful: boolean;
  model_date: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, init);
  } catch {
    throw new Error("Cannot reach the API. It may be waking up, try again in a minute.");
  }
  if (!res.ok) {
    if (res.status === 422) throw new Error("Enter a repository as owner/name.");
    if (res.status === 404) throw new Error("Repository not found.");
    if (res.status === 429) throw new Error("Rate limit reached (30/hour). Try again later.");
    let detail = "";
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      detail = "";
    }
    throw new Error(detail || `API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const getModel = () => request<ModelMeta>("/model");

export const rank = (repo: string, top: number) =>
  request<RankResponse>(`/rank?repo=${encodeURIComponent(repo)}&top=${top}&explain=true`);

export const sendVote = (vote: Vote) =>
  request<{ saved: boolean }>("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vote),
  });