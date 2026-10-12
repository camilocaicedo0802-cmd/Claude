"use client";
import { ArrowUpRight, Menu, X } from "lucide-react";
import { AnimatePresence, motion, useMotionValueEvent, useReducedMotion, useScroll } from "motion/react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { profile, whatsappUrl } from "../content/profile";
import { lockScroll } from "../lib/scroll";

export interface NavLink {
  href: string;
  label: string;
}

interface Props {
  links: NavLink[];
  /** Base path for anchors when rendered outside the home page (case studies). */
  home?: string;
  role: string;
}

export function Nav({ links, home = "", role }: Props) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string | null>(null);
  const reduced = useReducedMotion();
  const { scrollY } = useScroll();
  useMotionValueEvent(scrollY, "change", (v) => setScrolled(v > 24));

  // Active section: the one crossing the upper third of the viewport.
  useEffect(() => {
    if (home) return;
    const ids = links.map((l) => l.href.replace("#", ""));
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) if (entry.isIntersecting) setActive(`#${entry.target.id}`);
      },
      { rootMargin: "-30% 0px -60% 0px" },
    );
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
  }, [links, home]);

  useEffect(() => {
    lockScroll(open);
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-[background-color,border-color] duration-300 ${
        scrolled || open ? "border-b border-line bg-ink" : "border-b border-transparent bg-transparent"
      }`}
    >
      <nav aria-label="Principal" className="shell flex h-[var(--nav-h)] items-center justify-between gap-6">
        <Link href={home || "/"} className="group flex items-baseline gap-3 whitespace-nowrap" aria-label={`${profile.name}, inicio`}>
          <span className="text-[0.95rem] font-semibold tracking-[-0.01em]">
            Juan Camilo <span className="em text-signal">Caicedo</span>
          </span>
          <span className="hidden text-xs text-smoke xl:inline">{role}</span>
        </Link>

        <ul className="hidden items-center gap-8 lg:flex">
          {links.map((link) => (
            <li key={link.href} className="relative">
              <a
                href={`${home}${link.href}`}
                className={`py-2 text-[0.8125rem] font-medium transition-colors duration-200 ${
                  active === link.href ? "text-paper" : "text-fog hover:text-paper"
                }`}
                aria-current={active === link.href ? "true" : undefined}
              >
                {link.label}
              </a>
              {active === link.href && (
                <motion.span
                  layoutId="nav-playhead"
                  className="absolute -bottom-0.5 left-0 right-0 h-[2px] bg-signal"
                  transition={{ type: "spring", duration: 0.4, bounce: 0 }}
                />
              )}
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2">
          <a
            href={whatsappUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="press hidden h-10 items-center gap-2 bg-signal px-4 text-[0.75rem] font-medium uppercase tracking-[0.06em] hover:bg-signal-deep sm:inline-flex"
          >
            Trabajemos juntos <ArrowUpRight aria-hidden size={15} />
          </a>
          <button
            type="button"
            className="press -mr-2 grid size-11 place-items-center lg:hidden"
            aria-label={open ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={open}
            aria-controls="mobile-menu"
            onClick={() => setOpen((o) => !o)}
          >
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            id="mobile-menu"
            className="fixed inset-x-0 bottom-0 top-[var(--nav-h)] flex flex-col justify-between bg-ink px-[var(--gutter)] pb-10 pt-8 lg:hidden"
            initial={reduced ? { opacity: 0 } : { clipPath: "inset(0% 0% 100% 0%)" }}
            animate={reduced ? { opacity: 1 } : { clipPath: "inset(0% 0% 0% 0%)" }}
            exit={reduced ? { opacity: 0 } : { clipPath: "inset(0% 0% 100% 0%)", transition: { duration: 0.25 } }}
            transition={{ duration: 0.45, ease: [0.7, 0, 0.2, 1] }}
          >
            <ul className="space-y-1">
              {links.map((link, i) => (
                <li key={link.href} className="line-mask">
                  <motion.a
                    href={`${home}${link.href}`}
                    onClick={() => setOpen(false)}
                    className="block py-2 text-[2.6rem] font-bold leading-tight tracking-[-0.03em]"
                    initial={reduced ? false : { y: "100%" }}
                    animate={{ y: "0%" }}
                    transition={{ delay: 0.12 + i * 0.05, duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
                  >
                    <span className="mr-3 align-top text-sm font-semibold text-signal tabular">{String(i + 1).padStart(2, "0")}</span>
                    {link.label}
                  </motion.a>
                </li>
              ))}
            </ul>
            <div className="space-y-4">
              <a
                href={whatsappUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="press flex h-14 items-center justify-center gap-2 bg-signal font-medium uppercase tracking-[0.06em]"
              >
                Trabajemos juntos <ArrowUpRight aria-hidden size={18} />
              </a>
              <a href={`mailto:${profile.email}`} className="block text-center text-sm text-fog">
                {profile.email}
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
