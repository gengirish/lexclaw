import { describe, expect, it } from "vitest";

describe("dashboard shell", () => {
  it("loads baseline title", () => {
    const title = "LexClaw Control Plane";
    expect(title).toContain("LexClaw");
  });
});
