import React from "react";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useVideoConfig,
} from "remotion";
import "./lib/fonts";
import { P, pf } from "./lib/timing";
import {
  S01Intro,
  S02Isla,
  S03Nino,
  S03Posibilidades,
  S03Sueno,
  S04United,
  S05Madrid,
  SNegro,
} from "./scenes/escenas1";
import {
  S06Mundo,
  S07Disciplina,
  S08Sacrificio,
  S09Imparable,
  S10Records,
  S11Titulos,
  S12Historia,
  S13Cristiano,
  S14Legado,
} from "./scenes/escenas2";
import { DURACION_TOTAL, E } from "./scenes/tiempos";

/** Un SFX en un fotograma global (estilo.md §9.2: siempre pegado a un evento visual). */
const Sfx: React.FC<{
  en: number;
  src: string;
  vol?: number;
  nombre?: string;
}> = ({ en, src, vol = 0.8, nombre }) => {
  const { fps } = useVideoConfig();
  return (
    <Audio
      name={nombre ?? src}
      from={Math.max(0, en)}
      src={staticFile(`sfx/${src}.wav`)}
      volume={vol}
      premountFor={fps}
    />
  );
};

export const CR7: React.FC = () => {
  const { fps } = useVideoConfig();
  const fin = E.negro[0];
  return (
    <AbsoluteFill style={{ backgroundColor: "#fff" }}>
      {/* ---------- Imagen ---------- */}
      <S01Intro />
      <S02Isla />
      <S03Nino />
      <S03Sueno />
      <S03Posibilidades />
      <S04United />
      <S05Madrid />
      <S06Mundo />
      <S07Disciplina />
      <S08Sacrificio />
      <S09Imparable />
      <S10Records />
      <S11Titulos />
      <S12Historia />
      <S13Cristiano />
      <S14Legado />
      <SNegro />

      {/* ---------- Voz ---------- */}
      <Audio name="Voz" src={staticFile("audio/voz.mp3")} premountFor={fps} />

      {/* ---------- Música: "Timeless" limpia, desplazada para que el drop (7,15 s) caiga en 7,56 s ---------- */}
      <Audio
        name="Música Timeless"
        src={staticFile("audio/musica_timeless.wav")}
        premountFor={fps}
        volume={(f) =>
          interpolate(f, [0, 3, fin - 4, fin], [0, 1.1, 1.1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        }
      />

      {/* ---------- SFX extraídos de la referencia ---------- */}
      {/* Intro: clic de flash en cada corte rápido */}
      <Sfx nombre="flash corte 1" en={0} src="flash_click_1" vol={0.9} />
      <Sfx nombre="flash corte 2" en={8} src="flash_click_2" vol={0.8} />
      <Sfx nombre="flash corte 3" en={16} src="flash_click_3" vol={0.8} />
      <Sfx nombre="flash corte 4" en={23} src="flash_click_2" vol={0.8} />
      <Sfx nombre="flash corte 5" en={30} src="flash_click_1" vol={0.8} />
      <Sfx nombre="flash corte 6" en={38} src="flash_click_3" vol={0.8} />
      {/* Oscuro → blanco: golpe + campanilla con la isla */}
      <Sfx nombre="boom isla" en={E.isla[0]} src="boom_ring" vol={0.9} />
      <Sfx nombre="pop chincheta" en={pf(P.portugal)} src="pop_1" vol={0.7} />
      {/* Planos oscuros del niño */}
      <Sfx nombre="flash niño" en={E.nino[0]} src="flash_click_2" vol={0.45} />
      <Sfx
        nombre="flash sueño"
        en={E.sueno[0]}
        src="flash_click_1"
        vol={0.45}
      />
      <Sfx
        nombre="flash posibilidades"
        en={E.posib[0]}
        src="flash_click_3"
        vol={0.45}
      />
      {/* Riser antes del giro → drop musical en "De Madeira" */}
      <Sfx nombre="riser" en={E.united[0] - 44} src="riser" vol={0.75} />
      <Sfx nombre="boom United" en={E.united[0]} src="boom_ring_2" vol={0.8} />
      <Sfx nombre="pop Madeira" en={pf(P.madeira) - 3} src="pop_2" vol={0.6} />
      <Sfx
        nombre="pop escudo United"
        en={pf(P.manchester)}
        src="pop_3"
        vol={0.7}
      />
      {/* B&N Madrid */}
      <Sfx
        nombre="flash Madrid"
        en={E.madrid[0]}
        src="flash_click_1"
        vol={0.6}
      />
      {/* Globo: un pop por escudo */}
      <Sfx nombre="pop Sporting" en={pf(P.conquistar)} src="pop_1" vol={0.6} />
      <Sfx
        nombre="pop United"
        en={pf(P.conquistar) + 4}
        src="pop_2"
        vol={0.6}
      />
      <Sfx
        nombre="pop Madrid"
        en={pf(P.conquistar) + 8}
        src="pop_3"
        vol={0.6}
      />
      <Sfx
        nombre="pop Juventus"
        en={pf(P.conquistar) + 12}
        src="pop_4"
        vol={0.6}
      />
      {/* Diálogo de interfaz */}
      <Sfx nombre="ui beep" en={E.disciplina[0] + 1} src="ui_beep" vol={0.75} />
      <Sfx
        nombre="clic Entrenar"
        en={E.disciplina[0] + 23}
        src="flash_click_3"
        vol={0.9}
      />
      <Sfx
        nombre="flash sacrificio"
        en={E.sacrificio[0]}
        src="flash_click_2"
        vol={0.5}
      />
      {/* Gráfica imparable: un pop por punto */}
      <Sfx
        nombre="pop gráfica 1"
        en={E.imparable[0] + 8 + 5}
        src="pop_1"
        vol={0.55}
      />
      <Sfx
        nombre="pop gráfica 2"
        en={E.imparable[0] + 8 + 13}
        src="pop_2"
        vol={0.55}
      />
      <Sfx
        nombre="pop gráfica 3"
        en={E.imparable[0] + 8 + 20}
        src="pop_3"
        vol={0.55}
      />
      <Sfx
        nombre="pop gráfica 4"
        en={E.imparable[0] + 8 + 26}
        src="pop_4"
        vol={0.6}
      />
      {/* Récords: el cristal se rompe */}
      <Sfx
        nombre="cristal roto"
        en={pf(P.records)}
        src="glass_crack"
        vol={0.95}
      />
      {/* Polaroids cayendo */}
      <Sfx
        nombre="polaroid 1"
        en={E.titulos[0] + 3}
        src="photo_paper"
        vol={0.75}
      />
      <Sfx
        nombre="polaroid 2"
        en={E.titulos[0] + 11}
        src="photo_paper"
        vol={0.75}
      />
      <Sfx
        nombre="polaroid 3"
        en={E.titulos[0] + 19}
        src="photo_paper"
        vol={0.75}
      />
      {/* Historia */}
      <Sfx nombre="pop historia" en={pf(P.historia)} src="pop_2" vol={0.6} />
      {/* Gran revelado del nombre */}
      <Sfx
        nombre="boom Cristiano"
        en={E.cristiano[0]}
        src="boom_ring"
        vol={0.9}
      />
      {/* Legado: puntos que aparecen y salen "más allá" */}
      <Sfx nombre="pops puntos" en={E.legado[0] + 3} src="pops" vol={0.5} />
      <Sfx nombre="pop más allá 1" en={pf(P.mas2)} src="pop_3" vol={0.6} />
      <Sfx nombre="pop más allá 2" en={pf(P.mas2) + 4} src="pop_4" vol={0.6} />
      <Sfx nombre="pop balón" en={pf(P.futbol) - 2} src="pop_1" vol={0.6} />
    </AbsoluteFill>
  );
};

export const CR7_DURACION = DURACION_TOTAL;
