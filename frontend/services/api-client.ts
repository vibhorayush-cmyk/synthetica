const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const tokenKey = "synthetica.access-token";
const refreshKey = "synthetica.refresh-token";

export function getAccessToken() {
  if (typeof window === "undefined") return null;
  try { return window.localStorage.getItem(tokenKey); } catch { return null; }
}

export function storeTokens(tokens: { access_token: string; refresh_token: string }) {
  try {
    window.localStorage.setItem(tokenKey, tokens.access_token);
    window.localStorage.setItem(refreshKey, tokens.refresh_token);
  } catch { throw new Error("Your browser blocked secure session storage."); }
}

export function clearTokens() {
  try { window.localStorage.removeItem(tokenKey); window.localStorage.removeItem(refreshKey); } catch { /* no local session to clear */ }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const send = (token: string | null) => fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  let response = await send(getAccessToken());
  if (response.status === 401 && !path.startsWith("/auth/")) {
    let refreshToken: string | null = null;
    try { refreshToken = window.localStorage.getItem(refreshKey); } catch { /* no refresh token */ }
    if (refreshToken) {
      const refreshed = await fetch(`${apiUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (refreshed.ok) {
        const tokens = await refreshed.json() as { access_token: string; refresh_token: string };
        storeTokens(tokens);
        response = await send(tokens.access_token);
      } else {
        clearTokens();
      }
    }
  }
  if (!response.ok) {
    let message = "Request failed.";
    try {
      const payload = (await response.json()) as { detail?: string };
      message = payload.detail ?? message;
    } catch {
      // Preserve a safe generic failure message for non-JSON gateway responses.
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function authenticatedDownload(url: string) {
  const response = await fetch(url, {
    headers: getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {},
  });
  if (!response.ok) throw new Error("The requested export is no longer available.");
  const objectUrl = URL.createObjectURL(await response.blob());
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = "";
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export { apiUrl };
