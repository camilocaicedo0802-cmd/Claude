import { ArrowUpRight, Mail } from "lucide-react";
import { Button } from "../components/Button";
import { RevealText } from "../components/RevealText";
import { profile, whatsappUrl } from "../content/profile";
import type { NavLink } from "../components/Nav";

interface Props {
  links: NavLink[];
  otherSite?: { href: string; label: string };
  role: string;
}

export function Contact({ links, otherSite, role }: Props) {
  const year = new Date().getFullYear();
  return (
    <>
      <section id="contacto" aria-labelledby="contacto-title" className="relative overflow-hidden border-t border-line pb-16 pt-16 md:pb-24 md:pt-40">
        <div className="shell">
          <RevealText
            as="h2"
            id="contacto-title"
            className="display max-w-[14ch]"
            lines={[
              <span key="a">Let&apos;s Create</span>,
              <span key="b">Something Worth</span>,
              <span key="c" className="em text-signal">
                Watching.
              </span>,
            ]}
          />
          <div className="mt-10 grid gap-10 md:mt-14 md:grid-cols-12 md:gap-6">
            <p className="text-lg leading-relaxed text-fog md:col-span-6 md:text-xl">
              ¿Tienes una idea, una marca o un proyecto que necesita destacar? Hagamos que cobre vida a través de una edición que conecte, comunique y
              genere impacto.
            </p>
            <div className="flex flex-col items-stretch gap-5 sm:items-start md:col-span-5 md:col-start-8 md:items-end">
              <Button href={whatsappUrl()} target="_blank" rel="noopener noreferrer" size="lg" magnetic className="w-full sm:w-auto" icon={<ArrowUpRight size={22} />}>
                Hablemos por WhatsApp
              </Button>
              <a href={`mailto:${profile.email}`} className="inline-flex items-center gap-2 text-fog underline decoration-white/20 underline-offset-[6px] hover:text-paper hover:decoration-signal">
                <Mail aria-hidden size={16} /> {profile.email}
              </a>
              <p className="text-sm text-smoke tabular">{profile.whatsappDisplay}</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="shell grid gap-10 py-12 md:grid-cols-12 md:gap-6">
          <div className="md:col-span-5">
            <p className="text-2xl font-semibold tracking-[-0.02em]">{profile.name}</p>
            <p className="mt-2 text-sm text-signal">{role}</p>
          </div>
          <nav aria-label="Secciones" className="md:col-span-3">
            <ul className="space-y-2 text-sm">
              {links.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="text-fog hover:text-paper">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <div className="space-y-2 text-sm md:col-span-4">
            {profile.socials.map((s) => (
              <a key={s.href} href={s.href} target="_blank" rel="noopener noreferrer" className="block text-fog hover:text-paper">
                {s.label}
              </a>
            ))}
            {otherSite && (
              <a href={otherSite.href} className="inline-flex items-center gap-1.5 text-paper underline decoration-signal underline-offset-[6px]">
                {otherSite.label} <ArrowUpRight aria-hidden size={14} />
              </a>
            )}
          </div>
        </div>
        <div className="shell flex flex-col gap-2 border-t border-line py-6 text-xs text-smoke sm:flex-row sm:justify-between">
          <p>© {year} {profile.name}. Todo el material es trabajo real de mi portafolio.</p>
          <p>Creatividad. Precisión. Movimiento.</p>
        </div>
      </footer>
    </>
  );
}
