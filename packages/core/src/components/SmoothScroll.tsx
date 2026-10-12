"use client";
import Lenis from "lenis";
import { useEffect } from "react";
import { setLenis } from "../lib/scroll";

/** Lenis smooth scrolling on pointer devices only, never with reduced motion. */
export function SmoothScroll() {
  useEffect(() => {
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (reduced || !fine) return;
    const lenis = new Lenis({ autoRaf: true, anchors: { offset: 0 }, lerp: 0.12, wheelMultiplier: 1 });
    setLenis(lenis);
    return () => {
      setLenis(null);
      lenis.destroy();
    };
  }, []);
  return null;
}
