// Small API client for the shared IdeaLab backend (same endpoints the website uses).
// Access tokens are kept in memory only by the caller; nothing is written to browser storage.

const BASE_URL: string = import.meta.env.VITE_API_URL || "/api";
const REQUEST_TIMEOUT_MS = 70_000; // backend AI timeout is 60 s

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export interface ChatSource {
  url: string;
  title: string | null;
}

export interface ChatResult {
  content: string;
  sources: ChatSource[];
  conversation_id: string | null;
  ai_available: boolean;
  mode?: string | null;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

interface UserResponse {
  full_name: string;
  role: string | null;
}

function errorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object") {
    const b = body as { error?: { message?: unknown }; message?: unknown; detail?: unknown };
    if (typeof b.error?.message === "string") return b.error.message;
    if (typeof b.message === "string") return b.message;
    if (typeof b.detail === "string") return b.detail;
  }
  return fallback;
}

async function request<T>(
  method: "GET" | "POST",
  path: string,
  options: { body?: unknown; token?: string; signal?: AbortSignal } = {},
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const onCallerAbort = () => controller.abort();
  options.signal?.addEventListener("abort", onCallerAbort);

  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (options.token) headers.Authorization = `Bearer ${options.token}`;

    let response: Response;
    try {
      response = await fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: controller.signal,
      });
    } catch (err) {
      if (options.signal?.aborted) throw err; // cancelled by the user
      if (controller.signal.aborted) throw new ApiError("The request timed out.", 0);
      throw new ApiError("Cannot reach the IdeaLab server. Is the backend running?", 0);
    }

    const text = await response.text();
    let body: unknown = undefined;
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    }
    if (!response.ok) {
      throw new ApiError(errorMessage(body, response.statusText || "Request failed"), response.status);
    }
    return body as T;
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", onCallerAbort);
  }
}

export function sendVoiceMessage(
  message: string,
  conversationId: string | null,
  token: string | null,
  signal: AbortSignal,
  mode?: string | null,
): Promise<ChatResult> {
  return request<ChatResult>("POST", "/ai/chat", {
    body: {
      message,
      conversation_id: conversationId,
      channel: "voice",
      use_search: true,
      mode: mode || undefined,
    },
    token: token ?? undefined,
    signal,
  });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("POST", "/auth/login", { body: { email, password } });
}

export function fetchMe(token: string): Promise<UserResponse> {
  return request<UserResponse>("GET", "/auth/me", { token });
}
