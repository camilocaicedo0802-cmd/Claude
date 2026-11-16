import type { Metric, SiteId, Tool } from "./types";

/** Reel insights from Instagram screenshots in Canva portfolio 1 (page 4). */
export const reelMetrics: { name: string; metrics: Metric[] }[] = [
  {
    name: "Reel B",
    metrics: [
      { value: 259373, label: "visualizaciones", context: "Instagram Insights", format: "integer" },
      { value: 176620, label: "cuentas alcanzadas", context: "99,7 % no seguidores", format: "integer" },
      { value: 11651, label: "interacciones", context: "8.196 me gusta, 1.866 compartidos, 1.582 guardados", format: "integer" },
      { value: 392, label: "nuevos seguidores", context: "desde el reel", format: "integer" },
    ],
  },
  {
    name: "Reel A",
    metrics: [
      { value: 207283, label: "visualizaciones", context: "Instagram Insights", format: "integer" },
      { value: 129676, label: "cuentas alcanzadas", context: "99,7 % no seguidores", format: "integer" },
      { value: 7214, label: "interacciones", context: "4,8 mil me gusta, 1,2 mil compartidos", format: "integer" },
      { value: 318, label: "nuevos seguidores", context: "desde el reel", format: "integer" },
    ],
  },
];

export const reelTotals = {
  views: 259373 + 207283,
  reach: 176620 + 129676,
  watchTime: "15 días, 14 horas",
};

/** Meta Ads screenshots in Canva portfolio 1 (page 3). Amounts are omitted: the currency is not shown. */
export const campaignMetrics: Metric[] = [
  { value: 278, label: "conversaciones iniciadas", context: "Campaña de interacción, 19 nov al 2 dic", format: "integer" },
  { value: 5747, label: "personas alcanzadas", context: "Misma campaña, frecuencia 1,5", format: "integer" },
  { value: 59, label: "conversaciones iniciadas", context: "Post Feria Esco, 4 al 10 nov", format: "integer" },
];

export interface SkillGroup {
  title: string;
  /** Word rendered in Playfair italic red. */
  emphasis: string;
  summary: string;
  items: string[];
  /** Video slug used as a live example. */
  example?: string;
}

export interface ToolGroup {
  title: string;
  tools: { name: Tool; mark: string }[];
}

export interface ProcessStep {
  title: string;
  text: string;
}

export interface SiteSections {
  hero: {
    /** Line above the headline; the highlight is set in white. */
    eyebrow: { highlight: string; text: string };
    lines: { text: string; em?: boolean; red?: boolean }[][];
    subtitle: string;
    video: string;
    /** Accessible description and on-screen label of the hero video. */
    videoLabel: string;
    videoTag: string;
  };
  skills: SkillGroup[];
  toolkit: ToolGroup[];
  process: ProcessStep[];
}

const toolkit: ToolGroup[] = [
  {
    title: "Edición y diseño",
    tools: [
      { name: "Premiere Pro", mark: "Pr" },
      { name: "After Effects", mark: "Ae" },
      { name: "CapCut", mark: "Cc" },
      { name: "Photoshop", mark: "Ps" },
      { name: "Illustrator", mark: "Ai" },
      { name: "Canva", mark: "Ca" },
    ],
  },
  {
    title: "Generación con IA",
    tools: [
      { name: "Veo 3", mark: "V3" },
      { name: "Google Flow", mark: "Fl" },
      { name: "Google AI Studio", mark: "As" },
      { name: "Midjourney", mark: "Mj" },
    ],
  },
  {
    title: "Voz y texto con IA",
    tools: [
      { name: "ElevenLabs", mark: "11" },
      { name: "ChatGPT", mark: "Gp" },
      { name: "Claude", mark: "Cl" },
    ],
  },
  {
    title: "Pauta y gestión",
    tools: [
      { name: "Google Ads", mark: "Ga" },
      { name: "TikTok Ads", mark: "Tk" },
      { name: "Hootsuite", mark: "Ht" },
      { name: "Notion", mark: "No" },
    ],
  },
];

export const sections: Record<SiteId, SiteSections> = {
  disenador: {
    hero: {
      eyebrow: { highlight: "4 años", text: "de experiencia como editor de video y diseñador" },
      lines: [
        [{ text: "Transformo ideas en" }],
        [{ text: "experiencias", em: true }, { text: " visuales" }],
        [{ text: "que se " }, { text: "sienten.", em: true, red: true }],
      ],
      subtitle: "Edición de video · Motion graphics · Diseño digital · Contenido con IA",
      video: "editor-promo",
      videoLabel: "Video de motion graphics ¿Necesitas editor?, de Juan Camilo Caicedo",
      videoTag: "Motion graphics",
    },
    skills: [
      {
        title: "Edición de",
        emphasis: "video",
        summary: "Montaje con ritmo para contenido corto y largo, de la toma en bruto al video final.",
        items: [
          "Edición de reels y anuncios",
          "Videos de formato largo",
          "Storytelling audiovisual",
          "Ritmo narrativo y transiciones",
          "Subtítulos dinámicos",
          "Corrección de color",
          "Diseño sonoro y limpieza de audio",
        ],
        example: "meb-podcast",
      },
      {
        title: "YouTube y",
        emphasis: "Shorts",
        summary: "Videos completos para YouTube, del guion a la edición, y Shorts recortados de cada episodio.",
        items: [
          "Guiones para YouTube",
          "Voces con IA",
          "Edición de videos largos",
          "Clipping: Shorts a partir de episodios largos",
          "Hooks y retención",
          "Intros, textos animados e imágenes de apoyo",
        ],
        example: "yt-short-01",
      },
      {
        title: "Motion",
        emphasis: "graphics",
        summary: "Tipografía cinética y animación de elementos gráficos con criterio de diseño.",
        items: ["Tipografía cinética", "Motion design 2D", "Animación de elementos gráficos", "Infografías animadas", "Transiciones animadas", "Animación para contenido comercial"],
        example: "tiempo-motion",
      },
      {
        title: "Contenido con",
        emphasis: "IA",
        summary: "Videos, voces, avatares e imágenes generados con IA, con dirección de arte y pensados para vender.",
        items: [
          "Videos con IA para ecommerce",
          "Avatares y creadores UGC con IA",
          "Voces con IA para narración",
          "Anuncios para cada etapa del embudo",
          "Versiones de un anuncio con distintos hooks",
          "Generación y edición de imágenes con IA",
          "Campañas conceptuales 100 % IA",
        ],
        example: "ia-matcha-ugc",
      },
      {
        title: "Diseño",
        emphasis: "visual",
        summary: "Piezas, campañas, landing pages e identidades para redes con dirección visual coherente.",
        items: ["Branding e identidad para redes", "Carruseles y posts", "Flyers y banners", "Landing pages", "Workbooks y material descargable", "Diseño de camisetas", "Mockups y dirección de arte"],
      },
      {
        title: "Redes y",
        emphasis: "pauta",
        summary: "Comunidad, campañas y métricas para que el contenido tenga resultados.",
        items: ["Manejo de comunidades", "Manejo de campañas", "Análisis de métricas", "Optimización de perfiles", "Gestión de 12 a 15 clientes en agencia"],
      },
    ],
    toolkit,
    process: [
      { title: "Descubrimiento", text: "Entiendo la marca, la audiencia y la plataforma donde va a vivir el video o la pieza. Defino qué tiene que pasar cuando alguien la vea." },
      { title: "Dirección creativa", text: "Propongo el enfoque: guion, ritmo, tipografía, referencias y la estructura del montaje o del sistema de piezas." },
      { title: "Edición y motion", text: "Selecciono tomas, corto, animo tipografía y gráficos, limpio el audio y diseño el sonido. Cuando el proyecto lo pide, genero voces, imágenes o escenas con IA." },
      { title: "Ajustes", text: "Corrección de color, ajustes de ritmo y rondas de revisión con tus comentarios." },
      { title: "Entrega final", text: "Exporto en los formatos que necesitas: vertical u horizontal, versiones por plataforma, Shorts y archivos listos para publicar o pautar." },
    ],
  },
};
