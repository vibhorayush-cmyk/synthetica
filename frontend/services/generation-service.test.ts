import { afterEach, describe, expect, it, vi } from "vitest";
import { generateDataset } from "@/services/generation-service";

const request = {
  industry: "retail",
  scenario: "none",
  export: "zip",
  configuration: { customers: 1, products: 1, stores: 1, orders: 1 },
  quality: {
    missing_values: 0,
    duplicates: 0,
    outliers: 0,
    invalid_formats: 0,
    referential_noise: 0,
  },
} as const;

describe("generateDataset", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("explains dataset limit validation errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "configuration.orders must not exceed MAX_ORDERS (100000)." }), {
          status: 422,
          headers: { "Content-Type": "application/json" },
        })
      )
    );

    await expect(generateDataset(request)).rejects.toThrow("MAX_ORDERS");
  });

  it("uses FastAPI validation messages for configured limits", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: [{ msg: "Value error, configuration.orders must not exceed MAX_ORDERS (100000)." }],
          }),
          { status: 422, headers: { "Content-Type": "application/json" } }
        )
      )
    );

    await expect(generateDataset(request)).rejects.toThrow("MAX_ORDERS");
  });

  it("explains timeouts and service failures without rendering raw responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("", { status: 504 })));
    await expect(generateDataset(request)).rejects.toThrow("took too long");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("", { status: 500 })));
    await expect(generateDataset(request)).rejects.toThrow("server could not generate");
  });

  it("explains rate limits using the server retry hint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("", { status: 429, headers: { "Retry-After": "60" } }))
    );

    await expect(generateDataset(request)).rejects.toThrow("in 60 seconds");
  });
});
