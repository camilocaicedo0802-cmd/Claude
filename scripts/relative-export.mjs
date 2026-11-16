#!/usr/bin/env node
/**
 * Turns an export built with NEXT_PUBLIC_RELATIVE_EXPORT=1 into a flat folder
 * that works from any sub-path or plain file host:
 *   _next/                     -> assets/_next/ (where assetPrefix points)
 *   trabajos/<slug>/index.html -> trabajo-<slug>.html
 *   landings/<slug>/index.html -> landing-<slug>.html
 * and removes the RSC payloads (.txt) that only client-side navigation uses.
 *
 * Usage: node scripts/relative-export.mjs disenador
 */
import fs from "node:fs";
import path from "node:path";

const app = process.argv[2];
if (!["disenador"].includes(app)) {
  console.error("Usage: node scripts/relative-export.mjs disenador");
  process.exit(1);
}
const out = path.join(import.meta.dirname, "..", "apps", app, "out");
const home = path.join(out, "index.html");
if (!fs.existsSync(home) || !fs.readFileSync(home, "utf8").includes('"./assets/_next/')) {
  console.error(`${out} is not a relative build. Run: NEXT_PUBLIC_RELATIVE_EXPORT=1 npm run build:${app}`);
  process.exit(1);
}

// Build files to where assetPrefix points.
const assets = path.join(out, "assets");
if (fs.existsSync(path.join(out, "_next"))) {
  fs.rmSync(assets, { recursive: true, force: true });
  fs.mkdirSync(assets);
  fs.renameSync(path.join(out, "_next"), path.join(assets, "_next"));
}

// Case studies and landing pages to the root, so every page shares the same relative base.
let moved = 0;
for (const [folder, prefix] of [["trabajos", "trabajo-"], ["landings", "landing-"]]) {
  const dir = path.join(out, folder);
  for (const slug of fs.existsSync(dir) ? fs.readdirSync(dir) : []) {
    const page = path.join(dir, slug, "index.html");
    if (!fs.existsSync(page)) continue;
    fs.renameSync(page, path.join(out, `${prefix}${slug}.html`));
    moved++;
  }
  fs.rmSync(dir, { recursive: true, force: true });
}

// RSC payloads and route folders left without pages.
for (const name of fs.readdirSync(out)) {
  const full = path.join(out, name);
  if (name.endsWith(".txt") && name !== "robots.txt") fs.rmSync(full);
  else if (name === "_not-found" || name === "404") fs.rmSync(full, { recursive: true, force: true });
}

// Root-relative leftovers that Next writes regardless of assetPrefix.
const leftovers = [];
for (const name of fs.readdirSync(out).filter((n) => n.endsWith(".html"))) {
  const file = path.join(out, name);
  const html = fs
    .readFileSync(file, "utf8")
    .replace('<link rel="preconnect" href="/" crossorigin=""/>', "")
    .replaceAll("/icon.svg?", "icon.svg?");
  fs.writeFileSync(file, html);
  for (const m of html.matchAll(/(?:src|href)=\\?"(\/[^/"\\][^"\\]*)/g)) leftovers.push(`${name}: ${m[1]}`);
}

console.log(`${app}: ${moved} pages flattened into ${path.relative(process.cwd(), out)}`);
if (leftovers.length) {
  console.error(`Root-relative URLs left:\n  ${[...new Set(leftovers)].join("\n  ")}`);
  process.exit(1);
}
