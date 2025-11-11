"use client";

import { cn } from "@/lib/utils";

export type TimelineItem = {
  id: string | number;
  timeLabel: string;
  title: string;
  description?: string;
  teamName?: string;
  tone?: "goal" | "turnover" | "timeout" | "default";
};

const toneStyles: Record<NonNullable<TimelineItem["tone"]>, string> = {
  default: "border-border bg-background text-foreground",
  goal: "border-emerald-500/60 bg-emerald-500/10 text-emerald-600 dark:text-emerald-300",
  turnover:
    "border-amber-500/60 bg-amber-500/15 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300",
  timeout:
    "border-sky-500/60 bg-sky-500/10 text-sky-600 dark:bg-sky-500/15 dark:text-sky-300",
};

export interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

export function Timeline({ items, className }: TimelineProps) {
  return (
    <ol className={cn("relative flex flex-col gap-4", className)}>
      {items.map((item, index) => {
        const tone = item.tone ?? "default";
        return (
          <li
            key={item.id}
            className="relative flex gap-4"
          >
            <div className="flex w-16 flex-col items-end pt-1 text-xs text-muted-foreground">
              <span>{item.timeLabel}</span>
              {item.teamName ? (
                <span className="mt-1 font-medium text-foreground">
                  {item.teamName}
                </span>
              ) : null}
            </div>
            <div className="flex flex-1 flex-col gap-2">
              <div
                className={cn(
                  "relative rounded-2xl border px-4 py-3 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/70",
                  toneStyles[tone],
                )}
              >
                <p className="text-sm font-medium">{item.title}</p>
                {item.description ? (
                  <p className="mt-1 text-xs text-muted-foreground">
                    {item.description}
                  </p>
                ) : null}
              </div>
              {index !== items.length - 1 ? (
                <div className="ml-8 h-full border-l border-dashed border-border/70 dark:border-border/40" />
              ) : null}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

