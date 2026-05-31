import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

page.on('pageerror', err => console.log('ERR:', err.message));

await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForTimeout(2000);

await page.locator('text=我是谁').first().click();
await page.waitForTimeout(800);
await page.locator('text=未命名章节').first().click();
await page.waitForTimeout(2000);

// Select text
const pm = page.locator('.ProseMirror');
const box = await pm.boundingBox();
await page.mouse.click(box.x + 200, box.y + 60, { clickCount: 3 });
await page.waitForTimeout(500);

// Click polish
await page.locator('button', { hasText: '润色' }).first().click();
await page.waitForTimeout(500);

// Click start polish
await page.locator('button', { hasText: '开始润色' }).click();

// Wait for result then click replace
await page.waitForSelector('button:has-text("替换原文")', { timeout: 30000 });
await page.locator('button', { hasText: '替换原文' }).click();
await page.waitForTimeout(1000);

// Check editor content
const newContent = await pm.innerHTML();
console.log('Editor content after replace:', newContent);

// Check the word was replaced
const bodyText = await page.locator('.ProseMirror').innerText();
console.log('Editor text:', bodyText);

await browser.close();
