import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "How it works",
  robots: { index: false, follow: true },
  alternates: { canonical: "/insights" },
};

export default function Layout({ children }: { children: ReactNode }) {
  return children;
}