import Link from "next/link";
import FaqItem from "@/components/FaqItem";

const faqs: [string, string][] = [
  [
    "Why not just filter by the good first issue label?",
    "Labels go stale or are missing. Lysis also looks at signals such as description clarity, repo age and how recently maintainers merged pull requests.",
  ],
  [
    "Which languages does it cover?",
    "The model was trained on Python and JavaScript repositories. Other languages can still be ranked, but expect rougher results.",
  ],
  [
    "Does AI decide the ranking?",
    "No. A gradient boosted model produces the score. Groq-generated text only explains a result and never changes the ranking.",
  ],
  [
    "How accurate is it?",
    "Accuracy is measured across all training data, not per repository. After a search, open the info icon to see how that result was scored.",
  ],
];

export default function AboutSection() {
  return (
    <section className="mt-6 border-t border-zinc-800 pt-8">
      <h2 className="text-xl font-semibold text-zinc-100">How Lysis works</h2>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-zinc-400">
        Lysis looks at a GitHub repository&apos;s open issues that nobody is
        assigned to, turns each one into signals such as labels, description
        length, language, repo age and recent merge activity, and scores how
        likely a first-time contributor is to get a pull request merged. The
        model learned from historical contributor outcomes, not from labels
        alone.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-zinc-100">
        What the score means
      </h2>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-zinc-400">
        A higher score ranks an issue above the others in the same repository.
        It is not a promise that an issue is easy or that a pull request will be
        merged. Read the issue and the contributing guide before you start.
      </p>
      <p className="mt-3 text-sm">
        <Link
          href="/guides/find-good-first-issues"
          className="text-emerald-400 hover:text-emerald-300"
        >
          Read: how to find good first issues on GitHub
        </Link>
      </p>

      <h2 className="mt-8 text-xl font-semibold text-zinc-100">Questions</h2>
      <p className="mt-3 text-xs text-zinc-500">
        Hover a question to see the answer.
      </p>
      <div className="mt-3 max-w-2xl space-y-1">
        {faqs.map(([q, a]) => (
          <FaqItem key={q} q={q} a={a} />
        ))}
      </div>
    </section>
  );
}
