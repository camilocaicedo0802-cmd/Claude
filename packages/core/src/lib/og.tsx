import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ImageResponse } from "next/og";

const root = join(process.cwd(), "..", "..");
const font = (file: string) => readFileSync(join(root, "node_modules", "@fontsource", file));

interface Props {
  role: string;
  headline: [string, string];
  subtitle: string;
  poster: string;
}

/** 1200x630 share card: black ground, white Poppins name, red role and Playfair word, a real poster. */
export function ogImage({ role, headline, subtitle, poster }: Props) {
  const posterData = `data:image/png;base64,${readFileSync(join(root, "media", "out", "og", `${poster}.png`)).toString("base64")}`;
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", background: "#080808", color: "#fff", fontFamily: "Poppins" }}>
        <div style={{ width: 6, height: "100%", background: "#e50914" }} />
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", padding: "64px 56px", flex: 1 }}>
          <div style={{ display: "flex", fontSize: 26, fontWeight: 600 }}>
            Juan Camilo Caicedo
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 56, fontWeight: 700, letterSpacing: -2, lineHeight: 1.05 }}>{headline[0]}</div>
            <div style={{ fontSize: 58, fontFamily: "Playfair", fontStyle: "italic", color: "#e50914", lineHeight: 1.2 }}>{headline[1]}</div>
            <div style={{ marginTop: 24, fontSize: 26, color: "#a3a3a3" }}>{subtitle}</div>
          </div>
          <div style={{ fontSize: 22, color: "#e50914" }}>{role}</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", paddingRight: 56 }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={posterData} width={296} height={526} style={{ objectFit: "cover" }} alt="" />
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      fonts: [
        { name: "Poppins", data: font("poppins/files/poppins-latin-600-normal.woff"), weight: 600, style: "normal" },
        { name: "Poppins", data: font("poppins/files/poppins-latin-700-normal.woff"), weight: 700, style: "normal" },
        { name: "Poppins", data: font("poppins/files/poppins-latin-400-normal.woff"), weight: 400, style: "normal" },
        { name: "Playfair", data: font("playfair-display/files/playfair-display-latin-500-italic.woff"), weight: 500, style: "italic" },
      ],
    },
  );
}
