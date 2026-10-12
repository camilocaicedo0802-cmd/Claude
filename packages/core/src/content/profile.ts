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
}

export const siteCopy: Record<SiteId, SiteCopy> = {
  editor: {
    id: "editor",
    url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3001",
    title: "Juan Camilo Caicedo | Editor de video y Motion Graphics",
    description:
      "Editor de video freelance y motion designer. Edición de reels, anuncios, contenido para YouTube y motion graphics para marcas, creadores y agencias.",
    keywords: [
      "editor de video profesional",
      "editor de videos freelance",
      "motion graphics",
      "edición de reels",
      "edición de contenido audiovisual",
      "video editor",
    ],
    role: "Editor de video y motion designer",
    about: [
      "Soy Juan Camilo Caicedo, editor de video y motion designer. Hago la postproducción de contenido para redes, marcas y campañas digitales: tomo el material grabado y lo convierto en piezas con ritmo, intención y un acabado que se nota desde el primer segundo.",
      "Vengo del diseño gráfico y del trabajo en agencia, donde he llevado portafolios de 12 a 15 clientes al mismo tiempo. De ahí salen dos hábitos: pensar cada corte según la plataforma y la audiencia, y entregar a tiempo sin bajar el estándar.",
      "Animo tipografía, limpio y diseño el audio, corrijo color y construyo transiciones en After Effects y Premiere Pro, y uso inteligencia artificial para acelerar el proceso sin perder el criterio visual.",
    ],
    values: [
      { title: "Ritmo narrativo", text: "Cada corte tiene una razón: sostener la atención y llevar al mensaje." },
      { title: "Motion con diseño", text: "Tipografía editorial y composición propia, no plantillas genéricas." },
      { title: "Hecho para rendir", text: "Edito sabiendo cómo funcionan los reels, los anuncios y sus métricas." },
      { title: "Flujo con IA", text: "Más velocidad en audio, imagen y versiones, con el mismo estándar." },
    ],
  },
  disenador: {
    id: "disenador",
    url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3002",
    title: "Juan Camilo Caicedo | Diseñador digital y audiovisual",
    description:
      "Diseñador digital y creador audiovisual. Piezas para redes, campañas con IA, identidad visual, edición de video y motion graphics para marcas y agencias.",
    keywords: [
      "diseñador digital",
      "diseñador gráfico freelance",
      "motion graphics",
      "edición de reels",
      "contenido para redes sociales",
      "campañas con inteligencia artificial",
    ],
    role: "Diseñador digital y audiovisual",
    about: [
      "Soy Juan Camilo Caicedo, diseñador digital y creador audiovisual. Diseño piezas, campañas e identidades para redes sociales, y las llevo al movimiento con edición de video y motion graphics.",
      "He trabajado en agencias con portafolios de 12 a 15 clientes al mismo tiempo, gestionando comunidades de marca personal y campañas pagas. Por eso diseño con una pregunta en mente: qué tiene que pasar después de que alguien vea la pieza.",
      "Integro la Suite de Adobe con inteligencia artificial para generar, editar y optimizar contenido, cuidando que cada marca mantenga su coherencia estética y emocional.",
    ],
    values: [
      { title: "Diseño y video", text: "La pieza estática y su versión en movimiento salen de la misma mano." },
      { title: "Estrategia de redes", text: "Contenido, comunidad y pauta pensados como un solo sistema." },
      { title: "IA con criterio", text: "Generación de imágenes y contenido con dirección de arte, no al azar." },
      { title: "Volumen con calidad", text: "Experiencia sosteniendo de 12 a 15 marcas en paralelo." },
    ],
  },
};
