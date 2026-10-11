import React from "react";
import { useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Aparece, Escena, FotoOscura, Golpe } from "../components/base";
import {
  Arcos,
  Bokeh,
  FormaDesenfocada,
  Reticula,
  Trazo,
} from "../components/decor";
import {
  Balon,
  BotonContador,
  DialogoUI,
  Firma,
  Globo,
  GraficaImparable,
  Insignia,
  Polaroid,
  Puntos,
  Recorte,
} from "../components/graficos";
import { Bloque } from "../components/texto";
import { SOMBRA } from "../lib/theme";
import { P, pf } from "../lib/timing";
import { E } from "./tiempos";

/* 6 · Blanco: globo terráqueo con los escudos orbitando — "a conquistar el MUNDO" */
export const S06Mundo: React.FC = () => {
  const [from, dur] = E.mundo;
  const fConq = pf(P.conquistar) - from;
  const fMundo = pf(P.mundo) - from;
  const escudos: Array<[string, number, number]> = [
    ["img/escudos/sporting.png", 205, 1000],
    ["img/escudos/manchester_united.svg", 880, 930],
    ["img/escudos/real_madrid.svg", 190, 1420],
    ["img/escudos/juventus.svg", 890, 1400],
  ];
  return (
    <Escena nombre="06 Conquistar el mundo" from={from} dur={dur} empuje={0.06}>
      <Globo cx={150} cy={130} d={520} peana={false} blur={10} fase={300} />
      <Globo cx={760} cy={1930} d={600} peana={false} blur={12} fase={700} />
      <Bloque
        top={330}
        lineas={[
          {
            w: [{ i: P.a }, { i: P.conquistar }, { i: P.el }],
            tipo: "peq",
            align: "left",
          },
          { w: [{ i: P.mundo, t: "MUNDO" }], tipo: "hero", size: 230 },
        ]}
      />
      <Trazo
        d="M 330 640 C 470 690, 680 690, 790 625"
        en={fMundo + 4}
        dur={9}
        grosor={5}
        flecha
      />
      <Aparece
        en={0}
        desde={0.35}
        rot={-14}
        flotar={8}
        style={{ left: 0, top: 0, width: 1080, height: 1920 }}
      >
        <Globo cx={540} cy={1180} d={560} />
      </Aparece>
      {escudos.map(([src, x, y], k) => (
        <Insignia
          key={src}
          src={src}
          x={x}
          y={y}
          size={170}
          en={fConq + k * 4}
        />
      ))}
    </Escena>
  );
};

/* 7 · Blanco: diálogo de interfaz — "DISCIPLINA" */
export const S07Disciplina: React.FC = () => {
  const [from, dur] = E.disciplina;
  return (
    <Escena nombre="07 Disciplina" from={from} dur={dur} empuje={0.05}>
      <Arcos en={0} variante={0} />
      <Reticula cx={540} cy={1080} size={900} n={6} opacidad={0.7} />
      <Bloque
        top={360}
        lineas={[
          {
            w: [{ i: P.disciplina, t: "DISCIPLINA" }],
            tipo: "hero",
            size: 190,
          },
        ]}
      />
      <DialogoUI en={1} clicEn={23} cx={540} cy={1100} />
    </Escena>
  );
};

/* 8 · Oscuro: entrenamiento de noche — "SACRIFICIO" */
export const S08Sacrificio: React.FC = () => {
  const [from, dur] = E.sacrificio;
  return (
    <Escena
      nombre="08 Sacrificio"
      from={from}
      dur={dur}
      modo="oscuro"
      empuje={0.05}
    >
      <FotoOscura src="img/oscuro/noche_entreno.jpg" dur={dur} />
      <Bloque
        top={840}
        lineas={[
          {
            w: [{ i: P.sacrificio, t: "SACRIFICIO" }],
            tipo: "hero",
            size: 200,
          },
        ]}
      />
    </Escena>
  );
};

/* 9 · Blanco: gráfica que se dispara con el balón — "y una ambición IMPARABLE" */
export const S09Imparable: React.FC = () => {
  const [from, dur] = E.imparable;
  return (
    <Escena nombre="09 Ambición imparable" from={from} dur={dur} empuje={0.06}>
      <FormaDesenfocada x={40} y={1880} rot={10} />
      <Reticula cx={560} cy={1130} size={980} n={7} en={0} />
      <Bloque
        top={300}
        lineas={[
          {
            w: [{ i: P.y }, { i: P.una2 }, { i: P.ambicion }],
            tipo: "peq",
            align: "left",
          },
          { w: [{ i: P.imparable, t: "IMPARABLE" }], tipo: "hero", size: 190 },
        ]}
      />
      <GraficaImparable en={2} dur={34} />
    </Escena>
  );
};

/* 10 · Blanco: contador de goles que se agrieta — "Rompió RÉCORDS" */
export const S10Records: React.FC = () => {
  const [from, dur] = E.records;
  return (
    <Escena nombre="10 Rompió récords" from={from} dur={dur} empuje={0.06}>
      <FormaDesenfocada x={1020} y={90} rot={40} />
      <FormaDesenfocada x={60} y={1850} rot={-20} vel={-7} />
      <Bloque
        top={330}
        lineas={[
          {
            w: [{ i: P.rompio }],
            tipo: "peq",
            align: "left",
            size: 56,
            mb: 14,
          },
          { w: [{ i: P.records, t: "RÉCORDS" }], tipo: "hero", size: 230 },
        ]}
      />
      <BotonContador
        cx={540}
        cy={1170}
        en={1}
        grietaEn={pf(P.records) - from}
      />
    </Escena>
  );
};

/* 11 · Blanco: polaroids de títulos — "conquistó TÍTULOS" */
export const S11Titulos: React.FC = () => {
  const [from, dur] = E.titulos;
  return (
    <Escena nombre="11 Títulos" from={from} dur={dur} empuje={0.06}>
      <FormaDesenfocada x={1020} y={80} rot={70} />
      <Reticula cx={540} cy={1200} size={860} en={0} />
      <Bloque
        top={300}
        lineas={[
          {
            w: [{ i: P.conquisto }],
            tipo: "peq",
            align: "left",
            size: 56,
            mb: 14,
          },
          { w: [{ i: P.titulos, t: "TÍTULOS" }], tipo: "hero", size: 230 },
        ]}
      />
      <Polaroid
        src="img/fotos/premier_2008.jpg"
        texto="PREMIER LEAGUE (2008)"
        x={420}
        y={1080}
        rot={-9}
        en={3}
        foco="55% 40%"
      />
      <Polaroid
        src="img/fotos/champions_2018.jpg"
        texto="CHAMPIONS (2018)"
        x={660}
        y={1170}
        rot={8}
        en={11}
        foco="40% 45%"
      />
      <Polaroid
        src="img/fotos/balon_oro_museo.jpg"
        texto="BALÓN DE ORO x5"
        x={500}
        y={1290}
        rot={-3}
        en={19}
        foco="50% 30%"
      />
    </Escena>
  );
};

/* 12 · Blanco: camiseta 7 + firma — "y escribió su propia HISTORIA" */
export const S12Historia: React.FC = () => {
  const [from, dur] = E.historia;
  const fEscribio = pf(P.escribio) - from;
  const fHistoria = pf(P.historia) - from;
  return (
    <Escena nombre="12 Su propia historia" from={from} dur={dur} empuje={0.07}>
      <FormaDesenfocada x={1030} y={100} rot={15} />
      <Bokeh
        puntos={[
          [120, 760, 34],
          [960, 860, 24],
          [180, 1640, 40],
          [930, 1700, 28],
          [70, 1240, 18],
        ]}
        en={2}
      />
      <Bloque
        top={300}
        lineas={[
          {
            w: [{ i: P.y2 }, { i: P.escribio }, { i: P.su }, { i: P.propia }],
            tipo: "peq",
            align: "left",
          },
          { w: [{ i: P.historia, t: "HISTORIA" }], tipo: "hero", size: 220 },
        ]}
      />
      <Golpe en={fHistoria} cuanto={0.12} origen="50% 70%">
        <Aparece
          en={0}
          desde={0.4}
          rot={-12}
          flotar={8}
          style={{ left: 0, top: 0, width: 1080, height: 1920 }}
        >
          <Recorte
            src="img/recortes/camiseta7.png"
            x={110}
            y={830}
            alto={760}
          />
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              width: 1080,
              height: 1920,
              filter: "invert(1)",
            }}
          >
            <Firma x={560} y={1330} ancho={520} en={fEscribio} dur={26} />
          </div>
        </Aparece>
      </Golpe>
      <Trazo
        d="M 250 1580 C 420 1640, 700 1640, 860 1560"
        en={fHistoria}
        dur={9}
        grosor={5}
      />
    </Escena>
  );
};

/* 13 · Blanco: gran revelado con la celebración — "Su nombre es CRISTIANO Ronaldo" */
export const S13Cristiano: React.FC = () => {
  const [from, dur] = E.cristiano;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sube = spring({
    frame: frame - 1,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.9 },
  });
  return (
    <Escena nombre="13 Cristiano Ronaldo" from={from} dur={dur} empuje={0.07}>
      <Bokeh
        puntos={[
          [130, 300, 46],
          [950, 260, 30],
          [80, 900, 26],
          [1000, 980, 52],
          [200, 1300, 34],
          [900, 1500, 22],
          [540, 180, 20],
        ]}
        en={0}
      />
      <FormaDesenfocada x={1040} y={1880} rot={-40} />
      <Bloque
        top={400}
        lineas={[
          {
            w: [{ i: P.Su }, { i: P.nombre }, { i: P.es }],
            tipo: "peq",
            align: "left",
            size: 56,
          },
          { w: [{ i: P.cristiano, t: "CRISTIANO" }], tipo: "hero", size: 210 },
          {
            w: [{ i: P.ronaldo, t: "Ronaldo" }],
            tipo: "med",
            align: "right",
            size: 92,
          },
        ]}
      />
      <Golpe en={pf(P.ronaldo) - from} cuanto={0.1} origen="50% 85%">
        <Recorte
          src="img/recortes/celebracion_madrid.png"
          x={-90}
          y={1060}
          alto={880}
          style={{
            translate: `0px ${(1 - sube) * 420}px`,
            filter: `${SOMBRA}${sube < 0.9 ? ` blur(${(1 - sube) * 10}px)` : ""}`,
          }}
        />
      </Golpe>
    </Escena>
  );
};

/* 14 · Blanco: estatua de Funchal + puntos que salen "más allá" — "y su legado va mucho MÁS ALLÁ del fútbol" */
export const S14Legado: React.FC = () => {
  const [from, dur] = E.legado;
  const fMas = pf(P.mas2) - from;
  const fFutbol = pf(P.futbol) - from;
  return (
    <Escena
      nombre="14 Legado"
      from={from}
      dur={dur}
      empuje={0.06}
      salida={false}
    >
      <Reticula cx={540} cy={1200} size={900} n={6} en={0} />
      <Bloque
        top={300}
        lineas={[
          {
            w: [
              { i: P.y3 },
              { i: P.su2 },
              { i: P.legado },
              { i: P.va },
              { i: P.mucho },
            ],
            tipo: "peq",
            align: "left",
          },
          {
            w: [
              { i: P.mas2, t: "MÁS" },
              { i: P.alla, t: "ALLÁ" },
            ],
            tipo: "hero",
            size: 210,
          },
          {
            w: [{ i: P.del2 }, { i: P.futbol, t: "fútbol" }],
            tipo: "peq",
            align: "right",
          },
        ]}
      />
      <Puntos cx={540} cy={1200} en={3} salenEn={fMas} />
      <Recorte
        src="img/recortes/estatua_funchal.png"
        x={366}
        y={830}
        alto={760}
      />
      <Aparece
        en={fFutbol - 2}
        desde={0.2}
        rot={-90}
        flotar={4}
        style={{ left: 640, top: 1450, filter: SOMBRA }}
      >
        <Balon size={130} rot={-15} />
      </Aparece>
    </Escena>
  );
};
