// S0 演示记录生成器（第1章）。
//
// 第1章不要求学生写代码，但要求他们能说明“查看某测点历史观测”这一次操作
// 在六个环节里各发生了什么、出问题时去哪里找证据（1.2.1 节的追踪图）。
// 课堂上未必有可用的演示环境，所以这里把一次完整操作实录成固定文本，
// 教师可以直接投影，学生可以照着对每一环节。
//
// 用法：
//   node teaching-api/server.mjs &
//   node teaching-api/record-demo.mjs > S0-demo-record.md
//
// 记录里的时间戳会随运行变化，但状态码、路径、字段名不会——
// 后者才是要对照 8.1 节契约表检查的东西。

const base = (process.argv[2] ?? 'http://localhost:8080').replace(/\/$/, '');
const out = [];
const say = line => out.push(line);

function preview(text, limit = 220) {
  if (text === '') return '（空响应体）';
  const one = text.replace(/\s+/g, ' ');
  return one.length > limit ? one.slice(0, limit) + ' …（已截断）' : one;
}

async function step(no, title, why, path, options = {}) {
  const started = Date.now();
  const res = await fetch(base + path, options);
  const text = await res.text();
  const ms = Date.now() - started;
  say(`### 环节 ${no}：${title}\n`);
  say(`**这一步在做什么**：${why}\n`);
  say('```http');
  say(`${options.method ?? 'GET'} ${path}`);
  for (const [k, v] of Object.entries(options.headers ?? {})) {
    say(`${k}: ${k === 'Authorization' ? 'Bearer <令牌已省略>' : v}`);
  }
  if (options.body) say(`\n${options.body}`);
  say('```\n');
  say(`**响应**：\`${res.status} ${res.statusText}\`，耗时 ${ms} ms\n`);
  say('```json');
  say(preview(text));
  say('```\n');
  let json = null;
  try { json = text === '' ? null : JSON.parse(text); } catch { /* 非 JSON */ }
  return { status: res.status, json, text, ms };
}

const run = async () => {
  say('# S0 演示记录：一次“查看某测点历史观测”的完整过程\n');
  say('> 本文件由 `teaching-api/record-demo.mjs` 对运行中的教学接口实录生成，');
  say('> 不是手写的示例。对照第1章 1.2.1 节的六环节追踪图阅读。\n');
  say(`> 生成时间：${new Date().toISOString()}　数据来源：教学接口 ${base}\n`);
  say('---\n');

  const login = await step(1, '页面动作 → 身份', '值班员在登录页提交账号口令，页面把它变成一次 HTTP 请求。',
    '/api/auth/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'duty01', password: 'duty123' }),
    });
  const token = login.json?.accessToken;
  const h = { Authorization: `Bearer ${token}` };
  say(`平台发回一个有效期 ${login.json?.expiresInSeconds} 秒的令牌，角色为 `
    + `\`${(login.json?.authorities ?? []).join(', ')}\`。此后每个业务请求都要带上它。\n`);

  await step(2, 'HTTP 请求 → 对象列表', '页面要先知道有哪些测点，才能让用户选一个。',
    '/api/assets', { headers: h });

  await step(3, '服务处理 → 最新观测', '选中案例渗压07 后，页面请求它的最新一条观测。',
    '/api/assets/DAM-A-PZ-07/readings/latest', { headers: h });

  await step(4, '数据查询 → 一段历史', '把时间窗交给平台，取回一段观测用来画曲线。时间必须带时区。',
    '/api/assets/DAM-A-PZ-07/readings'
    + '?from=2026-07-01T00%3A00%3A00%2B08%3A00&to=2026-07-01T02%3A00%3A00%2B08%3A00',
    { headers: h });

  await step(5, '页面更新 → 预警状态', '曲线之外，值班员还要看到这个测点当前有没有预警。',
    '/api/warnings?assetId=DAM-A-PZ-07', { headers: h });

  say('---\n');
  say('## 出问题时去哪里找证据\n');
  say('把上面五个环节各破坏一次，观察平台的回答有什么不同。');
  say('这四种情况都能当场复现，也都是第4章要在页面上分别显示的状态。\n');

  const noToken = await step('6a', '证据一：不带令牌', '模拟令牌过期。页面应当清除令牌并跳转登录页，登录后回到原页面。',
    '/api/assets');
  const notFound = await step('6b', '证据二：编码打错', '模拟用户输错对象编码。404 与 204 必须分开——前者是“没有这个测点”，后者是“有但还没上报”。',
    '/api/assets/DAM-A-XX-99/readings/latest', { headers: h });
  const noReading = await step('6c', '证据三：有测点但没观测', '位移测点在数据集中没有观测记录。页面应显示“暂无观测”，不是报错也不是空白。',
    '/api/assets/DAM-A-D-01/readings/latest', { headers: h });
  const badRange = await step('6d', '证据四：时间窗写反', 'from 晚于 to。错误体里的 field 指出是哪个字段错了，页面据此定位输入框。',
    '/api/assets/DAM-A-PZ-07/readings'
    + '?from=2026-07-02T00%3A00%3A00%2B08%3A00&to=2026-07-01T00%3A00%3A00%2B08%3A00',
    { headers: h });

  say('| 破坏方式 | 状态码 | 错误码 | 页面应有的表现 |');
  say('|---|---|---|---|');
  say(`| 不带令牌 | ${noToken.status} | ${noToken.json?.code ?? '—'} | 清除令牌，跳登录页，登录后回跳 |`);
  say(`| 编码打错 | ${notFound.status} | ${notFound.json?.code ?? '—'} | “对象不存在，请返回列表” |`);
  say(`| 有测点无观测 | ${noReading.status} | ${noReading.json?.code ?? '—'} | “暂无观测”，不是报错 |`);
  say(`| 时间窗写反 | ${badRange.status} | ${badRange.json?.code ?? '—'}（field=${badRange.json?.field ?? '—'}） | 提示到具体字段，保留已输入的值 |`);
  say('');
  say('五个环节里的路径、字段名和错误码，都能在教材 8.1 节的接口契约表里查到。');
  say('如果实录结果与契约表对不上，说明某一端写歪了——这正是第5章契约核对脚本要拦住的事。');
};

run().then(() => {
  console.log(out.join('\n'));
  finish(0);
}).catch(err => {
  console.error(`无法连接 ${base}：${err.message}`);
  console.error('先运行 node teaching-api/server.mjs');
  finish(2);
});

async function finish(code) {
  process.exitCode = code;
  try { await globalThis[Symbol.for('undici.globalDispatcher.1')]?.close(); } catch { /* 忽略 */ }
}
