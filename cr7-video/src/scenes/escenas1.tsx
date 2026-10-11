import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  Aparece,
  DestelloBlanco,
  Escena,
  FotoOscura,
} from "../components/base";
import { FormaDesenfocada, Reticula, Trazo } from "../components/decor";
import {
  BotonIsla,
  FotoSemitono,
  Insignia,
  ManchaOscura,
  Recorte,
} from "../components/graficos";
import { Bloque } from "../components/texto";
import { MADEIRA } from "../data/mapas";
import { SANS } from "../lib/fonts";
import { SOMBRA_SUAVE } from "../lib/theme";
import { P, pf } from "../lib/timing";
import { E } from "./tiempos";

/** Rótulo pequeño que aparece con desenfoque (etiquetas de mapa). */
const EtiquetaTardia: React.FC<{
  texto: string;
  x: number;
  y: number;
  en: number;
}> = ({ texto, x, y, en }) => {
  const f = useCurrentFrame();
  const p = Math.min(1, Math.max(0, (f - en) / 6));
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        translate: "-50% 0px",
        opacity: p,
        filter: `blur(${(1 - p) * 8}px)`,
        fontFamily: SANS,
        fontWeight: 700,
        fontSize: 38,
        letterSpacing: "-0.05em",
      }}
    >
      {texto}
    </div>
  );
};

/** Muestra los hijos solo entre dos fotogramas locales (bloques que se sustituyen). */
export const Ventana: React.FC<{
  desde: number;
  hasta: number;
  children: React.ReactNode;
}> = ({ desde, hasta, children }) => {
  const f = useCurrentFrame();
  return f >= desde && f < hasta ? <>{children}</> : null;
};

/* 1 · Intro oscura con cortes cada 8 fotogramas — "Todo comenzó en una pequeña" */
export const S01Intro: React.FC = () => {
  const { fps } = useVideoConfig();
  const [from, dur] = E.intro;
  const planos: Array<[string, number, number]> = [
    ["img/oscuro/intro_1_acantilado.jpg", 0, 8],
    ["img/oscuro/intro_2_olas.jpg", 8, 8],
    ["img/oscuro/intro_3_calle.jpg", 16, 7],
    ["img/oscuro/intro_4_roca.jpg", 23, 7],
    ["img/oscuro/intro_5_costa.jpg", 30, 8],
    ["img/oscuro/intro_6_acantilado2.jpg", 38, 7],
  ];
  return (
    <Escena
      nombre="01 Intro Madeira"
      from={from}
      dur={dur}
      modo="oscuro"
      entrada={false}
      empuje={0.04}
    >
      {planos.map(([src, a, d]) => (
        <Sequence
          key={src}
          name={src.split("/").pop()}
          from={a}
          durationInFrames={d}
          premountFor={fps}
        >
          <FotoOscura src={src} dur={d} empuje={0.03} />
        </Sequence>
      ))}
      <Bloque
        top={790}
        lineas={[
          { w: [{ i: P.todo }], tipo: "peq", align: "left", size: 56, mb: 14 },
          { w: [{ i: P.comenzo }], tipo: "heroSans", size: 205 },
          {
            w: [{ i: P.en }, { i: P.una }, { i: P.pequena }],
            tipo: "peq",
            align: "right",
            size: 52,
          },
        ]}
      />
      <DestelloBlanco dur={5} />
    </Escena>
  );
};

/* 2 · Blanco: botón con la isla — "isla de Portugal" */
export const S02Isla: React.FC = () => {
  const [from, dur] = E.isla;
  const pin = pf(P.portugal) - from;
  return (
    <Escena nombre="02 Isla de Portugal" from={from} dur={dur}>
      <FormaDesenfocada x={1010} y={70} rot={20} />
      <FormaDesenfocada x={40} y={1860} rot={-30} vel={-6} />
      <Bloque
        top={360}
        lineas={[
          { w: [{ i: P.una }, { i: P.pequena }], tipo: "peq", align: "left" },
          { w: [{ i: P.isla }], tipo: "heroSans", size: 230 },
          {
            w: [{ i: P.de }, { i: P.portugal, t: "Portugal" }],
            tipo: "peq",
            align: "right",
          },
        ]}
      />
      <BotonIsla cx={540} cy={1130} en={1} pinEn={pin} />
      <Insignia
        src="img/escudos/portugal_bandera.svg"
        x={830}
        y={850}
        size={150}
        en={pin + 3}
        redondo
      />
    </Escena>
  );
};

/* 3a · Oscuro — "donde un NIÑO" */
export const S03Nino: React.FC = () => {
  const [from, dur] = E.nino;
  return (
    <Escena nombre="03a Niño" from={from} dur={dur} modo="oscuro" empuje={0.04}>
      <FotoOscura
        src="img/oscuro/nino_silueta.jpg"
        dur={dur}
        origen="50% 60%"
      />
      <Bloque
        top={720}
        lineas={[
          {
            w: [{ i: P.donde }, { i: P.un }],
            tipo: "peq",
            align: "left",
            size: 54,
          },
          { w: [{ i: P.nino, t: "NIÑO" }], tipo: "hero", size: 250 },
        ]}
      />
    </Escena>
  );
};

/* 3b · Oscuro — "tenía un SUEÑO" */
export const S03Sueno: React.FC = () => {
  const [from, dur] = E.sueno;
  return (
    <Escena
      nombre="03b Sueño"
      from={from}
      dur={dur}
      modo="oscuro"
      empuje={0.04}
    >
      <FotoOscura
        src="img/oscuro/ninos_jugando.jpg"
        dur={dur}
        origen="50% 30%"
      />
      <Bloque
        top={760}
        lineas={[
          {
            w: [{ i: P.tenia }, { i: P.un2 }],
            tipo: "peq",
            align: "left",
            size: 54,
          },
          { w: [{ i: P.sueno, t: "SUEÑO" }], tipo: "hero", size: 250 },
        ]}
      />
    </Escena>
  );
};

/* 3c · Oscuro, una palabra por línea — "más grande que sus posibilidades" */
export const S03Posibilidades: React.FC = () => {
  const [from, dur] = E.posib;
  return (
    <Escena
      nombre="03c Posibilidades"
      from={from}
      dur={dur}
      modo="oscuro"
      empuje={0.16}
    >
      <FotoOscura
        src="img/oscuro/balon_escalera.jpg"
        dur={dur}
        origen="30% 60%"
        empuje={0.1}
      />
      <Bloque
        top={700}
        cx={640}
        lineas={[
          { w: [{ i: P.mas }], tipo: "med", size: 92 },
          { w: [{ i: P.grande }], tipo: "med", size: 92 },
          { w: [{ i: P.que }, { i: P.sus }], tipo: "med", size: 92 },
          {
            w: [{ i: P.posibilidades, t: "posibilidades" }],
            tipo: "serifMin",
            size: 112,
          },
        ]}
      />
    </Escena>
  );
};

/* 4 · Blanco (drop musical) — "De Madeira al Manchester United" */
export const S04United: React.FC = () => {
  const [from, dur] = E.united;
  const fMadeira = pf(P.madeira) - from;
  const fManchester = pf(P.manchester) - from;
  const iw = 250;
  return (
    <Escena nombre="04 Manchester United" from={from} dur={dur} empuje={0.08}>
      <FormaDesenfocada x={1030} y={120} rot={60} />
      <Reticula cx={540} cy={1330} size={820} en={2} />
      <Bloque
        top={300}
        lineas={[
          {
            w: [{ i: P.De }, { i: P.madeira }, { i: P.al }],
            tipo: "peq",
            align: "left",
          },
          {
            w: [{ i: P.manchester, t: "MANCHESTER" }],
            tipo: "hero",
            size: 168,
          },
          { w: [{ i: P.united, t: "United" }], tipo: "peq", align: "right" },
        ]}
      />
      {/* ruta Madeira → Manchester por encima de la cabeza */}
      <Aparece
        en={fMadeira - 3}
        desde={0.4}
        rot={-10}
        flotar={6}
        style={{ left: 170 - iw / 2, top: 1090 }}
      >
        <svg
          viewBox={`0 0 ${MADEIRA.w} ${MADEIRA.h}`}
          width={iw}
          height={(iw * MADEIRA.h) / MADEIRA.w}
          style={{ filter: SOMBRA_SUAVE }}
        >
          <path d={MADEIRA.d} fill="#151515" />
        </svg>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 38,
            letterSpacing: "-0.05em",
            textAlign: "center",
            marginTop: 10,
          }}
        >
          Madeira
        </div>
      </Aparece>
      <Trazo
        d="M 175 1060 C 260 740, 760 690, 880 1020"
        en={fMadeira + 2}
        dur={fManchester - fMadeira}
        grosor={5}
        flecha
      />
      <Recorte src="img/recortes/mu_espalda.png" x={322} y={850} alto={1100} />
      <Insignia
        src="img/escudos/manchester_united.svg"
        x={880}
        y={1160}
        size={230}
        en={fManchester}
      />
      <EtiquetaTardia
        texto="Manchester"
        x={880}
        y={1300}
        en={fManchester + 4}
      />
    </Escena>
  );
};

/* 5 · B&N con semitono, palabra suelta en el pecho — "del Real / Madrid" */
export const S05Madrid: React.FC = () => {
  const [from, dur] = E.madrid;
  const fMadrid = pf(P.madrid) - from;
  return (
    <Escena
      nombre="05 Real Madrid"
      from={from}
      dur={dur}
      modo="oscuro"
      empuje={0.05}
    >
      <FotoSemitono
        src="img/fotos/madrid_2016.jpg"
        dur={dur}
        origen="50% 30%"
      />
      <ManchaOscura cx={540} cy={1060} />
      <Ventana desde={0} hasta={fMadrid - 4}>
        <Bloque
          top={1010}
          lineas={[{ w: [{ i: P.del }, { i: P.real }], tipo: "med", size: 84 }]}
        />
      </Ventana>
      <Ventana desde={fMadrid - 4} hasta={dur}>
        <Bloque
          top={995}
          lineas={[
            { w: [{ i: P.madrid, t: "Madrid" }], tipo: "serifMin", size: 132 },
          ]}
        />
      </Ventana>
    </Escena>
  );
};

/* Fondo negro final (corte a negro, estilo.md §6) */
export const SNegro: React.FC = () => {
  const [from, dur] = E.negro;
  return (
    <Sequence name="Negro final" from={from} durationInFrames={dur}>
      <AbsoluteFill style={{ backgroundColor: "#000" }} />
    </Sequence>
  );
};
