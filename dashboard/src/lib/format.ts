const eur = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 2 });
const eurCompact = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", notation: "compact", maximumFractionDigits: 1 });

export const formatCurrency = (v: number) => eur.format(v);
export const formatCurrencyCompact = (v: number) => eurCompact.format(v);
export const formatSignedCurrency = (v: number) => (v > 0 ? "+" : v < 0 ? "−" : "") + eur.format(Math.abs(v));
export const formatPercent = (v: number) => `${v.toFixed(1)}%`;
export const formatSignedPercent = (v: number) => (v > 0 ? "+" : v < 0 ? "−" : "") + `${Math.abs(v).toFixed(2)}%`;

export const formatDateTime = (iso: string) =>
  new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "UTC" }).format(new Date(iso)) + " UTC";
export const formatShortDate = (iso: string) =>
  new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", timeZone: "UTC" }).format(new Date(iso));
export const formatLongDate = (iso: string) =>
  new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(iso));

export function formatKpi(value: number, format: "currency" | "percent" | "signedCurrency" | "signedPercent") {
  switch (format) {
    case "currency": return formatCurrency(value);
    case "percent": return formatPercent(value);
    case "signedCurrency": return formatSignedCurrency(value);
    case "signedPercent": return formatSignedPercent(value);
  }
}
