/**
 * Minimal typed HTTP client for the Python FastAPI backend.
 * The dashboard talks ONLY to this backend — never to Supabase directly.
 * No credentials are sent or read here; VITE_* values are public.
 */

export const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;
  readonly requestId: string | null;
  readonly url: string;

  constructor(opts: {
    message: string;
    status: number;
    url: string;
    detail?: unknown;
    requestId?: string | null;
  }) {
    super(opts.message);
    this.name = "ApiError";
    this.status = opts.status;
    this.url = opts.url;
    this.detail = opts.detail;
    this.requestId = opts.requestId ?? null;
  }

  /** status 0 = network/CORS failure, no HTTP response received. */
  get isNetworkError(): boolean {
    return this.status === 0;
  }
}

/** Validate and normalise a base URL (strip trailing slashes). Throws on invalid input. */
export function normalizeBaseUrl(raw: string | undefined | null): string {
  const value = (raw ?? "").trim() || DEFAULT_API_BASE_URL;
  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error(`Invalid VITE_API_BASE_URL: "${value}"`);
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    throw new Error(`VITE_API_BASE_URL must use http(s): "${value}"`);
  }
  return value.replace(/\/+$/, "");
}

export function getApiBaseUrl(): string {
  return normalizeBaseUrl(import.meta.env["VITE_API_BASE_URL"] as string | undefined);
}

export type QueryValue = string | number | boolean | null | undefined;
export type QueryParams = Record<string, QueryValue>;

/** Build "?a=1&b=2", skipping null/undefined. Returns "" when empty. */
export function buildQueryString(params?: QueryParams): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    sp.append(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

/** Join base + path without dropping any base path segment (e.g. a reverse-proxy prefix). */
export function buildUrl(
  path: string,
  params?: QueryParams,
  baseUrl: string = getApiBaseUrl(),
): string {
  if (!path.startsWith("/")) throw new Error(`API path must start with "/": "${path}"`);
  return `${normalizeBaseUrl(baseUrl)}${path}${buildQueryString(params)}`;
}

export type ApiGetOptions = {
  params?: QueryParams;
  signal?: AbortSignal;
  baseUrl?: string;
};

function extractMessage(body: unknown, fallback: string): string {
  if (typeof body === "string" && body.trim()) return body.slice(0, 300);
  if (body && typeof body === "object") {
    const obj = body as Record<string, unknown>;
    const d = obj["detail"] ?? obj["message"] ?? obj["error"];
    if (typeof d === "string") return d;
    // FastAPI validation errors: detail: [{ msg, loc }]
    if (Array.isArray(d) && d.length > 0) {
      const first = d[0] as Record<string, unknown> | undefined;
      if (first && typeof first["msg"] === "string") return first["msg"];
    }
  }
  return fallback;
}

async function readBody(res: Response): Promise<unknown> {
  if (res.status === 204 || res.status === 205) return null;
  const text = await res.text();
  if (!text) return null;
  const type = res.headers.get("content-type") ?? "";
  if (type.includes("json")) {
    try {
      return JSON.parse(text) as unknown;
    } catch {
      return text;
    }
  }
  return text;
}

export async function apiGet<T>(path: string, options: ApiGetOptions = {}): Promise<T> {
  const url = buildUrl(path, options.params, options.baseUrl);
  let res: Response;
  try {
    res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: options.signal ?? null,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError({
      message: "Could not reach the backend (network or CORS error).",
      status: 0,
      url,
      detail: err instanceof Error ? err.message : err,
    });
  }

  const requestId = res.headers.get("x-request-id") ?? res.headers.get("x-correlation-id");
  const body = await readBody(res);

  if (!res.ok) {
    throw new ApiError({
      message: extractMessage(body, `Request failed with status ${res.status}`),
      status: res.status,
      url,
      detail: body,
      requestId,
    });
  }
  return body as T;
}
