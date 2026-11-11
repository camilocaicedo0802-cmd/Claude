import path from "node:path";
import type { NextConfig } from "next";

// LIFE OS is a client-side app (data lives in the browser's IndexedDB), so it exports as a static site
// that can be served from any host. NEXT_PUBLIC_BASE_PATH lets it live under a sub-path (e.g. /life-os).
const basePath = process.env.NEXT_PUBLIC_BASE_PATH?.replace(/\/$/, "") || undefined;

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
  images: { unoptimized: true },
  devIndicators: false,
  turbopack: { root: path.join(__dirname, "..", "..") },
};

export default nextConfig;
