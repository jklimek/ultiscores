import { type Division } from "@/lib/api/schemas";

const SHORT_DATE = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
});

const DATE_TIME = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "medium",
  timeStyle: "short",
});

export function formatDate(value: string) {
  if (!value || value === "") return "TBD";
  const date = new Date(value);
  if (isNaN(date.getTime())) return "TBD";
  return SHORT_DATE.format(date);
}

export function formatDateRange(start: string, end: string) {
  const startDate = new Date(start);
  const endDate = new Date(end);

  const sameMonth = startDate.getMonth() === endDate.getMonth();
  const startLabel = SHORT_DATE.format(startDate);
  const endLabel = sameMonth
    ? endDate.getDate().toString()
    : SHORT_DATE.format(endDate);

  return `${startLabel} – ${endLabel}`;
}

export function formatDivision(division: Division) {
  return division.charAt(0).toUpperCase() + division.slice(1);
}

export function formatDateTime(value: string) {
  if (!value || value === "") return "TBD";
  const date = new Date(value);
  if (isNaN(date.getTime())) return "TBD";
  return DATE_TIME.format(date);
}

