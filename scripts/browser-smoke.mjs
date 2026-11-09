import { chromium } from 'playwright';
import { existsSync } from 'node:fs';

const systemChrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const baseUrl = process.env.SIGNTALK_BASE_URL || 'http://localhost:5173';
const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_EXECUTABLE_PATH ? { executablePath: process.env.CHROME_EXECUTABLE_PATH } : existsSync(systemChrome) ? { executablePath: systemChrome } : {}), args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(2500);
const story = await page.locator('.story').evaluate(element => ({ top: element.offsetTop, height: element.offsetHeight }));
const shots = [];
const sceneCounters = [];
for (const progress of [0, .25, .5, .75, 1]) {
  await page.evaluate(({ story, progress }) => scrollTo(0, story.top + progress * (story.height - innerHeight)), { story, progress });
  await page.waitForTimeout(500);
  const path = `docs/qa-shots/desktop-${progress * 100}.png`;
  await page.screenshot({ path });
  shots.push(path);
  sceneCounters.push(await page.locator('.scene-counter').innerText());
}
const webgl = await page.locator('canvas').evaluate(canvas => ({ width: canvas.width, height: canvas.height, webgl: !!(canvas.getContext('webgl2') || canvas.getContext('webgl')) }));
await page.goto(`${baseUrl}/learn`, { waitUntil: 'domcontentloaded' });
await page.getByPlaceholder('Cari kata dalam Inggris atau Indonesia').fill('hello');
const searchResults = await page.locator('.lesson').count();
await page.locator('.lesson').first().click();
await page.waitForURL('**/learn/hello');
await page.waitForSelector('.source-visual a[href^="https://www.youtube.com/watch?v="]');
const lessonVideoClean = await page.locator('.source-media-card iframe').count() === 0;
const detailWorks = await page.locator('.source-visual a[href^="https://www.youtube.com/watch?v="]').isVisible() && lessonVideoClean && await page.locator('.teaching-steps li').count() >= 2 && await page.locator('.lesson-side-column').isVisible();
const detailDiagnostic = { url: page.url(), title: await page.locator('h1').first().textContent(), embeddedPlayers: await page.locator('.source-media-card iframe').count(), teachingSteps: await page.locator('.teaching-steps li').count(), rightColumnVisible: await page.locator('.lesson-side-column').isVisible(), main: (await page.locator('main').innerText()).slice(0,180) };
await page.goto(`${baseUrl}/phrases`, { waitUntil: 'domcontentloaded' });
const phraseCount = await page.locator('.lesson').count();
await page.locator('.lesson').first().click();
await page.waitForURL('**/phrases/thank-you');
await page.waitForSelector('.source-demo-asset');
const phraseVideoWorks = await page.locator('.source-demo-asset').isVisible() && await page.locator('.source-media-card iframe').count() === 0 && await page.locator('.source-text-link[href^="https://www.youtube.com/watch?v="]').isVisible();
await page.goto(`${baseUrl}/practice/asl-who`, { waitUntil: 'domcontentloaded' });
const cleanSourceDemo = { url: await page.locator('.practice-demo-video img.source-demo-asset').getAttribute('src'), noYoutubeChrome: await page.locator('.practice-demo-video iframe').count() === 0 };
await page.setViewportSize({ width: 360, height: 844 });
await page.goto(`${baseUrl}/about`, { waitUntil: 'domcontentloaded' });
const aboutHasNoOverflow = await page.evaluate(() => document.documentElement.scrollWidth === innerWidth);
await page.goto(`${baseUrl}/learn/hello`, { waitUntil: 'domcontentloaded' });
const lessonResponsive = await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, instructionCount: document.querySelectorAll('.teaching-steps li').length, sideColumnVisible: (() => { const box=document.querySelector('.lesson-side-column')?.getBoundingClientRect(); return !!box && box.width>0 && box.right<=innerWidth; })() }));
await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1000);
const responsive = [];
for (const width of [360, 390, 430, 768, 1024, 1440]) {
  await page.setViewportSize({ width, height: width < 500 ? 844 : 900 });
  responsive.push(await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, headingVisible: document.querySelector('h1').getBoundingClientRect().right <= innerWidth })));
}
const mobile = responsive.find(view => view.width === 390);
const mobilePage = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
await mobilePage.goto(baseUrl, { waitUntil: 'domcontentloaded' });
await mobilePage.waitForTimeout(2000);
await mobilePage.screenshot({ path: 'docs/qa-shots/mobile-390.png' });
const mobileCanvas = await mobilePage.evaluate(() => ({ canvases: [...document.querySelectorAll('canvas')].map(canvas => ({ width: canvas.width, height: canvas.height, rect: canvas.getBoundingClientRect().toJSON(), display: getComputedStyle(canvas).display, visibility: getComputedStyle(canvas).visibility })), fallback: !!document.querySelector('.webgl-fallback'), reduced: matchMedia('(prefers-reduced-motion: reduce)').matches }));
await page.addInitScript(() => { Object.defineProperty(navigator, 'mediaDevices', { configurable: true, value: { getUserMedia: () => Promise.reject(new DOMException('Permission denied', 'NotAllowedError')) } }); });
await page.goto(`${baseUrl}/practice/hello`, { waitUntil: 'domcontentloaded' });
await page.getByRole('button', { name: 'Aktifkan kamera' }).click();
await page.getByRole('button', { name: 'Coba lagi' }).waitFor();
const permissionDeniedHandled = await page.getByText(/Izin kamera ditolak/).isVisible();
const cameraContext = await browser.newContext({ permissions: ['camera'], viewport: { width: 1280, height: 900 } });
const cameraPage = await cameraContext.newPage();
const cameraErrors = [];
cameraPage.on('pageerror', error => cameraErrors.push(error.message));
cameraPage.on('requestfailed', request => cameraErrors.push(`request failed: ${request.url()} ${request.failure()?.errorText}`));
cameraPage.on('response', response => { if (response.status() >= 400) cameraErrors.push(`HTTP ${response.status()}: ${response.url()}`); });
await cameraPage.goto(`${baseUrl}/practice/hello`, { waitUntil: 'domcontentloaded' });
const cameraApi = await cameraPage.evaluate(() => ({ secure: isSecureContext, mediaDevices: !!navigator.mediaDevices, getUserMedia: !!navigator.mediaDevices?.getUserMedia }));
await cameraPage.getByRole('button', { name: 'Aktifkan kamera' }).click();
await cameraPage.waitForTimeout(2000);
let mediaPipeInitialized = false;
try {
  await cameraPage.locator('.tracking-status').waitFor({ timeout: 45000 });
  await cameraPage.waitForFunction(() => /Mencari tangan|Tangan belum terlihat|tangan terlacak/i.test(document.querySelector('.tracking-status')?.textContent || ''), null, { timeout: 45000 });
  mediaPipeInitialized = true;
} catch { /* report actual camera/model initialization failure below */ }
let liveCoachWorks = false;
let practiceVideoHasNoEmbeddedPlayer = false;
if (mediaPipeInitialized) {
  try {
    await cameraPage.locator('.coach-message').waitFor({ timeout: 10000 });
    await cameraPage.locator('.coach-cue').waitFor({ timeout: 10000 });
    await cameraPage.locator('.coach-response .coach-demo-fallback a[href^="https://www.youtube.com/watch?v="]').waitFor({ timeout: 15000 });
    practiceVideoHasNoEmbeddedPlayer = await cameraPage.locator('.coach-response iframe').count() === 0;
    await cameraPage.getByRole('button', { name: 'Dengarkan coach' }).click();
    liveCoachWorks = await cameraPage.getByRole('button', { name: 'Matikan suara coach' }).isVisible() && practiceVideoHasNoEmbeddedPlayer;
  } catch { /* report actual video/coach availability below */ }
}
let optionalVisionInitialized = false;
if (mediaPipeInitialized) {
  try {
    await cameraPage.getByLabel('Lacak landmark wajah (deteksi saja)').check();
    await cameraPage.waitForFunction(() => /Wajah: (mencari|terdeteksi)/.test(document.querySelector('.vision-status')?.textContent || ''), null, { timeout: 45000 });
    await cameraPage.getByLabel('Lacak landmark tubuh (deteksi saja)').check();
    await cameraPage.waitForFunction(() => /Tubuh\/pose: (mencari|terdeteksi)/.test(document.querySelector('.vision-status')?.textContent || ''), null, { timeout: 45000 });
    optionalVisionInitialized = true;
  } catch { /* optional face/pose must not gate hand-only operation */ }
}
let attemptPersisted = false;
let trackingStatus = '';
let optionalVisionStatus = '';
if (mediaPipeInitialized) {
  trackingStatus = await cameraPage.locator('.tracking-status').innerText();
  optionalVisionStatus = await cameraPage.locator('.vision-status').innerText();
  await cameraPage.getByRole('button', { name: 'Selesaikan sesi' }).click();
  await cameraPage.waitForURL('**/challenge/hello/result/**');
  await cameraPage.goto(`${baseUrl}/progress`, { waitUntil: 'domcontentloaded' });
  attemptPersisted = await cameraPage.getByText(/1 sesi kamera tercatat/).isVisible();
}
const fallbackContext = await browser.newContext({ viewport: { width: 1280, height: 800 } });
await fallbackContext.addInitScript(() => {
  const original = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, ...args) {
    if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') return null;
    return original.call(this, type, ...args);
  };
});
const fallbackPage = await fallbackContext.newPage();
await fallbackPage.goto(baseUrl, { waitUntil: 'domcontentloaded' });
let webglFallback = false;
try { await fallbackPage.locator('.webgl-fallback').waitFor({ timeout: 10000 }); webglFallback = true; } catch { /* canvas did not trigger fallback */ }
const reducedPage = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await reducedPage.emulateMedia({ reducedMotion: 'reduce' });
await reducedPage.goto(baseUrl, { waitUntil: 'domcontentloaded' });
await reducedPage.evaluate(() => scrollTo(0, 500));
const reducedMotionUsable = await reducedPage.getByRole('link', { name: /Jelajahi materi/ }).isVisible();
const cameraState = await cameraPage.locator('main').innerText();
const mediaRequests = await cameraPage.evaluate(() => performance.getEntriesByType('resource').map(entry=>entry.name).filter(name=>name.includes('mediapipe')||name.includes('hand_landmarker')));
const blockingCameraErrors = cameraErrors.filter(message => {
  const expectedExternalAbort = message.includes('ERR_ABORTED') && (message.includes('youtube.com') || message.includes('googlevideo.com') || message.includes('yt3.ggpht.com') || message.includes('fonts.gstatic.com'));
  const optionalVisionTelemetryAbort = message.includes('odml.pa.googleapis.com') && message.includes('ERR_ABORTED');
  return !expectedExternalAbort && !optionalVisionTelemetryAbort;
});
console.log(JSON.stringify({ shots, sceneCounters, webgl, searchResults, detailWorks, lessonVideoClean, phraseCount, phraseVideoWorks, cleanSourceDemo, aboutHasNoOverflow, lessonResponsive, responsive, mobileCanvas, permissionDeniedHandled, cameraApi, mediaPipeInitialized, liveCoachWorks, practiceVideoHasNoEmbeddedPlayer, optionalVisionInitialized, optionalVisionStatus, trackingStatus, attemptPersisted, webglFallback, reducedMotionUsable, cameraState: cameraState.slice(-350), mediaRequests, cameraErrors, errors }, null, 2));
await reducedPage.close();
await mobilePage.close();
await fallbackContext.close();
await browser.close();
if (!webgl.webgl || !webgl.width || !webgl.height || searchResults !== 1 || !detailWorks || phraseCount < 2 || !phraseVideoWorks || !cleanSourceDemo.url || !cleanSourceDemo.noYoutubeChrome || !aboutHasNoOverflow || lessonResponsive.scrollWidth > lessonResponsive.width || lessonResponsive.instructionCount < 2 || !lessonResponsive.sideColumnVisible || !permissionDeniedHandled || !mediaPipeInitialized || !liveCoachWorks || !practiceVideoHasNoEmbeddedPlayer || !optionalVisionInitialized || !attemptPersisted || !webglFallback || !reducedMotionUsable || !(mobileCanvas.fallback || mobileCanvas.canvases.some(canvas => canvas.rect.width === 390)) || responsive.some(view => view.scrollWidth > view.width || !view.headingVisible) || errors.length || blockingCameraErrors.length) process.exitCode = 1;
