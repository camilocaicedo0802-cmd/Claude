import type { SiteId } from "./types";

export const profile = {
  name: "Juan Camilo Caicedo",
  shortName: "Camilo Caicedo",
  email: "camilocaicedo0802@gmail.com",
  /** International format, digits only. */
  whatsapp: "573187227063",
  whatsappDisplay: "+57 318 722 7063",
  whatsappMessage: "Hola, vi tu portafolio y me gustaría hablar contigo sobre un proyecto audiovisual.",
  /**
   * Verified social profiles. Empty on purpose: the sources do not include profile URLs.
   * Add entries like { label: "Instagram", href: "https://instagram.com/..." } and they
   * appear in the contact section and footer automatically.
   */
  socials: [] as { label: string; href: string }[],
  portrait: {
    file: "retrato",
    alt: "Retrato en blanco y negro de Juan Camilo Caicedo, de traje oscuro y corbata",
    width: 580,
    height: 592,
  },
};

export function whatsappUrl(message = profile.whatsappMessage) {
  return `https://wa.me/${profile.whatsapp}?text=${encodeURIComponent(message)}`;
}

export interface SiteCopy {
  id: SiteId;
  url: string;
  title: string;
  description: string;
  keywords: string[];
  role: string;
  about: string[];
  values: { title: string; text: string }[];
  /** Degree and courses, shown under "Sobre mí". */
  education: { title: string; detail: string }[];
}

const education = [
  { title: "Profesional en Publicidad y Mercadeo", detail: "Título profesional" },
  { title: "De Jr a Senior: Creatividad e innovación con IA", detail: "Seminario" },
];

export const siteCopy: Record<SiteId, SiteCopy> = {
  disenador: {
    id: "disenador",
    url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3002",
    title: "Juan Camilo Caicedo | Editor de video y diseñador digital",
    description:
      "Editor de video y diseñador digital con 4 años de experiencia. Reels, anuncios, videos y Shorts para YouTube, motion graphics, videos UGC con IA y diseño para marcas, creadores y agencias.",
    keywords: [
      "editor de video",
      "editor de video freelance",
      "edición de reels",
      "edición de videos para YouTube",
      "YouTube Shorts",
      "motion graphics",
      "videos UGC con IA",
      "diseñador digital",
      "contenido para redes sociales",
    ],
    role: "Editor de video y diseñador digital",
    about: [
      "Soy Juan Camilo Caicedo, editor de video y diseñador digital, profesional en Publicidad y Mercadeo y con 4 años de experiencia. Mi trabajo principal es la edición: reels, anuncios, videos y Shorts para YouTube y motion graphics para marcas, creadores y agencias. Tomo el material en bruto y lo convierto en piezas con ritmo, intención y un acabado que se nota desde el primer segundo.",
      "Vengo del diseño gráfico y del trabajo en agencia, donde he llevado portafolios de 12 a 15 clientes al mismo tiempo. De ahí salen dos hábitos: pensar cada corte según la plataforma y la audiencia, y entregar a tiempo sin bajar el estándar. El diseño sigue siendo parte de lo que hago: piezas, campañas e identidades que luego llevo al movimiento.",
      "Animo tipografía, limpio y diseño el audio, corrijo color y construyo transiciones en Premiere Pro y After Effects. Para YouTube escribo el guion, genero las voces con IA, edito el video completo y lo recorto en Shorts. Con Veo 3, Google Flow y Google AI Studio produzco anuncios de ecommerce con avatares y creadores UGC generados con IA. En ese camino me sigo formando: completé el seminario «De Jr a Senior: Creatividad e innovación con IA».",
    ],
    values: [
      { title: "Ritmo narrativo", text: "Cada corte tiene una razón: sostener la atención y llevar al mensaje." },
      { title: "Versatilidad", text: "Me adapto a cada cliente y formato: marcas, creadores, agencias, YouTube y ecommerce." },
      { title: "IA con criterio", text: "Guiones, voces, avatares e imágenes con IA bajo una dirección clara, no al azar." },
      { title: "Volumen con calidad", text: "Experiencia sosteniendo de 12 a 15 marcas en paralelo." },
    ],
    education,
  },
};
