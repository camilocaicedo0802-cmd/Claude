"use client";
import { motion, useReducedMotion, useScroll, useTransform } from "motion/react";
import { useRef } from "react";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { pieceSrc } from "../content/media";
import { profile, type SiteCopy } from "../content/profile";

export function About({ copy }: { copy: SiteCopy }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], reduced ? ["0%", "0%"] : ["-6%", "6%"]);
  const { portrait } = profile;

  return (
    <section id="sobre-mi" aria-labelledby="sobre-mi-title" className="py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <div className="grid gap-10 md:grid-cols-12 md:gap-x-6 md:gap-y-0">
          {/* Phones: heading, portrait, text. Desktop: portrait on the left spanning both rows. */}
          <div className="md:col-span-6 md:col-start-7 md:row-start-1">
            <SectionHeading
              id="sobre-mi-title"
              lines={[
                <span key="a">Behind the</span>,
                <span key="b" className="em text-signal">
                  Frames.
                </span>,
              ]}
            />
          </div>

          {/* Desktop: the portrait stays in view while the longer text column scrolls past it. */}
          <div ref={ref} className="w-full max-w-[22rem] md:sticky md:top-[calc(var(--nav-h)+2.5rem)] md:col-span-5 md:row-span-2 md:row-start-1 md:max-w-[26rem] md:self-start">
            <Reveal variant="wipe" className="relative overflow-hidden bg-panel">
              <div style={{ aspectRatio: `${portrait.width} / ${portrait.height}` }} className="relative">
                <motion.img
                  src={pieceSrc(portrait.file)}
                  alt={portrait.alt}
                  width={portrait.width}
                  height={portrait.height}
                  loading="lazy"
                  decoding="async"
                  className="absolute inset-x-0 -top-[6%] h-[112%] w-full object-cover"
                  style={{ y }}
                />
              </div>
            </Reveal>
            <p className="mt-4 flex items-center justify-between gap-4 text-sm">
              <span className="font-semibold">{profile.name}</span>
              <span className="text-right text-smoke">{copy.role}</span>
            </p>
          </div>

          <div className="md:col-span-6 md:col-start-7 md:row-start-2">
            <div className="space-y-5 md:mt-10">
              {copy.about.map((p, i) => (
                <Reveal key={i} delay={i * 0.06}>
                  <p className={i === 0 ? "text-lg leading-relaxed text-paper md:text-xl" : "body-copy"}>{p}</p>
                </Reveal>
              ))}
            </div>
            <dl className="mt-12 grid gap-x-8 gap-y-8 border-t border-line pt-10 sm:grid-cols-2">
              {copy.values.map((v, i) => (
                <Reveal key={v.title} delay={i * 0.06}>
                  <dt className="font-semibold">{v.title}</dt>
                  <dd className="mt-2 text-sm leading-relaxed text-fog">{v.text}</dd>
                </Reveal>
              ))}
            </dl>
            <Reveal className="mt-12 border-t border-line pt-10">
              <h3 className="text-sm font-semibold text-signal">Formación</h3>
              <ul className="mt-5 space-y-4">
                {copy.education.map((e) => (
                  <li key={e.title} className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-6">
                    <span className="text-lg font-semibold leading-snug tracking-[-0.01em]">{e.title}</span>
                    <span className="shrink-0 text-sm text-smoke">{e.detail}</span>
                  </li>
                ))}
              </ul>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}
