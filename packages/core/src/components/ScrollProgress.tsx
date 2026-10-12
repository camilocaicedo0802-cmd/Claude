"use client";
import { motion, useScroll, useSpring } from "motion/react";

/** The red playhead: page progress as a thin line (left edge on desktop, top on mobile). */
export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 220, damping: 40, mass: 0.4 });
  return (
    <>
      <motion.div
        aria-hidden
        className="fixed inset-x-0 top-0 z-[60] h-[2px] origin-left bg-signal md:hidden"
        style={{ scaleX: progress }}
      />
      <div aria-hidden className="fixed left-0 top-0 z-[60] hidden h-full w-[2px] bg-white/[0.06] md:block">
        <motion.div className="h-full w-full origin-top bg-signal" style={{ scaleY: progress }} />
      </div>
    </>
  );
}
