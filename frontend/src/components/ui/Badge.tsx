import type { ReactNode } from "react";

type BadgeTone =
  | "neutral"
  | "forum"
  | "tool"
  | "youtube"
  | "x"
  | "cybersecurity"
  | "ai"
  | "piracy"
  | "dark-web"
  | "news"
  | "docs-reference"
  | "archive-mirror"
  | "official"
  | "verified"
  | "unverified"
  | "working"
  | "down"
  | "unknown"
  | "seized";

type BadgeProps = {
  children: ReactNode;
  tone?: string;
};

const toneClasses: Record<BadgeTone, string> = {
  neutral: "border-slate-700 bg-slate-800/80 text-slate-200",
  forum: "border-amber-800/80 bg-amber-950/50 text-amber-200",
  tool: "border-sky-800/80 bg-sky-950/60 text-sky-200",
  youtube: "border-red-800/80 bg-red-950/50 text-red-200",
  x: "border-slate-700 bg-slate-800/80 text-slate-200",
  cybersecurity: "border-cyan-800/80 bg-cyan-950/50 text-cyan-200",
  ai: "border-violet-800/80 bg-violet-950/50 text-violet-200",
  piracy: "border-fuchsia-800/80 bg-fuchsia-950/50 text-fuchsia-200",
  "dark-web": "border-emerald-800/80 bg-emerald-950/50 text-emerald-200",
  news: "border-blue-800/80 bg-blue-950/50 text-blue-200",
  "docs-reference": "border-indigo-800/80 bg-indigo-950/50 text-indigo-200",
  "archive-mirror": "border-teal-800/80 bg-teal-950/50 text-teal-200",
  official: "border-green-800/80 bg-green-950/50 text-green-200",
  verified: "border-lime-800/80 bg-lime-950/50 text-lime-200",
  unverified: "border-slate-700 bg-slate-800/80 text-slate-200",
  working: "border-emerald-800/80 bg-emerald-950/50 text-emerald-200",
  down: "border-rose-800/80 bg-rose-950/50 text-rose-200",
  unknown: "border-slate-700 bg-slate-800/80 text-slate-200",
  seized: "border-amber-800/80 bg-amber-950/50 text-amber-200",
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  const resolvedTone = tone in toneClasses ? (tone as BadgeTone) : "neutral";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide ${toneClasses[resolvedTone]}`}
    >
      {children}
    </span>
  );
}
