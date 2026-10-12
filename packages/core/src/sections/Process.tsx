"use client";
import { motion, useScroll, useSpring } from "motion/react";
import { useRef } from "react";
import { RedRule } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import type { ProcessStep } from "../content/site-content";

/** Timeline whose red playhead fills as the visitor scrolls through the five steps. */
export function Process({ steps }: { steps: ProcessStep[] }) {
  const list = useRef<HTMLOListElement>(null);
  const { scrollYProgress } = useScroll({ target: list, offset: ["start 70%", "end 60%"] });
  const fill = useSpring(scrollYProgress, { stiffness: 200, damping: 40 });

  return (
    <section id="proceso" aria-labelledby="proceso-title" className="py-16 md:py-36">
      <div className="shell grid gap-12 md:grid-cols-12 md:gap-6">
        <div className="md:col-span-5">
          <div className="md:sticky md:top-[calc(var(--nav-h)+48px)]">
            <RedRule className="mb-10 md:mb-14" />
            <SectionHeading
              id="proceso-title"
              lines={[
                <span key="a">From Idea</span>,
                <span key="b">
                  to <span className="em text-signal">Impact.</span>
                </span>,
              ]}
            />
            <p className="body-copy mt-8 max-w-[40ch]">
              Un proceso corto y claro para que sepas qué pasa en cada etapa y cuándo recibes tu video.
            </p>
          </div>
        </div>
        <ol ref={list} className="relative md:col-span-6 md:col-start-7">
          <div aria-hidden className="absolute bottom-2 left-[11px] top-2 w-px bg-line">
            <motion.div className="h-full w-full origin-top bg-signal" style={{ scaleY: fill }} />
          </div>
          {steps.map((s, i) => (
            <li key={s.title} className="relative pb-14 pl-12 last:pb-0 md:pb-20">
              <span aria-hidden className="absolute left-[6px] top-2 size-[11px] rounded-full border-2 border-signal bg-ink" />
              <p className="text-sm font-semibold text-signal tabular">{String(i + 1).padStart(2, "0")}</p>
              <h3 className="mt-2 text-[clamp(1.75rem,3vw,2.75rem)] font-bold leading-tight tracking-[-0.03em]">{s.title}</h3>
              <p className="body-copy mt-3">{s.text}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
