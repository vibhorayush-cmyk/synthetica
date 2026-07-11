import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BrandLockup } from "@/components/brand/brand-lockup";

describe("BrandLockup", () => {
  it("renders the Synthetica wordmark and accessible home identity", () => {
    render(<BrandLockup />);
    expect(screen.getByText("Synthetica")).toBeInTheDocument();
    expect(screen.getByText("Realistic data. Real analytical practice.")).toBeInTheDocument();
  });
});
