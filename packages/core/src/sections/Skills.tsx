"use client";
import { Plus } from "lucide-react";
import { useState } from "react";
import { RedRule } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { VideoPreview } from "../components/VideoPreview";
import type { SkillGroup } from "../content/site-content";
import { useFinePointer } from "../lib/media-query";

/** Large expanding rows: one discipline at a time, with a live example when there is one. */
export function Skills({ groups }: { groups: SkillGroup[] }) {
  const [open, setOpen] = useState(0);
  const fine = useFinePointer();
  return (
    <section id="habilidades" aria-labelledby="habilidades-title" className="py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <SectionHeading
          id="habilidades-title"
          lines={[
            <span key="a">
              What I Do <span className="em text-signal">Best.</span>
            </span>,
          ]}
        />
        <ul className="mt-12 border-t border-line md:mt-16">
          {groups.map((g, i) => {
            const isOpen = open === i;
            const panelId = `skill-panel-${i}`;
            return (
              <li key={g.title} className="border-b border-line" onPointerEnter={() => fine && setOpen(i)}>
                <h3>
                  <button
                    type="button"
                    aria-expanded={isOpen}
                    aria-controls={panelId}
                    onClick={() => setOpen(i)}
                    className="group flex w-full items-center gap-4 py-6 text-left md:gap-8 md:py-8"
                  >
                    <span className={`text-sm font-semibold tabular transition-colors ${isOpen ? "text-signal" : "text-smoke"}`}>
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span
                      className={`min-w-0 flex-1 text-[clamp(1.75rem,5.2vw,5rem)] font-bold leading-none tracking-[-0.035em] transition-colors duration-300 ${
                        isOpen ? "text-paper" : "text-white/50 group-hover:text-white/75"
                      }`}
                    >
                      {g.title} <span className={`em ${isOpen ? "text-signal" : ""}`}>{g.emphasis}</span>
                    </span>
                    <Plus
                      aria-hidden
                      className={`shrink-0 transition-transform duration-300 ease-[var(--ease-out)] ${isOpen ? "rotate-45 text-signal" : "text-smoke"}`}
                      size={28}
                    />
                  </button>
                </h3>
                <div
                  id={panelId}
                  role="region"
                  aria-label={`${g.title} ${g.emphasis}`}
                  className="grid transition-[grid-template-rows] duration-500 ease-[var(--ease-out)]"
                  style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
                >
                  <div className="overflow-hidden" inert={!isOpen}>
                    <div className="grid gap-8 pb-10 md:grid-cols-12 md:gap-6 md:pb-12 md:pl-[4.25rem]">
                      <div className="md:col-span-7">
                        <p className="max-w-[46ch] text-lg leading-relaxed text-paper">{g.summary}</p>
                        <ul className="mt-6 flex flex-wrap gap-2">
                          {g.items.map((item) => (
                            <li key={item} className="border border-line px-3 py-2 text-sm text-fog">
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                      {g.example && (
                        <div className="w-40 md:col-span-3 md:col-start-10 md:w-auto md:max-w-[220px] md:justify-self-end">
                          <VideoPreview slug={g.example} alt="" active={isOpen} />
                          <p className="mt-2 text-xs text-smoke">Ejemplo real del portafolio</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
