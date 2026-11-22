"use client";

import { useState } from "react";

export default function FaqItem({ q, a }: { q: string; a: string }) {
  const [shown, setShown] = useState(false);

  return (
    <button
      type="button"
      aria-expanded={shown}
      onClick={() => setShown((v) => !v)}
      onPointerEnter={(e) => e.pointerType === "mouse" && setShown(true)}
      onPointerLeave={(e) => e.pointerType === "mouse" && setShown(false)}
      className="grid w-full rounded-xl border border-transparent px-4 py-2 text-left text-sm transition-colors hover:border-emerald-500/50"
    >
      <span
        aria-hidden={shown}
        className={`col-start-1 row-start-1 font-medium text-zinc-200 transition-opacity duration-200 ${
          shown ? "opacity-0" : "opacity-100"
        }`}
      >
        {q}
      </span>
      <span
        aria-hidden={!shown}
        className={`col-start-1 row-start-1 text-emerald-400 transition-opacity duration-200 ${
          shown ? "opacity-100" : "opacity-0"
        }`}
      >
        {a}
      </span>
    </button>
  );
}