import { MyComposition } from "./Composition";
import { Dia2 } from "./dia2/Dia2";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Día 1 (entregado) */}
      <MyComposition />
      {/* Día 2 · Punto de partida */}
      <Dia2 />
    </>
  );
};
