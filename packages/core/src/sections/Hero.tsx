"use client";
import { ArrowDown, ArrowUpRight } from "lucide-react";
import { motion, useReducedMotion, useScroll, useTransform } from "motion/react";
import { useRef } from "react";
import { Button } from "../components/Button";
import { RevealText } from "../components/RevealText";
import { ShowreelPlayer } from "../components/ShowreelPlayer";
import { whatsappUrl } from "../content/profile";
import type { SiteSections } from "../content/site-content";

interface Props {
  hero: SiteSections["hero"];
  /** Extra visual for the designer site: real pieces behind the video. */
  aside?: React.ReactNode;
}

export function Hero({ hero, aside }: Props) {
  const reduced = useReducedMotion();
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const videoY = useTransform(scrollYProgress, [0, 1], ["0%", reduced ? "0%" : "8%"]);

  const lines = hero.lines.map((line, i) => (
    <span key={i}>
      {line.map((part, j) => (
        <span key={j} className={`${part.em ? "em" : ""} ${part.red ? "text-signal" : ""}`}>
          {part.text}
        </span>
      ))}
    </span>
  ));

  return (
    <section ref={ref} id="inicio" aria-label="Presentación" className="relative overflow-hidden pt-[var(--nav-h)]">
      <div className="shell grid items-center gap-8 pb-14 pt-4 md:min-h-[calc(100svh-var(--nav-h))] md:grid-cols-12 md:gap-6 md:pb-16 md:pt-6">
        {/* Video first on phones */}
        <motion.div
          className="relative order-first mx-auto w-full max-w-[min(100%,calc(56svh*0.5625))] md:order-last md:col-span-5 md:col-start-8 md:max-w-[calc(82svh*0.5625)]"
          style={{ y: videoY }}
        >
          {aside}
          <motion.div
            initial={reduced ? { opacity: 0 } : { clipPath: "inset(100% 0% 0% 0%)" }}
            animate={reduced ? { opacity: 1 } : { clipPath: "inset(0% 0% 0% 0%)" }}
            transition={{ duration: reduced ? 0.2 : 0.95, delay: 0.1, ease: [0.7, 0, 0.2, 1] }}
            className="relative"
          >
            <ShowreelPlayer slug={hero.video} label={hero.videoLabel} tag={hero.videoTag} className="w-full" />
          </motion.div>
        </motion.div>

        <div className="md:col-span-7 md:pr-4">
          <RevealText as="h1" lines={lines} immediate delay={0.25} className="display-hero" />
          <motion.p
            className="mt-6 text-[0.9375rem] font-medium text-fog md:mt-8 md:text-base"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.75, duration: 0.6 }}
          >
            {hero.subtitle}
          </motion.p>
          <motion.div
            className="mt-8 flex flex-col gap-3 xs:flex-row md:mt-10"
            initial={reduced ? { opacity: 0 } : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.85, duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
          >
            <Button href="#trabajos" variant="primary" magnetic icon={<ArrowDown size={16} />}>
              Explorar proyectos
            </Button>
            <Button href={whatsappUrl()} target="_blank" rel="noopener noreferrer" variant="ghost" magnetic icon={<ArrowUpRight size={16} />}>
              Trabajemos juntos
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator: a red playhead running down a short track */}
      <div aria-hidden className="pointer-events-none absolute bottom-6 left-1/2 hidden h-12 w-px -translate-x-1/2 overflow-hidden bg-white/15 md:block">
        <span className="absolute inset-x-0 top-0 h-1/2 animate-[playhead_1.8s_var(--ease-in-out)_infinite] bg-signal motion-reduce:hidden" />
      </div>
    </section>
  );
}
