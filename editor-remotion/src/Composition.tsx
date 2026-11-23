import { Composition } from "remotion";
import { ArmandoBits } from "./Video";
import { FPS, H, W } from "./theme";
import { TOTAL_SECONDS } from "./timeline";

export const MyComposition = () => {
  return <Composition id="ArmandoBits" component={ArmandoBits} durationInFrames={Math.round(TOTAL_SECONDS * FPS)} fps={FPS} width={W} height={H} />;
};
