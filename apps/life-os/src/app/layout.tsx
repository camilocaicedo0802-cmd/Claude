import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { AppProviders } from "@/components/shell/app-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "LIFE OS", template: "%s · LIFE OS" },
  description: "Tu centro de control personal: finanzas, clientes y tu día en un solo lugar.",
  applicationName: "LIFE OS",
  manifest: `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/manifest.webmanifest`,
  appleWebApp: { capable: true, title: "LIFE OS", statusBarStyle: "default" },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#faf9f7",
};

// Applies the saved theme before the first paint (no light flash in dark mode).
const themeScript = `(function(){try{var t=localStorage.getItem("lifeos:theme")||"system";var d=t==="dark"||(t==="system"&&window.matchMedia("(prefers-color-scheme: dark)").matches);if(d){document.documentElement.classList.add("dark");}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={GeistSans.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
