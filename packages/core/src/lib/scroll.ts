"use client";
import type Lenis from "lenis";

let instance: Lenis | null = null;

export function setLenis(lenis: Lenis | null) {
  instance = lenis;
}

/** Pause page scrolling (modals, mobile menu). Works with or without Lenis. */
export function lockScroll(locked: boolean) {
  if (instance) {
    if (locked) instance.stop();
    else instance.start();
  }
  document.documentElement.style.overflow = locked ? "hidden" : "";
}

export function scrollToHash(hash: string) {
  const target = document.querySelector(hash);
  if (!target) return;
  if (instance) instance.scrollTo(target as HTMLElement, { offset: 0 });
  else target.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
}
