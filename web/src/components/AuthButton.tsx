"use client";

import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";

import { supabase } from "@/lib/supabase";

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

const SignIn = () => (
  <svg {...svg}>
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21a8 8 0 0 1 16 0" />
  </svg>
);

const LogOut = () => (
  <svg {...svg}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <path d="m16 17 5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);

export default function AuthButton() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setUser(data.session?.user ?? null));
    const { data } = supabase.auth.onAuthStateChange((_e, s) => setUser(s?.user ?? null));
    return () => data.subscription.unsubscribe();
  }, []);

  if (!supabase) return null;

  const btn =
    "inline-flex h-9 w-9 items-center justify-center rounded-md border border-zinc-800 text-zinc-300 hover:border-emerald-400 hover:text-emerald-400";

  if (!user) {
    return (
      <button
        className={btn}
        title="Sign in with GitHub"
        aria-label="Sign in with GitHub"
        onClick={() =>
          void supabase!.auth.signInWithOAuth({
            provider: "github",
            options: { redirectTo: window.location.origin },
          })
        }
      >
        <SignIn />
      </button>
    );
  }

  return (
    <button
      className={btn}
      title="Log out"
      aria-label="Log out"
      onClick={() => void supabase!.auth.signOut()}
    >
      <LogOut />
    </button>
  );
}
