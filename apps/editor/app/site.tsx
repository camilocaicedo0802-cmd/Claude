import type { NavLink } from "@jcc/core/components/Nav";
import { siteCopy } from "@jcc/core/content/profile";
import { projectBySlug, projectsFor } from "@jcc/core/content/projects";
import { sections } from "@jcc/core/content/site-content";

export const SITE = "editor" as const;
export const copy = siteCopy[SITE];
export const content = sections[SITE];
export const projects = projectsFor(SITE);

export const links: NavLink[] = [
  { href: "#motion", label: "Motion" },
  { href: "#trabajos", label: "Trabajos" },
  { href: "#sobre-mi", label: "Sobre mí" },
  { href: "#proceso", label: "Proceso" },
  { href: "#contacto", label: "Contacto" },
];

/** Strongest motion pieces, in the order they appear in section 02. */
export const motionProjects = [
  "tu-tiempo",
  "necesitas-editor",
  "legado-cr7",
  "reel-multivitaminico",
  "highline-coming-soon",
  "boxarome",
  "max-security",
].map((slug) => projectBySlug(slug)!);

export const otherSite = process.env.NEXT_PUBLIC_OTHER_SITE_URL
  ? { href: process.env.NEXT_PUBLIC_OTHER_SITE_URL, label: "Ver mi portafolio de diseño" }
  : undefined;
