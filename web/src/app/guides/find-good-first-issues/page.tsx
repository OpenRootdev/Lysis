import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "How to find good first issues on GitHub",
  description:
    "A practical checklist for choosing a GitHub issue you can actually finish as a first-time contributor, and why the good first issue label is not enough.",
  alternates: { canonical: "/guides/find-good-first-issues" },
};

const steps: [string, string][] = [
  [
    "Check that the project is alive",
    "Open the Pull requests tab and look for pull requests merged in the last few weeks. A repo where outside contributions sit for months is a poor first target, however friendly its labels look.",
  ],
  [
    "Read the contributing guide first",
    "CONTRIBUTING.md explains how to set up the project, which branch to target and which tests to run. Following it is the fastest way to avoid a rejected pull request.",
  ],
  [
    "Pick an issue with a clear finish line",
    "A good first issue describes the problem, the expected result and where to look. If you cannot say in one sentence what done looks like, move on.",
  ],
  [
    "Skip issues someone already claimed",
    "Check the assignee and the recent comments. If another person asked to work on it, choose a different issue or ask first.",
  ],
  [
    "Comment before you start",
    "A short message such as \"I would like to work on this, is it still open?\" saves wasted effort and shows maintainers you are serious.",
  ],
  [
    "Keep the first change small",
    "A focused fix with a test is easier to review and far more likely to be merged than a large refactor.",
  ],
];

export default function Guide() {
  return (
    <main className="mx-auto w-full max-w-2xl px-4 pb-16 pt-8 sm:px-5">
      <Link href="/" className="font-mono text-sm text-emerald-400 hover:text-emerald-300">
        lysis
      </Link>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight text-zinc-50 sm:text-3xl">
        How to find good first issues on GitHub
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-zinc-400">
        Your first open-source contribution goes best when the issue is small, clear and in a project that
        reviews outside pull requests. Here is a checklist you can follow on any repository.
      </p>

      {steps.map(([t, d], i) => (
        <section key={t} className="mt-8">
          <h2 className="text-lg font-semibold text-zinc-100">
            {i + 1}. {t}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-zinc-400">{d}</p>
        </section>
      ))}

      <h2 className="mt-10 text-lg font-semibold text-zinc-100">Why the good first issue label is not enough</h2>
      <p className="mt-2 text-sm leading-relaxed text-zinc-400">
        Labels are applied by hand, so many are stale, missing or too optimistic. An issue can carry the label
        for years while the project has stopped reviewing outside work. Treat the label as one signal, and check
        recent merge activity and how clearly the issue is written.
      </p>

      <h2 className="mt-10 text-lg font-semibold text-zinc-100">Where Lysis helps</h2>
      <p className="mt-2 text-sm leading-relaxed text-zinc-400">
        Lysis does that first filtering for you. It ranks a repository&apos;s open, unassigned issues using
        signals learned from historical first-time contributor outcomes, such as description clarity, repo age and
        recent merge activity. It was trained on Python and JavaScript repositories. A higher score means an issue
        ranks above the others in that repo. It is not a promise that an issue is easy or that a pull request
        will be merged.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-emerald-400"
      >
        Try a repository
      </Link>
    </main>
  );
}