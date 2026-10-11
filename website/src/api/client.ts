const BASE_URL = import.meta.env.VITE_API_URL || "/api";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body: any,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  method: string,
  path: string,
  data?: unknown,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  });

  let body: any;
  const text = await response.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const message = body?.error?.message || body?.message || response.statusText;
    throw new ApiError(message, response.status, body);
  }

  if (!text) {
    return {} as T;
  }
  return body as T;
}

export const api = {
  get: <T>(path: string, token?: string) => apiRequest<T>("GET", path, undefined, token),
  post: <T>(path: string, data: unknown, token?: string) =>
    apiRequest<T>("POST", path, data, token),
  patch: <T>(path: string, data: unknown, token?: string) =>
    apiRequest<T>("PATCH", path, data, token),
  delete: <T>(path: string, token?: string) =>
    apiRequest<T>("DELETE", path, undefined, token),
};
