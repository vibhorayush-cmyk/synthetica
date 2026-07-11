import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DatasetSummary } from "@/components/dataset-summary";

describe("DatasetSummary", () => {
  it("renders an informative empty state", () => {
    render(<DatasetSummary result={null} />);

    expect(
      screen.getByText("Your dataset summary will appear here")
    ).toBeInTheDocument();
  });

  it("renders generated challenge and download actions", () => {
    render(
      <DatasetSummary
        result={{
          download_url: "http://localhost:8000/downloads/sample.zip",
          challenge_pdf_url: "http://localhost:8000/downloads/bundle/challenge.pdf",
          generated_files: ["customers.csv", "challenge.pdf"],
          row_counts: { customers: 10 },
          generated_at: "2026-07-12T10:00:00",
          scenario: "black_friday",
          quality: {
            missing_values: 5,
            duplicates: 0,
            outliers: 0,
            invalid_formats: 0,
            referential_noise: 0,
          },
          challenge_title: "Retail Performance Investigation",
          difficulty: "Intermediate",
          estimated_time: "6–8 hours",
        }}
      />
    );

    expect(screen.getByText("Retail Performance Investigation")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download ZIP" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Download Challenge PDF" })
    ).toBeInTheDocument();
  });
});
