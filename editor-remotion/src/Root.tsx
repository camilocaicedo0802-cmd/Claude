import { Composition } from "remotion";
import { DURACION } from "./datos/edicion";
import { ALTO, ANCHO, FPS } from "./estilo";
import { SemillaCertificada } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SemillaCertificada"
        component={SemillaCertificada}
        durationInFrames={Math.ceil(DURACION * FPS)}
        fps={FPS}
        width={ANCHO}
        height={ALTO}
      />
    </>
  );
};
