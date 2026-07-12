import type { GenerateRequest, GenerateResponse } from "@/types/generation";
import { getAccessToken } from "@/services/api-client";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ApiValidationIssue = { msg?: string };
type ApiErrorPayload = { detail?: string | ApiValidationIssue[] };

async function responseMessage(response: Response): Promise<string> {
  let detail = "";
  try {
    const payload = (await response.json()) as ApiErrorPayload;
    if (typeof payload.detail === "string") {
      detail = payload.detail;
    } else if (Array.isArray(payload.detail)) {
      detail = payload.detail.find((issue) => typeof issue.msg === "string")?.msg ?? "";
    }
  } catch {
    // A reverse proxy can return a non-JSON response. Use a safe generic message.
  }

  if (response.status === 429) {
    const wait = response.headers.get("Retry-After");
    return `Too many generation requests. Please try again${wait ? ` in ${wait} seconds` : " shortly"}.`;
  }
  if (response.status === 504) {
    return "Generation took too long. Reduce the dataset size and try again.";
  }
  if (response.status === 507) {
    return "The download service is temporarily full. Please try again later.";
  }
  if (response.status === 422) {
    return detail || "Please check the dataset limits and configuration, then try again.";
  }
  if (response.status >= 500) {
    return "The server could not generate your dataset. Please try again later.";
  }
  return detail || "Dataset generation failed. Please try again.";
}

export async function generateDataset(request: GenerateRequest): Promise<GenerateResponse> {
  let response: Response;
  try {
    response = await fetch(`${apiUrl}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}) },
      body: JSON.stringify({ ...request, export: "zip" }),
    });
  } catch {
    throw new Error("Unable to reach the generation service. Check your connection and try again.");
  }

  if (!response.ok) {
    throw new Error(await responseMessage(response));
  }
  return response.json() as Promise<GenerateResponse>;
}
