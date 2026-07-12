import { apiRequest, clearTokens, storeTokens } from "@/services/api-client";
import type { Tokens, User } from "@/types/auth";

type RegistrationResponse = { user: User; tokens: Tokens; verification_message: string };

export async function login(email: string, password: string): Promise<Tokens> {
  const tokens = await apiRequest<Tokens>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  storeTokens(tokens);
  return tokens;
}

export async function register(fullName: string, email: string, password: string): Promise<User> {
  const response = await apiRequest<RegistrationResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ full_name: fullName, email, password }),
  });
  storeTokens(response.tokens);
  return response.user;
}

export function currentUser() {
  return apiRequest<User>("/users/me");
}

export function updateProfile(payload: { full_name?: string; avatar_url?: string; current_password?: string; password?: string }) {
  return apiRequest<User>("/users/me", { method: "PATCH", body: JSON.stringify(payload) });
}

export async function logout() {
  let refreshToken: string | null = null;
  try { refreshToken = window.localStorage.getItem("synthetica.refresh-token"); } catch { /* no persisted session */ }
  try {
    if (refreshToken) await apiRequest<void>("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
  } finally {
    clearTokens();
  }
}

export function requestPasswordReset(email: string) {
  return apiRequest<{ reset_token: string; message: string }>("/auth/password-reset/request", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}
