"use client";
import { motion, useInView, useReducedMotion } from "motion/react";
import type { ElementType, ReactNode } from "react";
import { useRef } from "react";

interface Props {
  lines: ReactNode[];
  as?: ElementType;
  className?: string;
  /** Delay before the first line, seconds. */
  delay?: number;
  /** Animate on mount instead of when scrolled into view. */
  immediate?: boolean;
  id?: string;
}

/**
 * Headline that prints line by line from behind a mask, like titles over picture.
 * Visibility is observed on the heading itself (never clipped), not on the masked lines.
 */
export function RevealText({ lines, as: Tag = "h2", className, delay = 0, immediate = false, id }: Props) {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.4 });
  const reduced = useReducedMotion();
  const show = immediate || inView;
  const hidden = reduced ? { opacity: 0 } : { y: "105%" };
  const shown = reduced ? { opacity: 1 } : { y: "0%" };
  return (
    <Tag ref={ref} className={className} id={id}>
      {lines.map((line, i) => (
        <span key={i} className="line-mask">
          <motion.span
            className="block"
            initial={hidden}
            animate={show ? shown : hidden}
            transition={{ duration: reduced ? 0.15 : 0.75, delay: delay + i * 0.07, ease: [0.23, 1, 0.32, 1] }}
          >
            {line}
          </motion.span>
        </span>
      ))}
    </Tag>
  );
}

/** Small helper: a word in Playfair italic, optionally red. */
export function Em({ children, red = false }: { children: ReactNode; red?: boolean }) {
  return <span className={`em ${red ? "text-signal" : ""}`}>{children}</span>;
}
