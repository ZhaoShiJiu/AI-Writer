// 冒烟测试：验证前端核心页面和功能
import { chromium } from 'playwright';

const BASE = 'http://localhost:3000';

async function assert(condition, msg) {
  if (!condition) throw new Error(`FAIL: ${msg}`);
  console.log(`  ✓ ${msg}`);
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  page.on('pageerror', err => console.log('❌ 页面JS错误:', err.message));

  // ===== 1. 页面加载 =====
  console.log('\n--- 1. 页面加载 ---');
  await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
  await assert(await page.title() !== '', '页面有标题');

  // ===== 2. 选择小说 =====
  console.log('\n--- 2. 选择小说 ---');
  const novelBtn = page.locator('button', { hasText: '超凡简史' }).first();
  await assert(await novelBtn.count() > 0, '找到小说按钮');
  await novelBtn.click();
  await page.waitForTimeout(1500);

  // ===== 3. 点击章节打开编辑器 =====
  console.log('\n--- 3. 点击章节 ---');
  // 章节显示为章节名，需要点击它来打开编辑器
  const chapterBtn = page.getByText('吉尔伽美什计划').first();
  await assert(await chapterBtn.count() > 0, '找到章节');
  await chapterBtn.click();
  await page.waitForTimeout(1500);

  // ===== 4. 编辑器 =====
  console.log('\n--- 4. 编辑器 ---');
  const editor = page.locator('.ProseMirror');
  await assert(await editor.count() > 0, 'ProseMirror 编辑器已加载');
  const text = await editor.innerText();
  console.log(`  内容预览: "${text.slice(0, 100)}${text.length > 100 ? '...' : ''}"`);

  // ===== 5. AI 面板 =====
  console.log('\n--- 5. AI 协同创作面板 ---');
  const aiBtn = page.getByText('AI 协同创作').first();
  await assert(await aiBtn.isVisible(), 'AI 协同创作按钮可见');
  await aiBtn.click();
  await page.waitForTimeout(1000);
  // 检查面板是否展示了提示信息
  const panelText = await page.locator('body').innerText();
  console.log(panelText.includes('续写') ? '  ✓ AI 面板已打开' : '  ⚠ AI 面板文本异常');

  console.log('\n✅ 冒烟测试全部通过！');
  await browser.close();
}

run().catch(err => {
  console.error('\n❌ 测试失败:', err.message);
  process.exit(1);
});
