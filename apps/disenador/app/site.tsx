import type { NavLink } from "@jcc/core/components/Nav";
import { siteCopy } from "@jcc/core/content/profile";
import { projectBySlug, projectsFor } from "@jcc/core/content/projects";
import { sections } from "@jcc/core/content/site-content";

export const SITE = "disenador" as const;
export const copy = siteCopy[SITE];
export const content = sections[SITE];
export const projects = projectsFor(SITE);

export const links: NavLink[] = [
  { href: "#piezas", label: "Piezas" },
  { href: "#motion", label: "Motion" },
  { href: "#trabajos", label: "Trabajos" },
  { href: "#sobre-mi", label: "Sobre mí" },
  { href: "#contacto", label: "Contacto" },
];

const bySlug = (slug: string) => projectBySlug(slug)!;

/** Gallery wall in section 02: the strongest graphic work. */
export const featuredTiles = [
  { project: bySlug("coca-cola-freeze"), show: 3, span: "md:col-span-7" },
  { project: bySlug("ordenar-la-comunicacion"), show: 2, span: "md:col-span-5" },
  { project: bySlug("ryhar"), show: 2, span: "md:col-span-5" },
  { project: bySlug("costena-bacana"), show: 2, span: "md:col-span-7" },
];

/** Motion pieces shown in the sticky reel. */
export const motionProjects = ["tu-tiempo", "legado-cr7", "necesitas-editor", "reel-multivitaminico", "sientes-el-llamado", "max-security"].map(bySlug);

/** Real pieces floating beside the hero video. */
export const heroPieces = [bySlug("coca-cola-freeze"), bySlug("ryhar")].map((p) => (p.media.kind === "images" ? p.media.images[0] : null)).filter((x) => x !== null);

export const otherSite = process.env.NEXT_PUBLIC_OTHER_SITE_URL
  ? { href: process.env.NEXT_PUBLIC_OTHER_SITE_URL, label: "Ver mi portafolio de edición de video" }
  : undefined;
