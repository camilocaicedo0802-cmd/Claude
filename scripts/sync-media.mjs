// Copies the transcoded media (media/out) into an app's public/media folder.
// Runs automatically before `dev` and `build`. Skipped when NEXT_PUBLIC_MEDIA_BASE
// points to an external CDN, because then the files are served from there.
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const app = process.argv[2];
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(root, "media", "out");
const dest = join(root, "apps", app, "public", "media");

if (process.env.NEXT_PUBLIC_MEDIA_BASE) {
  console.log(`sync-media: NEXT_PUBLIC_MEDIA_BASE is set, skipping copy for ${app}`);
  process.exit(0);
}
if (!existsSync(src)) {
  console.error("sync-media: media/out not found. Run `npm run media:build` first.");
  process.exit(1);
}
rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
for (const dir of ["videos", "previews", "posters", "pieces"]) {
  if (existsSync(join(src, dir))) cpSync(join(src, dir), join(dest, dir), { recursive: true });
}
console.log(`sync-media: copied media/out to apps/${app}/public/media`);
