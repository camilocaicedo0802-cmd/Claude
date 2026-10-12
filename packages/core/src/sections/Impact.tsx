import { Counter } from "../components/Counter";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { campaignMetrics, reelMetrics, reelTotals } from "../content/site-content";
import { counts } from "../content/chapters";
import type { Chapter } from "../content/types";

interface Props {
  chapters: Chapter[];
  showCampaigns?: boolean;
}

/** Only numbers from his own Instagram and Meta Ads screenshots, each with its context. */
export function Impact({ chapters, showCampaigns = false }: Props) {
  const clients = new Set(chapters.map((c) => c.client).filter(Boolean)).size;
  const videos = chapters.reduce((n, c) => n + counts(c).videos, 0);
  const pieces = chapters.reduce((n, c) => n + counts(c).pieces, 0);
  const work = [
    { value: videos, label: "videos en este portafolio" },
    ...(pieces > 0 ? [{ value: pieces, label: "piezas gráficas en este portafolio" }] : []),
    { value: clients, label: "marcas y clientes con trabajo publicado aquí" },
  ];

  return (
    <section id="impacto" aria-labelledby="impacto-title" className="py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <SectionHeading
          id="impacto-title"
          lines={[
            <span key="a">Creative Work.</span>,
            <span key="b">
              Real <span className="em text-signal">Impact.</span>
            </span>,
          ]}
        />

        <div className="mt-14 grid gap-10 md:mt-20 md:grid-cols-12 md:gap-6">
          <Reveal className="md:col-span-7">
            <p className="text-[clamp(3.6rem,11vw,10rem)] font-bold leading-[0.9] tracking-[-0.05em]">
              <Counter value={reelTotals.views} />
            </p>
            <p className="mt-5 max-w-[34ch] text-xl leading-snug">
              visualizaciones en dos reels que edité, con <Counter value={reelTotals.reach} className="font-bold text-signal" /> cuentas
              alcanzadas en total.
            </p>
            <p className="mt-3 text-sm text-smoke">Fuente: Instagram Insights, capturas incluidas en mi portafolio.</p>
          </Reveal>

          <div className="grid gap-px self-end bg-line sm:grid-cols-2 md:col-span-5">
            {reelMetrics.map((reel, ri) => (
              <Reveal key={reel.name} delay={ri * 0.08} className="bg-ink p-5 md:p-6">
                <h3 className="text-sm font-semibold text-signal">{reel.name}</h3>
                <ul className="mt-4 space-y-4">
                  {reel.metrics.map((m) => (
                    <li key={m.label}>
                      <p className="text-2xl font-bold tracking-[-0.02em]">
                        <Counter value={m.value} />
                      </p>
                      <p className="text-sm text-fog">{m.label}</p>
                      <p className="text-xs text-smoke">{m.context}</p>
                    </li>
                  ))}
                </ul>
              </Reveal>
            ))}
          </div>
        </div>

        {showCampaigns && (
          <div className="mt-16 border-t border-line pt-10 md:mt-24">
            <h3 className="text-xl font-semibold tracking-[-0.02em]">
              Pauta en Meta Ads <span className="text-smoke font-normal">· como trafficker</span>
            </h3>
            <div className="mt-8 grid gap-8 sm:grid-cols-3">
              {campaignMetrics.map((m, i) => (
                <Reveal key={i} delay={i * 0.06}>
                  <p className="text-5xl font-bold tracking-[-0.03em]">
                    <Counter value={m.value} />
                  </p>
                  <p className="mt-2 text-fog">{m.label}</p>
                  <p className="text-sm text-smoke">{m.context}</p>
                </Reveal>
              ))}
            </div>
          </div>
        )}

        <div className={`mt-16 grid gap-8 border-t border-line pt-10 md:mt-24 ${work.length > 2 ? "grid-cols-2 lg:grid-cols-4" : "sm:grid-cols-3"}`}>
          <h3 className="col-span-full text-sm font-medium text-smoke">Volumen de trabajo</h3>
          {work.map((w) => (
            <Reveal key={w.label}>
              <p className="text-5xl font-bold tracking-[-0.03em]">
                <Counter value={w.value} />
              </p>
              <p className="mt-2 text-fog">{w.label}</p>
            </Reveal>
          ))}
          <Reveal>
            <p className="text-5xl font-bold tracking-[-0.03em] tabular">12-15</p>
            <p className="mt-2 text-fog">clientes atendidos en paralelo en agencia</p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
