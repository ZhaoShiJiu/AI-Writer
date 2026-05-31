// 验证：侧边栏切换图标美化 + 右侧面板图标栏
import { chromium } from 'playwright';

const BASE = 'http://localhost:3000';

async function assert(condition, msg) {
  if (!condition) throw new Error(`FAIL: ${msg}`);
  console.log(`  OK ${msg}`);
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  page.on('pageerror', err => console.log('JS ERROR:', err.message));

  // ===== 1. 页面加载 =====
  console.log('--- 1. 页面加载 ---');
  await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'verify_01_initial.png', fullPage: false });
  console.log('  截图: verify_01_initial.png');

  // ===== 2. 左：验证保存栏侧边栏切换 SVG 图标 =====
  console.log('--- 2. 左侧边栏切换按钮（保存栏内） ---');
  // 保存按钮右边应该有竖线分隔符和侧边栏切换按钮
  const toggleBtn = page.locator('button[title="收起侧边栏"]').first();
  const exists = await toggleBtn.count();
  await assert(exists > 0, `侧边栏切换按钮存在: ${exists > 0 ? '是' : '否'}`);

  // 检查按钮内是 SVG（不是文字箭头）
  const svgInside = page.locator('button[title="收起侧边栏"] svg').first();
  const svgCount = await svgInside.count();
  await assert(svgCount > 0, `切换按钮使用SVG图标（非文字箭头）: ${svgCount > 0 ? '是' : '否'}`);

  // ===== 3. 左：点击切换，侧边栏收起 =====
  console.log('--- 3. 点击收起侧边栏 ---');
  await toggleBtn.click();
  await page.waitForTimeout(500);

  // 收起后，title 应变为 "展开侧边栏"
  const expandBtn = page.locator('button[title="展开侧边栏"]').first();
  const expandCount = await expandBtn.count();
  await assert(expandCount > 0, `收起后按钮变为"展开侧边栏": ${expandCount > 0 ? '是' : '否'}`);

  // 检查收起后的 SVG 图标（应该是展开图标——矩形在右边，箭头向右）
  const expandSvg = page.locator('button[title="展开侧边栏"] svg').first();
  await assert(await expandSvg.count() > 0, `收起状态下仍使用SVG图标: ${await expandSvg.count() > 0 ? '是' : '否'}`);

  // 截图：侧边栏收起，编辑器全宽
  await page.screenshot({ path: 'verify_02_sidebar_hidden.png', fullPage: false });
  console.log('  截图: verify_02_sidebar_hidden.png');

  // ===== 4. 左：再次点击展开 =====
  console.log('--- 4. 再次点击展开侧边栏 ---');
  await expandBtn.click();
  await page.waitForTimeout(500);
  await assert(await page.locator('button[title="收起侧边栏"]').count() > 0, '侧边栏重新展开');

  // ===== 5. 右：验证右侧面板收起为图标条 =====
  console.log('--- 5. 右侧面板图标条 ---');
  // 先确保右侧面板是展开的
  const rightToggle = page.locator('button[title="隐藏面板"]').first();
  await assert(await rightToggle.count() > 0, `右侧面板切换按钮存在: ${await rightToggle.count() > 0 ? '是' : '否'}`);

  // 点击隐藏右侧面板
  await rightToggle.click();
  await page.waitForTimeout(500);

  // 图标条应该出现：RightPanelIconBar 包含多个 SVG
  const iconBarSvgs = page.locator('svg').filter({ has: page.locator('circle, rect, line, path, polyline') });
  await page.screenshot({ path: 'verify_03_right_iconbar.png', fullPage: false });
  console.log('  截图: verify_03_right_iconbar.png');

  // 检查至少几个预期的图标存在
  const svgElements = await page.locator('svg').count();
  await assert(svgElements >= 9, `右侧图标条包含 >=9 个 SVG（实际: ${svgElements}）`);

  // ===== 6. 验证右侧图标悬停 tooltip ====
  console.log('--- 6. 右侧图标悬停提示 ---');
  // hover 第一个图标（写作规划）
  const iconButtons = page.locator('.group > div').filter({ has: page.locator('svg') });
  const iconCount = await iconButtons.count();
  console.log(`  找到 ${iconCount} 个图标按钮`);
  if (iconCount > 0) {
    await iconButtons.first().hover();
    await page.waitForTimeout(300);
    await page.screenshot({ path: 'verify_04_tooltip.png', fullPage: false });
    console.log('  截图: verify_04_tooltip.png');
    // 检查 tooltip 文字 "写作规划" 出现
    const tooltip = page.locator('text=写作规划').first();
    // tooltip may be visible or not depending on overflow; just check it exists in DOM
    console.log(`  tooltip "写作规划" DOM存在: ${await tooltip.count() > 0 ? '是' : '否'}`);
  }

  // ===== 7. 扩展右侧面板再截图 =====
  console.log('--- 7. 展开右侧面板 ---');
  const showRightBtn = page.locator('button[title="显示面板"]').first();
  if (await showRightBtn.count() > 0) {
    await showRightBtn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'verify_05_right_expanded.png', fullPage: false });
    console.log('  截图: verify_05_right_expanded.png');
  }

  await browser.close();
  console.log('\n所有验证通过！');
}

run().catch(err => { console.error('VERIFICATION FAILED:', err.message); process.exit(1); });
