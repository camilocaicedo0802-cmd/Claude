import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { EDL, Segment, zoomAt } from "../edl";

type Kind = "base" | "fg";

/**
 * Vídeo de una toma con su reencuadre. `offset` = fotograma local del segmento en el que
 * empieza este componente (para copias que arrancan a mitad de la toma, p. ej. la textura
 * dentro de las letras). Fondo, recorte y textura usan la misma transformación.
 */
export const SegmentFrame: React.FC<{ seg: Segment; kind: Kind; offset?: number; style?: React.CSSProperties }> = ({
  seg,
  kind,
  offset = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const z = zoomAt(seg, offset + frame);
  return (
    <AbsoluteFill style={{ scale: String(z.s), transformOrigin: `${z.ox}% ${z.oy}%`, ...style }}>
      <OffthreadVideo
        src={staticFile(kind === "base" ? seg.file : seg.fg)}
        trimBefore={offset}
        muted
        transparent={kind === "fg"}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};

/** Capa con todas las tomas habladas (fondo o recorte de la persona). */
export const SegmentsLayer: React.FC<{ kind: Kind }> = ({ kind }) => (
  <>
    {EDL.segments.map((seg) => (
      <Sequence key={`${kind}-${seg.id}`} from={seg.from_} durationInFrames={seg.dur} name={`${kind} ${seg.id}`}>
        <SegmentFrame seg={seg} kind={kind} />
      </Sequence>
    ))}
  </>
);
