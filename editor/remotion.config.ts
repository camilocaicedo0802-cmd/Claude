/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Entorno sin acceso a remotion.media: usa el Chromium preinstalado si existe.
import fs from "node:fs";
const chromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
if (fs.existsSync(chromium)) {
  Config.setBrowserExecutable(chromium);
}
