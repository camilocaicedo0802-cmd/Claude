import { Composition } from "remotion";
import { ArmandoBitsHorizontal } from "./horizontal/Video";
import { ArmandoBits } from "./Video";
import { FPS, H, W } from "./theme";
import { TOTAL_SECONDS } from "./timeline";

export const MyComposition = () => {
  const durationInFrames = Math.round(TOTAL_SECONDS * FPS);
  return (
    <>
      {/* Opción A: recorte vertical a pantalla completa */}
      <Composition id="ArmandoBits" component={ArmandoBits} durationInFrames={durationInFrames} fps={FPS} width={W} height={H} />
      {/* Opción B: plano horizontal en ventana, con textos y recursos arriba y abajo */}
      <Composition id="ArmandoBitsHorizontal" component={ArmandoBitsHorizontal} durationInFrames={durationInFrames} fps={FPS} width={W} height={H} />
    </>
  );
};
