import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { BloqueSubtitulo } from "./componentes/Subtitulos";
import { Cierre } from "./componentes/Cierre";
import { EscenaBarra } from "./componentes/EscenaBarra";
import { MarcaDeAgua } from "./componentes/MarcaDeAgua";
import { Plano } from "./componentes/Plano";
import { Sonido } from "./componentes/Sonido";
import { ANTES_DEL_CORTE, DESPUES_DEL_CORTE, TransicionLuz } from "./componentes/TransicionLuz";
import { BLOQUES, DURACION, ESCENAS_BARRA, PLANOS, T_CIERRE, TRANSICIONES_LUZ } from "./datos/edicion";
import { useFuentes } from "./fuentes";

/** "Semilla certificada" — AgroKrack. Montaje según estilo.md. */
export const SemillaCertificada: React.FC = () => {
  const fuentesListas = useFuentes();
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* ── Vídeo: busto parlante y b-roll ── */}
      {PLANOS.map((p) => (
        <Sequence key={p.id} name={p.id} from={f(p.desde)} durationInFrames={f(p.hasta) - f(p.desde)} premountFor={fps}>
          <Plano plano={p} />
        </Sequence>
      ))}

      {/* ── Motion graphics a pantalla completa ── */}
      {ESCENAS_BARRA.map((e, i) => (
        <Sequence key={e.id} name={e.id} from={f(e.desde)} durationInFrames={f(e.hasta) - f(e.desde)}>
          {fuentesListas ? <EscenaBarra escena={e} idx={i} /> : null}
        </Sequence>
      ))}

      {/* ── Cierre con el logo ── */}
      <Sequence name="Cierre · logo" from={f(T_CIERRE)} durationInFrames={f(DURACION) - f(T_CIERRE)}>
        <Cierre />
      </Sequence>

      {/* ── Subtítulos, destacados y cita ── */}
      {fuentesListas
        ? BLOQUES.map((b, i) => (
            <Sequence
              key={i}
              name={`Texto · ${b.tipo}`}
              from={f(b.ini)}
              durationInFrames={Math.max(1, f(b.fin) - f(b.ini))}
              layout="none"
            >
              <BloqueSubtitulo b={b} />
            </Sequence>
          ))
        : null}

      {/* ── Marca de agua (no aparece sobre el logo final) ── */}
      <Sequence name="Marca de agua" durationInFrames={f(T_CIERRE)} layout="none">
        {fuentesListas ? <MarcaDeAgua /> : null}
      </Sequence>

      {/* ── Transiciones de fuga de luz ── */}
      {TRANSICIONES_LUZ.map((tr) => (
        <Sequence
          key={tr.t}
          name="Transición · fuga de luz"
          from={f(tr.t - ANTES_DEL_CORTE)}
          durationInFrames={f(ANTES_DEL_CORTE + DESPUES_DEL_CORTE)}
        >
          <TransicionLuz semilla={tr.semilla} />
        </Sequence>
      ))}

      <Sonido />
    </AbsoluteFill>
  );
};
