import type { NavLink } from "@jcc/core/components/Nav";
import { chaptersFor } from "@jcc/core/content/chapters";
import { siteCopy } from "@jcc/core/content/profile";
import { sections } from "@jcc/core/content/site-content";

export const SITE = "disenador" as const;
export const copy = siteCopy[SITE];
export const content = sections[SITE];
/** Every chapter this site shows, in folder order (01 is the most important). */
export const chapters = chaptersFor(SITE);
/** Chapter 01, Motion Graphics, opens the page in its own section. */
export const motionChapter = chapters[0];
/** The rest, shown as Selected Works. */
export const workChapters = chapters.slice(1);

export const links: NavLink[] = [
  { href: "#motion", label: "Motion" },
  { href: "#trabajos", label: "Trabajos" },
  { href: "#sobre-mi", label: "Sobre mí" },
  { href: "#proceso", label: "Proceso" },
  { href: "#contacto", label: "Contacto" },
];

export const otherSite = process.env.NEXT_PUBLIC_OTHER_SITE_URL
  ? { href: process.env.NEXT_PUBLIC_OTHER_SITE_URL, label: "Ver mi portafolio de edición de video" }
  : undefined;
