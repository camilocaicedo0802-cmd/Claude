"use client";
import { motion, useInView, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";
import { useRef } from "react";

interface Props {
  children: ReactNode;
  className?: string;
  delay?: number;
  /** "wipe" opens a mask from the bottom (media), "rise" fades up (text blocks). */
  variant?: "wipe" | "rise";
}

/**
 * Entrance on first view. The wrapper is observed and the inner layer is animated,
 * so a fully clipped mask can still be detected as visible.
 */
export function Reveal({ children, className, delay = 0, variant = "rise" }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.12 });
  const reduced = useReducedMotion();
  const hidden =
    reduced ? { opacity: 0 } : variant === "wipe" ? { clipPath: "inset(100% 0% 0% 0%)" } : { opacity: 0, y: 24 };
  const shown = reduced ? { opacity: 1 } : variant === "wipe" ? { clipPath: "inset(0% 0% 0% 0%)" } : { opacity: 1, y: 0 };
  return (
    <div ref={ref} className={className}>
      <motion.div
        className="h-full"
        initial={hidden}
        animate={inView ? shown : hidden}
        transition={{
          duration: reduced ? 0.15 : variant === "wipe" ? 0.85 : 0.7,
          delay,
          ease: variant === "wipe" ? [0.7, 0, 0.2, 1] : [0.23, 1, 0.32, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}

/** Animated red separator that draws itself when it enters the viewport. */
export function RedRule({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 1 });
  const reduced = useReducedMotion();
  return (
    <div ref={ref} aria-hidden className={`h-px ${className}`}>
      <motion.div
        className="h-px origin-left bg-signal"
        initial={{ scaleX: reduced ? 1 : 0, opacity: reduced ? 0 : 1 }}
        animate={inView ? { scaleX: 1, opacity: 1 } : undefined}
        transition={{ duration: reduced ? 0.15 : 0.9, ease: [0.77, 0, 0.175, 1] }}
      />
    </div>
  );
}
