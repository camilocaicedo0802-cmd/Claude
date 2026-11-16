"use client";
import { ArrowUpRight, MessageCircle } from "lucide-react";
import { Button } from "../components/Button";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import type { Landing } from "../content/landings";
import { pieceSmallSrc } from "../content/media";
import { whatsappUrl } from "../content/profile";
import { landingHref } from "../lib/paths";

export const landingMessage = "Hola, vi tu portafolio y me gustaría una landing page para mi producto.";

/** The landing's screens stacked inside a phone frame that scrolls on its own. */
export function PhonePreview({ landing, className = "" }: { landing: Landing; className?: string }) {
  return (
    <div className={`relative mx-auto w-[min(100%,300px)] rounded-[2.6rem] border border-white/15 bg-panel p-2.5 shadow-[0_40px_80px_-30px_rgba(0,0,0,0.9)] ${className}`}>
      <div aria-hidden className="absolute left-1/2 top-4 z-10 h-5 w-20 -translate-x-1/2 rounded-full bg-ink" />
      {/* data-lenis-prevent: the page's smooth scroll leaves this inner scroll to the browser. */}
      <div
        data-lenis-prevent
        tabIndex={0}
        role="region"
        aria-label={`Vista previa de la landing ${landing.title}. Desliza dentro de la pantalla para recorrerla.`}
        className="aspect-[9/19.5] overflow-y-auto overscroll-contain rounded-[2.1rem] bg-white [scrollbar-width:none] focus-visible:outline-2 focus-visible:outline-signal [&::-webkit-scrollbar]:hidden"
      >
        {landing.pages.map((p, i) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={p.file}
            src={pieceSmallSrc(p.file)}
            alt={p.alt}
            width={p.width}
            height={p.height}
            loading={i < 2 ? "eager" : "lazy"}
            decoding="async"
            className="block h-auto w-full"
          />
        ))}
      </div>
    </div>
  );
}

/** "Landing pages" section near the end of the home page: one project per landing. */
export function LandingShowcase({ landings }: { landings: Landing[] }) {
  return (
    <section id="landing" aria-labelledby="landing-title" className="py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <SectionHeading
          id="landing-title"
          lines={[
            <span key="a">Diseño de</span>,
            <span key="b" className="em text-signal">
              landing pages.
            </span>,
          ]}
        />
        {landings.map((l) => (
          <div key={l.slug} className="mt-12 grid items-center gap-12 md:mt-16 md:grid-cols-12 md:gap-6">
            <Reveal className="md:col-span-6">
              <p className="text-sm font-medium text-smoke">{l.context}</p>
              <h3 className="mt-3 text-[clamp(1.75rem,3.2vw,2.75rem)] font-bold leading-[1.05] tracking-[-0.03em]">{l.title}</h3>
              <p className="body-copy mt-5 max-w-[60ch]">{l.description}</p>
              <dl className="mt-6 grid grid-cols-2 gap-6 border-t border-line pt-6 text-sm">
                <div>
                  <dt className="text-smoke">Mi rol</dt>
                  <dd className="mt-1">{l.role}</dd>
                </div>
                <div>
                  <dt className="text-smoke">Extensión</dt>
                  <dd className="mt-1">{l.pages.length} pantallas</dd>
                </div>
              </dl>
              <div className="mt-8 flex flex-col gap-3 xs:flex-row xs:flex-wrap">
                <Button href={landingHref(l.slug)} variant="primary" icon={<ArrowUpRight size={16} />}>
                  Ver landing completa
                </Button>
                <Button href={whatsappUrl(landingMessage)} target="_blank" rel="noopener noreferrer" variant="ghost" icon={<MessageCircle size={16} />}>
                  Quiero una landing así
                </Button>
              </div>
            </Reveal>
            <div className="md:col-span-5 md:col-start-8">
              <PhonePreview landing={l} />
              <p className="mt-4 text-center text-xs text-smoke">Desliza dentro de la pantalla para recorrerla</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
