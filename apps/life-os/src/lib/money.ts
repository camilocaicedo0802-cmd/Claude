/**
 * Money is stored as integers in minor units (1 unit = 1/100 of the currency) to avoid
 * floating point drift. Every sum, difference and comparison happens on integers; only
 * proration rounds, and it rounds explicitly.
 */
export type Minor = number;

export const MINOR_SCALE = 100;

export const CURRENCIES = [
  { code: "COP", label: "Peso colombiano", decimals: 0 },
  { code: "USD", label: "Dólar estadounidense", decimals: 2 },
  { code: "EUR", label: "Euro", decimals: 2 },
  { code: "MXN", label: "Peso mexicano", decimals: 2 },
  { code: "ARS", label: "Peso argentino", decimals: 0 },
  { code: "CLP", label: "Peso chileno", decimals: 0 },
  { code: "PEN", label: "Sol peruano", decimals: 2 },
] as const;

export type CurrencyCode = (typeof CURRENCIES)[number]["code"];

export function currencyDecimals(code: string): number {
  return CURRENCIES.find((c) => c.code === code)?.decimals ?? 2;
}

/**
 * Parses user input into minor units. Accepts Spanish formatting ("1.250.000", "1.250,50"),
 * plain digits ("1250000") and dot decimals ("12.5"). Returns null when the text is not a number.
 */
export function parseMoney(input: string | number | null | undefined): Minor | null {
  if (input === null || input === undefined) return null;
  if (typeof input === "number") {
    if (!Number.isFinite(input)) return null;
    return Math.round(input * MINOR_SCALE);
  }
  let s = input.trim().replace(/[\s$€]|COP|USD|EUR/gi, "");
  if (!s) return null;
  let negative = false;
  if (s.startsWith("-")) {
    negative = true;
    s = s.slice(1);
  }
  let intPart = s;
  let fracPart = "";
  if (s.includes(",")) {
    // Comma is the decimal separator; dots are thousands separators.
    const [i, f = ""] = s.split(",");
    if (s.split(",").length > 2) return null;
    intPart = i.replace(/\./g, "");
    fracPart = f;
  } else if (/^\d{1,3}(\.\d{3})+$/.test(s)) {
    intPart = s.replace(/\./g, "");
  } else if (s.includes(".")) {
    const parts = s.split(".");
    if (parts.length > 2) return null;
    intPart = parts[0] || "0";
    fracPart = parts[1];
  }
  if (!/^\d+$/.test(intPart) || (fracPart && !/^\d+$/.test(fracPart))) return null;
  const cents = Number((fracPart + "00").slice(0, 2));
  const roundUp = fracPart.length > 2 && Number(fracPart[2]) >= 5 ? 1 : 0;
  const value = Number(intPart) * MINOR_SCALE + cents + roundUp;
  if (!Number.isSafeInteger(value)) return null;
  return negative ? -value : value;
}

export function toMajor(minor: Minor): number {
  return minor / MINOR_SCALE;
}

export function fromMajor(major: number): Minor {
  return Math.round(major * MINOR_SCALE);
}

export function sumMinor(values: Iterable<Minor>): Minor {
  let total = 0;
  for (const v of values) total += v;
  return total;
}

/** amount × numerator / denominator, rounded half away from zero. */
export function prorate(amount: Minor, numerator: number, denominator: number): Minor {
  if (denominator <= 0) return 0;
  const raw = (amount * numerator) / denominator;
  return raw < 0 ? -Math.round(-raw) : Math.round(raw);
}

/** Splits an amount into equal parts, rounding down so the recommendation never overshoots. */
export function divideFloor(amount: Minor, parts: number): Minor {
  if (parts <= 0) return 0;
  return Math.floor(amount / parts);
}

export function percentOf(part: Minor, total: Minor): number {
  if (total <= 0) return 0;
  return (part / total) * 100;
}

const formatterCache = new Map<string, Intl.NumberFormat>();

function getFormatter(currency: string, locale: string, compact: boolean, decimals: number) {
  const key = `${currency}|${locale}|${compact}|${decimals}`;
  let f = formatterCache.get(key);
  if (!f) {
    f = new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      currencyDisplay: "narrowSymbol",
      notation: compact ? "compact" : "standard",
      minimumFractionDigits: compact ? 0 : decimals,
      maximumFractionDigits: compact ? 1 : decimals,
    });
    formatterCache.set(key, f);
  }
  return f;
}

export interface FormatMoneyOptions {
  currency?: string;
  locale?: string;
  compact?: boolean;
  /** Prefix positive values with "+" */
  signed?: boolean;
}

export function formatMoney(amount: Minor, opts: FormatMoneyOptions = {}): string {
  const currency = opts.currency ?? "COP";
  const locale = opts.locale ?? "es-CO";
  const decimals = currencyDecimals(currency);
  const major = toMajor(amount);
  const shown = decimals === 0 ? Math.round(major) : major;
  const text = getFormatter(currency, locale, !!opts.compact, decimals).format(shown);
  if (opts.signed && amount > 0) return `+${text}`;
  return text;
}

/** Formats a minor amount as editable text ("1.250.000" or "1.250,50"). */
export function moneyToInput(amount: Minor | null | undefined, currency = "COP"): string {
  if (amount === null || amount === undefined) return "";
  const decimals = currencyDecimals(currency);
  const major = toMajor(amount);
  return new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
    useGrouping: true,
  }).format(major);
}
