export class ApiError extends Error {
  constructor(public status: number, public code: string) { super(code); }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const r = await fetch(`/api/v1${path}`, {
    credentials: "include",
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    throw new ApiError(r.status, body.detail ?? "UNKNOWN");
  }
  return r.status === 204 ? (undefined as T) : r.json();
}
