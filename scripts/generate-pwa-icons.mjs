import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const chromePath = process.env.CHROME_EXECUTABLE_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await chromium.launch({ headless: true, ...(existsSync(chromePath) ? { executablePath: chromePath } : {}) });
const page = await browser.newPage({ deviceScaleFactor: 1 });
const svg = readFileSync('public/pwa-icon.svg').toString('base64');
const outputDir = resolve('public/pwa');
mkdirSync(outputDir, { recursive: true });
for (const size of [180, 192, 512]) {
  await page.setViewportSize({ width: size, height: size });
  await page.setContent(`<html><body style="margin:0;width:${size}px;height:${size}px"><img style="display:block;width:${size}px;height:${size}px" src="data:image/svg+xml;base64,${svg}"/></body></html>`);
  await page.locator('img').screenshot({ path: resolve(outputDir, `icon-${size}.png`) });
}
await browser.close();
console.log('Generated original SIGNTALK 180×180 Apple and 192×192/512×512 PWA PNG icons from public/pwa-icon.svg.');
