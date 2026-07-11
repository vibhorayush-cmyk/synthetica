import type { GenerateRequest, GenerateResponse } from "@/types/generation";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function generateDataset(request: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${apiUrl}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, export: "zip" }),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Dataset generation failed. Please try again.");
  }
  return response.json() as Promise<GenerateResponse>;
}
