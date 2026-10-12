import pieces from "../../../../media/out/pieces.json";
import type { Chapter, Entry, ImageAsset, ImageItem, MediaItem, SiteId, VideoItem } from "./types";

const dims = pieces as Record<string, number[]>;

function img(file: string, alt: string): ImageAsset {
  const size = dims[file];
  if (!size) throw new Error(`Unknown image "${file}" in media/out/pieces. Add it to media/selection.json and run npm run media:build.`);
  return { file, alt, width: size[0], height: size[1] };
}

const video = (slug: string, title: string, description?: string, longForm?: VideoItem["longForm"]): VideoItem => ({
  kind: "video",
  video: slug,
  title,
  description,
  longForm,
});
const piece = (file: string, title: string, alt: string): ImageItem => ({ kind: "image", image: img(file, alt), title });

const AE_PR = ["After Effects", "Premiere Pro"] as const;
const DRIVE = "Drive: Videos y Piezas para portafolio";

/**
 * Every chapter of the portfolio, in the order of the numbered Drive folders.
 * Lower number = more important. The editor site shows only the videos of each chapter;
 * the designer site shows videos and pieces.
 */
export const chapters: Chapter[] = [
  {
    slug: "motion-graphics",
    number: 1,
    title: "Motion Graphics",
    context: "Piezas propias de motion",
    categories: ["Motion Graphics"],
    description:
      "Tres piezas verticales de concepto propio: tipografía cinética, recortes, mockups y transiciones que siguen el ritmo del audio. Es el trabajo que mejor muestra mi lenguaje visual.",
    role: "Concepto, guion visual, edición y motion graphics",
    tools: [...AE_PR],
    source: `${DRIVE} / 1. Motion Graphics`,
    items: [
      video(
        "editor-promo",
        "¿Necesitas editor?",
        "Anuncio vertical de mis servicios de edición: una interfaz de timeline animada, mockups de celular y tipografía que cuenta la propuesta en 30 segundos, de la idea al impacto.",
      ),
      video(
        "cr7-legado",
        "Legado CR7",
        "La carrera de Cristiano Ronaldo en 30 segundos: de una pequeña isla a Manchester, la ambición, los títulos y la camiseta 7, con recortes, gráficas y tipografía animada sobre blanco.",
      ),
      video(
        "tiempo-motion",
        "Tu tiempo",
        "Pieza en blanco y negro sobre el valor del tiempo. Relojes de arena, bustos clásicos y un celular que se come las horas, con tipografía cinética que alterna sans y caligrafía.",
      ),
    ],
    caseStudy: {
      objective: "Demostrar control de tipografía cinética, composición y ritmo en piezas verticales de 30 a 43 segundos.",
      solution:
        "Cada pieza tiene su propio recurso gráfico (timeline y mockups, mapa y collage de títulos, objetos recortados en blanco y negro) unido por tipografía animada y transiciones con máscaras.",
      process: ["Guion visual frase por frase", "Composición de cada escena en 9:16", "Animación de tipografía y objetos", "Sincronización con el audio y diseño sonoro"],
      resources: ["After Effects", "Premiere Pro"],
    },
  },
  {
    slug: "maria-elena-badillo",
    number: 2,
    title: "María Elena Badillo",
    client: "María Elena Badillo",
    context: "Psicóloga, autora, empresaria y guía",
    categories: ["Video Editing", "Reels & Short Form", "Motion Graphics"],
    description:
      "María Elena Badillo es psicóloga, autora y empresaria, y su canal de YouTube reúne 1,3 millones de suscriptores. Para su marca personal edito reels a partir de conversaciones a cámara, clips de su podcast y momentos de su día a día, con subtítulos que resaltan cada idea clave, tipografía que acompaña su voz y un ritmo pensado para que el mensaje llegue completo. Su canal también me contactó para editar uno de sus episodios: corte y mezcla de tomas, limpieza de audio, animaciones de texto e infografías, intro y outro.",
    role: "Edición de reels y de un episodio para YouTube, subtítulos y motion graphics",
    tools: [],
    source: `${DRIVE} / 2. Maria Elena Badillo`,
    items: [
      video("meb-proposito", "Tu propósito no es empezar de cero"),
      video("meb-podcast", "Clip de podcast"),
      video("meb-vacaciones", "Vacaciones para encontrarte"),
      video("meb-cobrar", "Cobrar lo que realmente vales"),
      video("meb-domingo", "Un domingo real"),
      video("meb-reflexion", "Conversación al aire libre"),
      video(
        "meb-youtube",
        "Cómo volver a levantarte cuando sientes que todo se derrumbó",
        "Episodio completo de 38 minutos para su canal: adelanto de apertura, título animado, rótulo de presentación, cortes entre dos planos de cámara, palabras clave en pantalla, imágenes de apoyo y pantalla final de suscripción.",
        { platform: "YouTube" },
      ),
    ],
  },
  {
    slug: "ryhar",
    number: 3,
    title: "Ryhar",
    client: "Ryhar",
    context: "Marca de ropa con diseños personalizados",
    categories: ["Visual Design", "Social Media", "Commercial Ads"],
    description:
      "Camisetas pensadas como piezas de colección, inspiradas en artistas como Feid, Ryan Castro, Mac Miller, Rels B, Travis Scott y Héctor Lavoe, posts e historias de lanzamiento, y videos cortos de producto y nuevos drops.",
    role: "Diseño de camisetas y piezas, edición de video",
    tools: [],
    source: `${DRIVE} / 3. Ryhar`,
    items: [
      piece("ryhar-01", "Feid vs Ferxxo", "Diseño de camiseta Feid vs Ferxxo con Feid de gorra blanca entre flores y tipografía verde"),
      piece("ryhar-02", "Merch Feid", "Diseño Merch Feid: El club de las 19 flores, con camisetas y un auto entre plantas en tonos verdes"),
      piece("ryhar-03", "Mac Miller", "Diseño de camiseta Mac Miller con retrato sobre fondo de ondas rosadas y la frase Congratulations"),
      piece("ryhar-04", "Crudo Means Raw", "Diseño de camiseta Crudo Means Raw en negro con tipografía roja y blanca"),
      piece("ryhar-05", "Ryan Castro", "Diseño de camiseta Ryan Castro, El cantante del ghetto, con grafiti rojo sobre negro"),
      piece("ryhar-06", "Rels B", "Diseño de camiseta Rels B, Boys Don't Cry, con tipografía dorada repetida"),
      piece("ryhar-07", "Skinny Flakk", "Diseño de camiseta Skinny Flakk, A New Star, con retrato en blanco y negro y texto rojo vertical"),
      piece("ryhar-08", "Feid Ferxxo, negro", "Diseño de camiseta Feid Ferxxo en tipografía metálica y verde sobre negro"),
      piece("ryhar-09", "Feid Ferxxo, blanco", "Diseño de camiseta Feid Ferxxo con ilustración de Feid en verde sobre blanco"),
      piece("ryhar-10", "Héctor Lavoe", "Diseño de camiseta Héctor Lavoe, El cantante, con tipografía roja repetida"),
      piece("ryhar-11", "Travis Scott", "Diseño de camiseta Travis Scott, Circus Maximus 2024, con retrato y tipografía condensada"),
      piece("ryhar-sende", "Post de lanzamiento: Sende", "Post de lanzamiento Sende de Ryan Castro con tipografía en llamas"),
      piece("ryhar-setlist", "Historia: Posible setlist", "Historia Posible Setlist Awooween con Ryan Castro sobre fondo rojo"),
      piece("ryhar-deadpool", "Historia: Mañana", "Historia de Ryhar con Deadpool y Wolverine anunciando nuevos diseños"),
      video("ryhar-new-drop", "New drop: Ryan Castro"),
      video("ryhar-outfit", "Outfit BTS"),
      video("ryhar-coleccion", "Nueva colección"),
      video("ryhar-volvemos", "Volvemos"),
    ],
  },
  {
    slug: "beleza",
    number: 4,
    title: "Beleza",
    client: "Beleza",
    context: "Reto 21 días: guía de uso de producto",
    categories: ["Video Editing", "Motion Graphics", "Commercial Ads"],
    description:
      "Serie de videos para el Reto 21 días: una guía diaria de uso del producto con tarjetas animadas, cronómetros, pasos numerados, siluetas que marcan la zona de trabajo y títulos tipográficos, más tres videos complementarios de funcionamiento y preparación.",
    role: "Edición y motion graphics",
    tools: [],
    source: `${DRIVE} / 4. Beleza`,
    items: [
      ...Array.from({ length: 10 }, (_, i) => video(`beleza-dia-${String(i + 1).padStart(2, "0")}`, `Reto 21 días · ${String(i + 1).padStart(2, "0")}`)),
      video("beleza-funciona", "Cómo funciona el producto"),
      video("beleza-abdomen", "Preparación: abdomen"),
      video("beleza-piernas", "Preparación: piernas"),
    ],
  },
  {
    slug: "konexion-academica",
    number: 5,
    title: "Konexión Académica",
    client: "Konexión Académica",
    context: "Carruseles y reels con apoyo de IA",
    categories: ["Social Media", "Campañas con IA", "Video Editing"],
    description:
      "Tres carruseles educativos: la dopamina digital, el síndrome del impostor académico y la rutina que nos estanca. Combinan diseño estratégico e inteligencia artificial para el contenido, las imágenes y los gráficos de apoyo. Se suma un reel hablado con subtítulos dinámicos.",
    role: "Diseño de carruseles, contenido con IA y edición",
    tools: [],
    source: `${DRIVE} / 5. Konexión Académica`,
    items: [
      piece("konexion-01", "Dopamina digital · 1", "Portada del carrusel Dopamina digital con Deadpool mirando el celular sobre fondo rojo"),
      piece("konexion-02", "Dopamina digital · 2", "Slide: desbloqueas tu celular más de 96 veces al día, con un cerebro dentro de un celular"),
      piece("konexion-03", "Dopamina digital · 3", "Slide: desintoxícate conscientemente, con una lista de hábitos activados"),
      piece("konexion-04", "Dopamina digital · 4", "Slide: desconéctate para reconectar, con Deadpool en un sofá"),
      piece("konexion-05", "Síndrome del impostor · 1", "Portada: el síndrome del impostor académico, con piezas de ajedrez"),
      piece("konexion-06", "Síndrome del impostor · 2", "Slide con dados y el texto: sacas buenas notas y aun así sientes que no mereces estar ahí"),
      piece("konexion-07", "Síndrome del impostor · 3", "Slide: no es suerte, es esfuerzo, constancia y proceso, sobre un calendario"),
      piece("konexion-08", "Síndrome del impostor · 4", "Slide: dudar no te hace impostor, te hace humano"),
      piece("konexion-09", "Síndrome del impostor · 5", "Slide: no eres un fraude, solo estás aprendiendo a creértela"),
      piece("konexion-10", "Morimos lentamente · 1", "Portada: morimos lentamente sentados, no por edad sino por rutina"),
      piece("konexion-11", "Morimos lentamente · 2", "Slide con un reloj derretido: morimos un poco cada día que repetimos el mismo trabajo"),
      piece("konexion-12", "Morimos lentamente · 3", "Slide con un cerebro bombillo: morimos cuando dejamos que el cansancio gane"),
      piece("konexion-13", "Morimos lentamente · 4", "Slide con un despertador: pero también podemos renacer"),
      piece("konexion-14", "Morimos lentamente · 5", "Cierre: estudiar no es volver al pasado, con un libro abierto"),
      video(
        "konexion-reel",
        "Orientación profesional",
        "Reel hablado con subtítulos dinámicos, palabras clave resaltadas, recorte de la presentadora sobre el fondo y transiciones al ritmo de la voz.",
      ),
    ],
  },
  {
    slug: "mente-nueva-marketing",
    number: 6,
    title: "Mente Nueva Marketing",
    client: "Mente Nueva Marketing",
    context: "Agencia, de 12 a 15 clientes en paralelo",
    categories: ["Social Media", "Visual Design", "Video Editing"],
    description:
      "Desde la agencia diseñé flyers, banners y piezas para redes de iglesias y organizaciones como Príncipe de Paz, Iglesia Palabra Viva, Amor y Fe y Visión de Fe, y edité reels de eventos e invitaciones para Evangel Chapel, Global University of Theology y C.C.V.E, cumpliendo los objetivos y tiempos de entrega de cada cliente.",
    role: "Diseño de piezas, edición y motion graphics",
    tools: [],
    source: `${DRIVE} / 6. Mente Nueva Marketing`,
    items: [
      piece("mnm-banner", "Banner: Sin Fronteras", "Banner Sin Fronteras para la reunión de jóvenes de los jueves"),
      piece("mnm-jovenes", "Última reunión de jóvenes", "Flyer Última reunión de jóvenes con fotos de un grupo cantando y tocando guitarra"),
      piece("mnm-family", "Family Celebration", "Historia Family Celebration de Príncipe de Paz en negro y dorado con horarios del domingo"),
      piece("mnm-bendicion", "Servicio de bendición", "Flyer Servicio de bendición de Amor y Fe Miami con tipografía caligráfica turquesa"),
      piece("mnm-ensenanza", "Enseñanza en vivo", "Historia Enseñanza en vivo con horarios de viernes y domingo"),
      piece("mnm-cafe-mujeres", "Café de mujeres", "Flyer Café de mujeres, edición de San Valentín, de Visión de Fe con corazones rojos"),
      piece("mnm-ayuno", "Ayuno y oración", "Post Ayuno y oración de Príncipe de Paz en naranja y blanco"),
      piece("mnm-avivamiento", "Reunión de avivamiento", "Post Reunión de avivamiento de Príncipe de Paz con transmisión en vivo"),
      piece("mnm-retiro-mujeres", "Retiro de mujeres", "Post Retiro de mujeres con mujeres caminando en un campo"),
      piece("mnm-discipulado", "Discipulado para todos", "Post Discipulado para todos de Príncipe de Paz"),
      piece("mnm-escuela-dominical", "Escuela dominical", "Post Escuela dominical de Iglesia Palabra Viva con transmisión por Facebook"),
      piece("mnm-estudio-biblico", "Estudio bíblico", "Post Estudio bíblico de Iglesia Palabra Viva con un hombre leyendo y tomando café"),
      piece("mnm-estudio-biblico-2", "Estudio bíblico, versión grupal", "Post Estudio bíblico con un grupo leyendo la Biblia"),
      piece("mnm-lunes-oracion", "Lunes de oración", "Post Lunes de oración con manos sobre una Biblia en tonos verde azulado"),
      video(
        "mnm-evangel-retiro",
        "Retiro de servidores 2024 · Evangel Chapel",
        "Resumen del retiro: selección de momentos, alabanza y enseñanza montados en 45 segundos, con título tipográfico y cierre con redes.",
      ),
      video("mnm-theology", "La teología te enseña · Global University of Theology", "Tipografía cinética sobre material de archivo: la frase se arma palabra por palabra y cierra con los canales de contacto de la universidad."),
      video("mnm-ccve", "Invitación semanal · C.C.V.E"),
      video("mnm-evangel-servicio", "Retiro de líderes · Evangel Chapel", "Resumen de nueve segundos en pantalla dividida: alabanza, oración y comunidad del retiro de líderes."),
    ],
  },
  {
    slug: "gmedia",
    number: 7,
    title: "gmedia",
    client: "gmedia",
    context: "Carrusel para redes",
    categories: ["Social Media", "Visual Design"],
    description:
      "Carrusel de cinco slides sobre coherencia de marca: azul saturado, recortes de papel, objetos retro y una jerarquía tipográfica que guía la lectura slide por slide.",
    role: "Diseño del carrusel",
    tools: [],
    source: `${DRIVE} / 7. Gmedia`,
    items: [
      piece("gmedia-05", "Portada", "Portada del carrusel: 3 señales de que tu marca necesita ordenar su comunicación"),
      piece("gmedia-01", "Señal 1", "Slide 1: cada pieza parece de una marca distinta"),
      piece("gmedia-02", "Señal 2", "Slide 2: publicas, pero el mensaje cambia todo el tiempo"),
      piece("gmedia-03", "Señal 3", "Slide 3: el contenido se ve bien, pero no guía a ninguna acción"),
      piece("gmedia-04", "Cierre", "Cierre: ordenar la comunicación también es estrategia"),
    ],
  },
  {
    slug: "cmi",
    number: 8,
    title: "CMI",
    client: "CMI Equipamiento Equino",
    context: "Anuncios para un jaquimón personalizado",
    categories: ["Commercial Ads", "Social Media", "Visual Design"],
    description:
      "Siete anuncios verticales para vender un jaquimón ajustable y personalizado con el nombre de cada caballo: titulares de impacto, beneficios, reseñas de clientes y llamados a pedirlo por WhatsApp.",
    role: "Diseño de anuncios",
    tools: [],
    source: `${DRIVE} / 8. CMI`,
    items: [
      piece("cmi-01", "Menos tensión, mejor manejo", "Anuncio Menos tensión, mejor manejo, con un caballo castaño y jaquimón negro"),
      piece("cmi-02", "Un momento tranquilo", "Anuncio Un momento tranquilo junto a tu caballo, con una mujer y un caballo de jaquimón rojo"),
      piece("cmi-03", "Trabajos de piso", "Anuncio Guía tu caballo con trabajos de piso, con jaquimón fucsia"),
      piece("cmi-04", "Libertad", "Anuncio Trabajos desde el piso, con un jinete guiando un caballo en un corral"),
      piece("cmi-05", "Uno con el nombre de cada caballo", "Anuncio naranja con reseñas de clientes y jaquimones de colores personalizados"),
      piece("cmi-06", "Siempre a la mano", "Historia con la reseña Siempre a la mano para el trabajo con mis caballos"),
      piece("cmi-07", "Cómodo y muy fácil de ajustar", "Anuncio con reseña de cliente de cinco estrellas sobre un caballo blanco"),
    ],
  },
  {
    slug: "poolex",
    number: 9,
    title: "Poolex",
    client: "Poolex",
    context: "Comunidad de educación financiera",
    categories: ["Social Media", "Visual Design", "Video Editing"],
    description:
      "Gestión de marca con enfoque en coherencia comunicativa y fidelización: piezas para cursos, eventos y contenido educativo de mercados, una agenda diaria animada y la pieza horizontal de dos minutos que abre sus llamadas corporativas.",
    role: "Community management, diseño y edición",
    tools: [],
    source: `${DRIVE} / 9. Poolex`,
    items: [
      piece("poolex-banner", "Curso de finanzas personales", "Banner del curso Finanzas personales, módulo básico, en morado y verde"),
      piece("poolex-peru", "Viaje a Perú", "Post Participa por un viaje a Perú como protagonista"),
      piece("poolex-nueva-york", "Opciones en Nueva York", "Post Opciones en el mercado de valores de Nueva York con un portátil y divisas"),
      piece("poolex-persuasion", "Técnicas de persuasión", "Post Técnicas efectivas de persuasión con un imán 3D"),
      piece("poolex-acciones", "Opciones en acciones", "Post Opciones en acciones: la nueva era económica ha llegado, con toro y oso"),
      piece("poolex-crowdfunding", "Crowdfunding", "Post Crowdfunding: inversiones que cambian vidas"),
      piece("poolex-trading", "Consejos de trading", "Post Consejos para alcanzar el éxito en el trading"),
      video(
        "poolex-corporativo",
        "Inicio de llamadas corporativas",
        "Pieza horizontal para abrir las llamadas corporativas: campañas, lives, crowdfunding y el equipo, en banners animados.",
      ),
      video("poolex-agenda", "Agenda diaria"),
    ],
  },
  {
    slug: "common-room",
    number: 10,
    title: "Common Room",
    client: "Common Room",
    context: "Moda y joyería: Alanna y Luisa López",
    categories: ["Motion Graphics", "Commercial Ads", "Reels & Short Form"],
    description:
      "Reels animados para marcas de moda y joyería: el teaser de la colección Highline FW/2024 de Alanna con las fotos dentro de las letras, un lookbook en grilla que se recompone y un carrusel de joyería para Luisa López.",
    role: "Edición y motion graphics",
    tools: [],
    year: 2024,
    source: `${DRIVE} / 10. Common Room`,
    items: [
      video("alanna-coming-soon", "Alanna · Highline: coming soon"),
      video("alanna-lookbook", "Alanna · Lookbook"),
      video("luisa-lopez", "Luisa López · Joyería"),
    ],
  },
  {
    slug: "extrarome",
    number: 11,
    title: "Extrarome",
    client: "Extrarome",
    context: "Marca de aromas para espacios",
    categories: ["Visual Design", "Social Media", "Commercial Ads"],
    description:
      "Línea visual de una marca de aromas: fotografía de interiores, tipografía ligera, banners de scent marketing y aromaterapia, y videos de producto para el difusor Boxarome 1 y el aroma Granada de la colección Icónicas.",
    role: "Diseño de piezas y edición de video",
    tools: [],
    source: `${DRIVE} / 11. Extrarome`,
    items: [
      piece("extrarome-hogar", "La mejor opción para tu hogar", "Post La mejor opción para tu hogar con una sala en tonos grises"),
      piece("extrarome-elegancia", "Fusión de elegancia y pureza", "Post Fusión de elegancia y pureza con una habitación de madera clara"),
      piece("extrarome-aromas", "El poder de los aromas", "Post El poder de los aromas con un interior blanco"),
      piece("extrarome-plan", "El plan hogar incluye", "Post El plan hogar incluye: brief, propuestas, descuentos y un mes gratis"),
      piece("extrarome-scent", "Banner: scent marketing", "Banner Scent marketing con una mujer oliendo una vela"),
      piece("extrarome-aromaterapia", "Banner: aromaterapia", "Banner Aromaterapia con un frasco de aceite esencial"),
      video(
        "boxarome",
        "Boxarome 1",
        "Video de producto para el difusor Boxarome 1: funciones con iconografía, despiece de componentes, ficha técnica y el producto en ambientes reales.",
      ),
      video("iconicas", "Colección Icónicas: Granada", "Pieza para el aroma Granada: producto, ambiente y beneficios en 14 segundos, con tipografía limpia y la marca al cierre."),
    ],
  },
  {
    slug: "bellatriz",
    number: 12,
    title: "Bellatriz",
    client: "Bellatriz Beauty Club",
    context: "Piezas para redes de un club de belleza",
    categories: ["Social Media", "Visual Design"],
    description:
      "Cuatro posts para servicios de botox y limpieza facial: verde salvia, flores de línea y tipografía serif en mayúsculas, con jerarquía clara entre servicio, beneficio y llamado a reservar.",
    role: "Diseño de piezas",
    tools: [],
    source: `${DRIVE} / 12. Bellatriz`,
    items: [
      piece("bellatriz-01", "Botox", "Post Botox, tu aliado contra el envejecimiento, con botón Reserva tu cita"),
      piece("bellatriz-02", "Limpieza", "Post Limpieza para piel opaca y con imperfecciones"),
      piece("bellatriz-03", "Limpieza: lifting facial", "Post sobre lifting facial con flechas que marcan el contorno del rostro"),
      piece("bellatriz-04", "Limpieza: rutina", "Post Limpieza con la lista limpieza diaria, exfoliación e hidratación"),
    ],
  },
  {
    slug: "coca-cola-freeze",
    number: 13,
    title: "Coca-Cola Freeze",
    context: "Proyecto universitario, 100 % generado con IA",
    categories: ["Campañas con IA", "Visual Design"],
    description:
      "Campaña conceptual para un helado Coca-Cola Freeze: banner con QR, post para feed, empaque, registro y la activación del Laboratorio Freeze. Piezas y mockups generados con IA a partir de prompts.",
    role: "Dirección de arte, prompts y diseño",
    tools: [],
    source: `${DRIVE} / 13. Coca Cola Freeze (Proyecto Universitario)`,
    items: [
      piece("cocacola-banner", "Banner", "Banner rojo de Coca-Cola Freeze con un vaso de helado y el texto El helado que sabe a felicidad"),
      piece("cocacola-post", "Post para feed", "Post ¿Y si la felicidad se pudiera congelar? con un vaso de helado"),
      piece("cocacola-can", "Empaque", "Empaque de helado Coca-Cola Freeze sobre fondo gris"),
      piece("cocacola-register", "Registro", "Pieza Regístrate y vive la experiencia del Laboratorio Freeze"),
      piece("cocacola-lab", "Laboratorio Freeze", "Escena del Laboratorio Freeze con personas en una activación roja y blanca"),
    ],
    caseStudy: {
      objective: "Explorar una campaña completa de producto usando IA como herramienta de producción.",
      solution:
        "Un sistema rojo y blanco coherente con la marca: producto protagonista, claim emocional y una activación de marca con registro por QR.",
      process: ["Concepto y claim", "Prompts para producto y escenas", "Composición de piezas", "Adaptación a formatos"],
      result: "Kit de campaña con banner, post, empaque, registro y activación.",
    },
  },
  {
    slug: "costena-bacana",
    number: 14,
    title: "Costeña Bacana",
    context: "Proyecto conceptual, 100 % generado con IA",
    categories: ["Campañas con IA", "Visual Design"],
    description:
      "\"Hasta lo más bacano tiene su límite\": campaña conceptual con escenas de rumba, concierto y producto en verde, adaptada a post, banner, flyer con registro y pantalla de concierto. Contenido generado con IA a través de prompts.",
    role: "Dirección de arte, prompts y diseño",
    tools: [],
    source: `${DRIVE} / 14. Costeña Bacana`,
    items: [
      piece("costena-square", "Post", "Post cuadrado Hasta lo más bacano tiene su límite con amigos y la botella verde"),
      piece("costena-banner", "Banner", "Banner de Costeña Bacana con la botella verde y amigos celebrando"),
      piece("costena-vertical", "Flyer con registro", "Flyer vertical de Costeña Bacana con formulario de registro"),
      piece("costena-stage", "Pantalla de concierto", "Pantalla de concierto con la campaña de Costeña Bacana"),
    ],
  },
  {
    slug: "otros-proyectos",
    number: 15,
    title: "Otros proyectos",
    context: "Producto y proyectos universitarios",
    categories: ["Visual Design", "Motion Graphics", "Commercial Ads"],
    description:
      "Una pieza y un reel de producto para las Vitagomis de Multicentrum, y piezas académicas para dos lanzamientos de tecnología: la realidad virtual de Amazon y el Galaxy Ring de Samsung.",
    role: "Diseño, edición y motion graphics",
    tools: [],
    source: `${DRIVE} / 15. Otros proyectos`,
    items: [
      piece("multicentrum-post", "Multicentrum Vitagomis", "Post Siéntete imparable cada día con el frasco de Multicentrum Vitagomis entre hojas de menta"),
      video(
        "multivitaminico",
        "Reel multivitamínico",
        "Reel de producto: el empaque en primer plano, el claim repetido en capas de tipografía y una secuencia de beneficios con iconografía animada.",
      ),
      piece("amazon-vr", "Amazon: realidad virtual", "Banner Ha llegado la realidad virtual a nuestro servicio con una mujer usando visor VR"),
      piece("samsung-ring", "Samsung Galaxy Ring", "Pieza Samsung Galaxy Ring sobre fondo negro con luz azul"),
    ],
  },
];

/**
 * Chapters as each site shows them. The designer site shows every item, videos first;
 * the editor site keeps only chapters with video, and only their videos.
 */
export function chaptersFor(site: SiteId): Chapter[] {
  if (site === "disenador") {
    return chapters.map((c) => ({ ...c, items: [...c.items.filter((i) => i.kind === "video"), ...c.items.filter((i) => i.kind === "image")] }));
  }
  return chapters
    .map((c) => ({ ...c, items: c.items.filter((i) => i.kind === "video") }))
    .filter((c) => c.items.length > 0);
}

export function chapterBySlug(list: Chapter[], slug: string) {
  return list.find((c) => c.slug === slug);
}

export const entriesOf = (chapter: Chapter): Entry[] => chapter.items.map((item, index) => ({ item, chapter, index }));

export const isVideo = (item: MediaItem): item is VideoItem => item.kind === "video";

export const counts = (chapter: Chapter) => ({
  videos: chapter.items.filter((i) => i.kind === "video").length,
  pieces: chapter.items.filter((i) => i.kind === "image").length,
});
