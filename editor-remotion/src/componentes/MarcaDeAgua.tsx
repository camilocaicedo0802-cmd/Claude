import { FUENTE, MARCA_DE_AGUA } from "../estilo";

/** Marca de agua fija abajo, al 30 % (estilo.md §6). */
export const MarcaDeAgua: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: 0,
      width: "100%",
      top: MARCA_DE_AGUA.y - MARCA_DE_AGUA.tam * 0.6,
      textAlign: "center",
      fontFamily: FUENTE.normal,
      fontWeight: 300,
      fontSize: MARCA_DE_AGUA.tam,
      letterSpacing: "-0.04em",
      lineHeight: 1.2,
      color: "#FFFFFF",
      opacity: MARCA_DE_AGUA.opacidad,
      textShadow: "0 1px 6px rgba(0,0,0,0.35)",
    }}
  >
    {MARCA_DE_AGUA.texto}
  </div>
);
