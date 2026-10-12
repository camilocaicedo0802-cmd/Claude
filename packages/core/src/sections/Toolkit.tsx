import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import type { ToolGroup } from "../content/site-content";

const ADOBE: Record<string, string> = { "After Effects": "Ae", "Premiere Pro": "Pr", Photoshop: "Ps", Illustrator: "Ai" };

/** Typographic wall of the software he actually uses, grouped by job. */
export function Toolkit({ groups }: { groups: ToolGroup[] }) {
  return (
    <section id="herramientas" aria-labelledby="herramientas-title" className="py-24 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <SectionHeading
          id="herramientas-title"
          lines={[
            <span key="a">
              My Creative <span className="em text-signal">Toolkit.</span>
            </span>,
          ]}
        />
        <div className={`mt-12 grid gap-px bg-line md:mt-16 ${groups.length > 3 ? "md:grid-cols-2 xl:grid-cols-4" : "md:grid-cols-3"}`}>
          {groups.map((g, gi) => (
            <Reveal key={g.title} delay={gi * 0.08} className="bg-ink p-6 md:p-8">
              <h3 className="text-sm font-medium text-smoke">{g.title}</h3>
              <ul className="mt-6 space-y-3">
                {g.tools.map((t) => (
                  <li key={t.name} className="group flex items-center gap-4">
                    {ADOBE[t.name] ? (
                      <span className="grid size-12 shrink-0 place-items-center border border-signal/60 text-lg font-bold tracking-[-0.02em] text-paper transition-colors duration-200 group-hover:bg-signal">
                        {ADOBE[t.name]}
                      </span>
                    ) : (
                      <span aria-hidden className="grid size-12 shrink-0 place-items-center">
                        <span className="h-px w-5 bg-white/30 transition-[width,background-color] duration-300 group-hover:w-8 group-hover:bg-signal" />
                      </span>
                    )}
                    <span className="text-xl font-semibold tracking-[-0.02em] md:text-2xl">{t.name}</span>
                  </li>
                ))}
              </ul>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
