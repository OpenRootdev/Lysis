const INFO: Record<string, [string, string]> = {
  gfi: ["Labeled good first issue", "Maintainers flagged it as beginner friendly."],
  help_wanted: ["Labeled help wanted", "Maintainers are asking for outside help."],
  bug: ["Labeled bug", "A reported defect, often well scoped."],
  docs: ["Labeled documentation", "Docs changes tend to be quick to review."],
  n_labels: ["Number of labels", "Well-triaged issues usually carry several labels."],
  body_len_log: ["Description length", "Longer descriptions usually mean clearer requirements."],
  title_len: ["Title length", "Short, specific titles tend to describe focused tasks."],
  has_code: ["Includes a code snippet", "A snippet makes the problem easier to reproduce."],
  is_maintainer: ["Opened by a maintainer", "Maintainers write issues they intend to review."],
  has_license: ["Repo has a license", "A license signals a project open to contributions."],
  repo_age_days: ["Repo age", "Older projects have more settled review habits."],
  prs_90d: ["Recent merged PRs", "More merges means maintainers are actively reviewing."],
  merge_gap_days: ["Days since last merge", "Long gaps can mean slow or stalled review."],
};

export function featureName(f: string) {
  if (INFO[f]) return INFO[f][0];
  if (f.startsWith("lang_")) return `Language: ${f.slice(5)}`;
  return f.replace(/_/g, " ");
}

export const featureHint = (f: string) => INFO[f]?.[1] ?? "";