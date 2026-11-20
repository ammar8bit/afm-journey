// Capture the README screenshots from the built page with headless Edge/Chrome.
//   python scripts/build.py && node scripts/screenshots.mjs
// Uses the DevTools protocol directly (Node 22+, no npm packages). Set BROWSER to override the browser path.
import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const page = pathToFileURL(resolve(root, "dist/index.html")).href;
const outDir = resolve(root, "docs/screenshots");
const browser = process.env.BROWSER || [
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "/usr/bin/google-chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].find(existsSync);
if (!browser) throw new Error("No Edge/Chrome found; set BROWSER");

const shots = [
  { name: "hero", width: 1440, height: 900, target: null },
  { name: "overview", width: 1440, height: 900, target: "#overview", offset: 40 },
  { name: "plan", width: 1440, height: 900, target: "#plan", click: '.prow[data-day="11"]' },
  { name: "library", width: 1440, height: 900, target: "#library", offset: 110 },
];

const port = 9333;
const proc = spawn(browser, ["--headless=new", `--remote-debugging-port=${port}`, "--hide-scrollbars",
  "--force-prefers-reduced-motion", "--user-data-dir=" + resolve(root, "dist/.shot-profile"), "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));

let wsUrl;
for (let i = 0; i < 50 && !wsUrl; i++) {
  await sleep(200);
  try { wsUrl = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === "page")?.webSocketDebuggerUrl; } catch {}
}
const ws = new WebSocket(wsUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const pending = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
const evaluate = expression => send("Runtime.evaluate", { expression, awaitPromise: true });

mkdirSync(outDir, { recursive: true });
for (const s of shots) {
  await send("Emulation.setDeviceMetricsOverride", { width: s.width, height: s.height, deviceScaleFactor: 1.5, mobile: false });
  await send("Page.navigate", { url: page });
  await sleep(1500);
  await evaluate(`document.fonts.ready`);
  if (s.target) await evaluate(`window.scrollTo(0, document.querySelector('${s.target}').getBoundingClientRect().top + scrollY - ${s.offset || 0}); new Promise(r => setTimeout(r, 600))`);
  if (s.click) await evaluate(`document.querySelector('${s.click}').click(); new Promise(r => setTimeout(r, 500))`);
  const { result } = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(resolve(outDir, `${s.name}.png`), Buffer.from(result.data, "base64"));
  console.log("saved", `docs/screenshots/${s.name}.png`);
}
ws.close(); proc.kill();
