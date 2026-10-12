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

const toolkitEditor: ToolGroup[] = [
  {
    title: "Edición y motion",
    tools: [
      { name: "After Effects", mark: "Ae" },
      { name: "Premiere Pro", mark: "Pr" },
      { name: "CapCut", mark: "Cc" },
    ],
  },
  {
    title: "Diseño",
    tools: [
      { name: "Photoshop", mark: "Ps" },
      { name: "Illustrator", mark: "Ai" },
      { name: "Canva", mark: "Ca" },
    ],
  },
  {
    title: "Audio e IA",
    tools: [
      { name: "ElevenLabs", mark: "11" },
      { name: "Midjourney", mark: "Mj" },
      { name: "ChatGPT", mark: "Gp" },
      { name: "Claude", mark: "Cl" },
    ],
  },
];

const toolkitDesigner: ToolGroup[] = [
  ...toolkitEditor,
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

const process: ProcessStep[] = [
  { title: "Discovery", text: "Entiendo la marca, la audiencia y la plataforma donde va a vivir el video. Defino qué tiene que pasar cuando alguien lo vea." },
  { title: "Creative Direction", text: "Propongo el enfoque: ritmo, tipografía, referencias y estructura del guion visual o del montaje." },
  { title: "Editing & Motion", text: "Selecciono tomas, corto, animo tipografía y gráficos, limpio el audio y diseño el sonido." },
  { title: "Refinement", text: "Corrección de color, ajustes de ritmo y rondas de revisión con tus comentarios." },
  { title: "Final Delivery", text: "Exporto en los formatos que necesitas: vertical u horizontal, versiones por plataforma y archivos listos para pautar." },
];

export const sections: Record<SiteId, SiteSections> = {
  editor: {
    hero: {
      eyebrow: { highlight: "4 años", text: "de experiencia en edición y motion" },
      lines: [
        [{ text: "Transformo ideas en" }],
        [{ text: "experiencias", em: true }, { text: " visuales" }],
        [{ text: "que se " }, { text: "sienten.", em: true, red: true }],
      ],
      subtitle: "Video Editing · Motion Graphics · Visual Storytelling",
      video: "editor-promo",
      videoLabel: "Video de motion graphics ¿Necesitas editor?, de Juan Camilo Caicedo",
      videoTag: "Motion graphics",
    },
    skills: [
      {
        title: "Video",
        emphasis: "Editing",
        summary: "Montaje con ritmo para contenido corto y largo, de la toma en bruto al video final.",
        items: ["Edición profesional", "Storytelling audiovisual", "Contenido corto y largo", "Ritmo narrativo", "Transiciones", "Corrección de color", "Diseño sonoro y limpieza de audio"],
        example: "meb-podcast",
      },
      {
        title: "Motion",
        emphasis: "Graphics",
        summary: "Tipografía cinética y animación de elementos gráficos con criterio de diseño.",
        items: ["Kinetic typography", "Motion design 2D", "Animación de elementos gráficos", "Transiciones animadas", "Animación para contenido comercial", "Composición audiovisual"],
        example: "tiempo-motion",
      },
      {
        title: "Content",
        emphasis: "Creation",
        summary: "Piezas pensadas para cada plataforma y para el comportamiento de su audiencia.",
        items: ["Reels", "TikTok", "YouTube (intro, outro, infografías)", "Video ads", "Contenido corporativo", "Formatos verticales y horizontales"],
        example: "alanna-coming-soon",
      },
      {
        title: "Workflow &",
        emphasis: "IA",
        summary: "Procesos ordenados y herramientas de IA para entregar más rápido sin perder calidad.",
        items: ["Organización de material", "Adaptación multiplataforma", "Optimización de formatos", "Consistencia visual entre piezas", "Exportación profesional", "Generación y edición con IA"],
        example: "beleza-dia-01",
      },
    ],
    toolkit: toolkitEditor,
    process,
  },
  disenador: {
    hero: {
      eyebrow: { highlight: "4 años", text: "de experiencia como diseñador y editor" },
      lines: [
        [{ text: "Diseño que detiene" }],
        [{ text: "el " }, { text: "scroll", em: true, red: true }, { text: " y se pone" }],
        [{ text: "en " }, { text: "movimiento.", em: true }],
      ],
      subtitle: "Diseño digital · Motion Graphics · Contenido con IA",
      video: "editor-promo",
      videoLabel: "Video de motion graphics ¿Necesitas editor?, de Juan Camilo Caicedo",
      videoTag: "Motion graphics",
    },
    skills: [
      {
        title: "Diseño",
        emphasis: "visual",
        summary: "Piezas, campañas e identidades para redes con dirección visual coherente.",
        items: ["Branding e identidad para redes", "Carruseles y posts", "Flyers y banners", "Diseño de camisetas", "Mockups", "Dirección de arte"],
      },
      {
        title: "Motion &",
        emphasis: "video",
        summary: "La pieza estática pasa a movimiento: edición, tipografía cinética y reels.",
        items: ["Motion graphics", "Edición de reels", "Subtítulos dinámicos", "Diseño sonoro", "Corrección de color"],
        example: "cr7-legado",
      },
      {
        title: "Contenido con",
        emphasis: "IA",
        summary: "Imágenes, audio y contenido generados con IA bajo una dirección de arte clara.",
        items: ["Generación y edición de imágenes con IA", "Creación de contenido con IA", "Edición de audios con IA", "Campañas conceptuales 100 % IA"],
      },
      {
        title: "Redes y",
        emphasis: "pauta",
        summary: "Comunidad, campañas y métricas para que el contenido tenga resultados.",
        items: ["Manejo de comunidades", "Manejo de campañas", "Análisis de métricas", "Optimización de perfiles", "Gestión de 12 a 15 clientes en agencia"],
      },
    ],
    toolkit: toolkitDesigner,
    process: [
      { title: "Discovery", text: "Entiendo la marca, su audiencia y el objetivo de la pieza o campaña: vender, educar, invitar o posicionar." },
      { title: "Creative Direction", text: "Defino la línea visual: paleta, tipografía, referencias y el sistema de piezas que necesita la campaña." },
      { title: "Design & Motion", text: "Diseño las piezas, genero imágenes con IA cuando aporta y las llevo a video o motion si el formato lo pide." },
      { title: "Refinement", text: "Ajustes con tus comentarios y adaptación a cada formato y plataforma." },
      { title: "Final Delivery", text: "Entrego archivos listos para publicar o pautar, y si lo necesitas, acompaño la medición de resultados." },
    ],
  },
};
