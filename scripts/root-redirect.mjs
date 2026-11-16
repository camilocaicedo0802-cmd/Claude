#!/usr/bin/env node
/**
 * The site root used to hold the video editor portfolio, which is now part of the main one
 * under /disenador/. This writes, into the Pages folder:
 *   index.html  a redirect to the portfolio
 *   404.html    the portfolio's 404 page, which first sends old root URLs (the home page and
 *               trabajo-<slug>.html project pages) to the same page under /disenador/
 *
 * Usage: node scripts/root-redirect.mjs <pages-folder> <base-url>
 *   e.g. node scripts/root-redirect.mjs _site https://user.github.io/repo
 */
import fs from "node:fs";
import path from "node:path";

const [dir, baseUrl] = process.argv.slice(2);
if (!dir || !baseUrl) {
  console.error("Usage: node scripts/root-redirect.mjs <pages-folder> <base-url>");
  process.exit(1);
}
const base = baseUrl.replace(/\/$/, "");
const root = new URL(base).pathname.replace(/\/$/, "");
const portfolio = `${base}/disenador/`;

fs.writeFileSync(
  path.join(dir, "index.html"),
  `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Juan Camilo Caicedo | Editor de video y diseñador digital</title>
<link rel="canonical" href="${portfolio}">
<meta http-equiv="refresh" content="0; url=${portfolio}">
<script>location.replace(${JSON.stringify(portfolio)} + location.hash);</script>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#080808;color:#fff;font:16px/1.5 system-ui,sans-serif}a{color:#fff}</style>
</head>
<body><p><a href="${portfolio}">Ir al portafolio de Juan Camilo Caicedo</a></p></body>
</html>
`,
);

// Old root URLs go to the same page in the portfolio; real misses inside it keep the 404 page.
const redirect = `<script>(function(){var r=${JSON.stringify(root)},p=location.pathname;if(p.indexOf(r+"/disenador/")===0||p.indexOf(r+"/life-os/")===0)return;var m=p.match(/\\/(trabajo-[\\w-]+\\.html)$/);location.replace(r+"/disenador/"+(m?m[1]:"")+location.hash);})();</script>`;
const notFound = fs.readFileSync(path.join(dir, "disenador", "404.html"), "utf8");
if (!notFound.includes("<head>")) throw new Error("404.html has no <head>");
// Its relative URLs must resolve inside /disenador/ whatever path GitHub serves it under.
fs.writeFileSync(path.join(dir, "404.html"), notFound.replace("<head>", `<head>${redirect}<base href="${portfolio}">`));
console.log(`root-redirect: ${dir}/index.html and ${dir}/404.html point to ${portfolio}`);
