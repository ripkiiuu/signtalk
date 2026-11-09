import { chromium } from 'playwright';
import { existsSync } from 'node:fs';

const executablePath = process.env.CHROME_EXECUTABLE_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await chromium.launch({ headless: true, ...(existsSync(executablePath) ? { executablePath } : {}) });
const context = await browser.newContext();
const page = await context.newPage();
const base = process.env.SIGNTALK_BASE_URL || 'http://localhost:4173';
await page.goto(base, { waitUntil: 'domcontentloaded' });
const registration = await page.evaluate(async () => {
  if (!('serviceWorker' in navigator)) return { supported: false, scope: null };
  const sw = await navigator.serviceWorker.ready;
  return { supported: true, scope: sw.scope, active: !!sw.active };
});
const installAssets = await page.evaluate(async () => {
  const manifest = await (await fetch('/manifest.webmanifest')).json();
  const appleTouchIcon = (await fetch('/pwa/icon-180.png')).status;
  const icons = await Promise.all((manifest.icons || []).map(async icon => ({
    src: icon.src, sizes: icon.sizes, status: (await fetch(icon.src)).status,
  })));
  return { display: manifest.display, appleTouchIcon, icons };
});
await context.setOffline(true);
await page.goto(`${base}/learn`, { waitUntil: 'domcontentloaded', timeout: 15000 });
const offlineCatalog = await page.getByRole('heading', { name: 'Amati. Pahami. Coba.' }).isVisible().catch(() => false);
console.log(JSON.stringify({ registration, installAssets, offlineNavigationLoaded: page.url().includes('/learn'), renderedApp: offlineCatalog }, null, 2));
await browser.close();
if (!registration.supported || !registration.active || installAssets.display !== 'standalone' || installAssets.appleTouchIcon !== 200 || !installAssets.icons.some(icon => icon.sizes === '192x192' && icon.status === 200) || !installAssets.icons.some(icon => icon.sizes === '512x512' && icon.status === 200) || !page.url().includes('/learn') || !offlineCatalog) process.exitCode = 1;
