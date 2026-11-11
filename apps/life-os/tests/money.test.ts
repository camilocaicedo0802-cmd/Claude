import { describe, expect, it } from "vitest";
import { divideFloor, formatMoney, moneyToInput, parseMoney, prorate, sumMinor } from "@/lib/money";

describe("money", () => {
  it("parses Spanish-formatted amounts into integer minor units", () => {
    expect(parseMoney("1.000.000")).toBe(100_000_000);
    expect(parseMoney("$ 1.250.000")).toBe(125_000_000);
    expect(parseMoney("1250000")).toBe(125_000_000);
    expect(parseMoney("1.250,50")).toBe(125_050);
    expect(parseMoney("12.5")).toBe(1_250);
    expect(parseMoney("0,1")).toBe(10);
    expect(parseMoney("abc")).toBeNull();
    expect(parseMoney("")).toBeNull();
    expect(parseMoney("1,2,3")).toBeNull();
  });

  it("adds without floating point drift", () => {
    // 0.1 + 0.2 in major units
    expect(sumMinor([parseMoney("0,1")!, parseMoney("0,2")!])).toBe(30);
    expect(sumMinor(Array.from({ length: 1000 }, () => parseMoney("0,01")!))).toBe(1000);
  });

  it("prorates and divides conservatively", () => {
    expect(prorate(100_000, 1, 3)).toBe(33_333);
    expect(divideFloor(100, 3)).toBe(33);
    expect(divideFloor(100, 0)).toBe(0);
  });

  it("formats COP without decimals and round-trips inputs", () => {
    expect(formatMoney(85_000_000).replace(/\s/g, " ")).toMatch(/\$\s?850\.000/);
    expect(moneyToInput(125_000_000)).toBe("1.250.000");
    expect(parseMoney(moneyToInput(125_000_000))).toBe(125_000_000);
  });
});
