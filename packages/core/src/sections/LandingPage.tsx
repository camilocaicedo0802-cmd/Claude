"use client";
import { ArrowLeft, MessageCircle } from "lucide-react";
import { Button } from "../components/Button";
import { RevealText } from "../components/RevealText";
import { SiteLink } from "../components/SiteLink";
import type { Landing } from "../content/landings";
import { pieceSmallSrc, pieceSrc } from "../content/media";
import { whatsappUrl } from "../content/profile";
import { homeHref } from "../lib/paths";
import { landingMessage } from "./LandingShowcase";

/** A landing page at full length, as it reads on a phone: its screens stacked in one column. */
export function LandingPage({ landing }: { landing: Landing }) {
  return (
    <article className="pt-[var(--nav-h)]">
      <div className="shell pb-10 pt-10 md:pb-14 md:pt-16">
        <SiteLink href={homeHref("#landing")} className="inline-flex items-center gap-2 text-sm text-fog hover:text-paper">
          <ArrowLeft aria-hidden size={16} /> Volver al portafolio
        </SiteLink>
        <p className="mt-10 text-sm font-medium text-smoke">{landing.context}</p>
        <RevealText as="h1" immediate className="display mt-5 max-w-[16ch]" lines={[landing.title]} />
        <p className="body-copy mt-6 max-w-[65ch] text-lg">{landing.description}</p>
      </div>

      <div className="mx-auto w-full max-w-[480px] px-[var(--gutter)] sm:px-0">
        <div className="overflow-hidden rounded-2xl bg-white shadow-[0_40px_80px_-30px_rgba(0,0,0,0.9)]">
          {landing.pages.map((p, i) => {
            const small = Math.round((p.width * 720) / p.height);
            return (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={p.file}
                src={pieceSrc(p.file)}
                srcSet={`${pieceSmallSrc(p.file)} ${small}w, ${pieceSrc(p.file)} ${p.width}w`}
                sizes="(min-width: 640px) 480px, 100vw"
                alt={p.alt}
                width={p.width}
                height={p.height}
                loading={i < 2 ? "eager" : "lazy"}
                decoding="async"
                className="block h-auto w-full"
              />
            );
          })}
        </div>
      </div>

      <div className="shell mt-16 flex flex-col items-start gap-6 border-t border-line pt-10 md:mt-24 md:flex-row md:items-center md:justify-between">
        <p className="max-w-[40ch] text-2xl font-semibold leading-tight tracking-[-0.02em] md:text-3xl">¿Quieres una landing así para tu producto?</p>
        <Button href={whatsappUrl(landingMessage)} target="_blank" rel="noopener noreferrer" size="lg" icon={<MessageCircle size={20} />}>
          Hablemos por WhatsApp
        </Button>
      </div>
    </article>
  );
}
