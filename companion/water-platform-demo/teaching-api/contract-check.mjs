// 契约核对：把教材表 tab:ch05-first-verify（第一个接口的契约核对单）与
// tab:api-contract 的通用约定变成可执行的检查。
//
// 同一个脚本对三种数据来源都应当全绿——这就是“教学接口可替换”的含义：
//   node teaching-api/server.mjs                                     # 教学接口
//   mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson52.Lesson52Application
//   mvn spring-boot:run                                              # 完整后端（需数据库）
//
// 用法：node teaching-api/contract-check.mjs [baseUrl] [--stage=teaching|lesson52|full]
//   node teaching-api/contract-check.mjs http://localhost:8080 --stage=teaching
//
// 三种来源的数据深度不同，所以分阶段裁剪期望：
//   teaching  固定数据集全量（28 个对象），支持 teach= 故障注入
//   lesson52  5.2 节的四个写死对象，只有 DAM-A-PZ-07 有观测
//   full      真实数据库，对象与观测由 db/002_seed.sql 决定
// 但**契约形状**（状态码、字段名、错误体）三者必须完全一致，这才是核对的重点。

const args = process.argv.slice(2);
const base = (args.find(a => a.startsWith('http')) ?? 'http://localhost:8080').replace(/\/$/, '');
const stage = (args.find(a => a.startsWith('--stage='))?.slice(8)) ?? 'teaching';
if (!['teaching', 'lesson52', 'full'].includes(stage)) {
  console.error(`未知阶段 ${stage}，可选 teaching / lesson52 / full`);
  process.exit(2);
}

let pass = 0, fail = 0;
const results = [];
function check(name, condition, detail = '') {
  if (condition) { pass++; results.push(['OK  ', name, '']); }
  else { fail++; results.push(['FAIL', name, detail]); }
}

async function call(path, options = {}) {
  const res = await fetch(base + path, options);
  const text = await res.text();
  let json = null;
  try { json = text === '' ? null : JSON.parse(text); } catch { /* 非 JSON 保持 null */ }
  return { status: res.status, json, text };
}

// 认证：教学接口与完整后端要求令牌，lesson52 阶段还没有认证（5.6 节才加）
async function login() {
  if (stage === 'lesson52') return {};
  const res = await call('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'duty01', password: 'duty123' }),
  });
  check('POST /api/auth/login 返回 200 与 accessToken',
    res.status === 200 && typeof res.json?.accessToken === 'string',
    `status=${res.status} body=${res.text.slice(0, 120)}`);
  check('登录响应含 expiresInSeconds 与 authorities',
    typeof res.json?.expiresInSeconds === 'number' && Array.isArray(res.json?.authorities),
    JSON.stringify(res.json)?.slice(0, 120));
  return res.json?.accessToken ? { Authorization: `Bearer ${res.json.accessToken}` } : {};
}

// 错误体必须是 {code, message, field?}——8.1 节通用约定
function isContractError(json, expectedCode, expectedField) {
  if (!json || typeof json.code !== 'string' || typeof json.message !== 'string') return false;
  if (expectedCode && json.code !== expectedCode) return false;
  if (expectedField && json.field !== expectedField) return false;
  return true;
}

const run = async () => {
  const auth = await login();
  const h = { headers: auth };

  // —— 契约第 2 行：对象列表 ——
  const assets = await call('/api/assets', h);
  check('GET /api/assets 返回 200 与数组',
    assets.status === 200 && Array.isArray(assets.json),
    `status=${assets.status}`);
  const first = assets.json?.[0];
  check('对象字段为 assetId/displayName/assetType/unit（驼峰，不是下划线）',
    first && 'assetId' in first && 'displayName' in first
      && 'assetType' in first && 'unit' in first && !('asset_id' in first),
    JSON.stringify(first));
  if (stage === 'lesson52') {
    check('5.2 节固定数据为 4 个对象', assets.json?.length === 4, `${assets.json?.length}`);
    check('位移测点编码与台账一致（DAM-A-D-01）',
      assets.json?.some(a => a.assetId === 'DAM-A-D-01'),
      JSON.stringify(assets.json?.map(a => a.assetId)));
  }

  // —— 核对单第 1 行：有观测的对象 200 ——
  const latest = await call('/api/assets/DAM-A-PZ-07/readings/latest', h);
  check('GET …/DAM-A-PZ-07/readings/latest 返回 200',
    latest.status === 200, `status=${latest.status} body=${latest.text.slice(0, 120)}`);
  check('观测字段为 assetId/occurredAt/value/unit/quality',
    latest.json && ['assetId', 'occurredAt', 'value', 'unit', 'quality']
      .every(k => k in latest.json),
    JSON.stringify(latest.json));
  check('质量码取 valid/suspect/missing 之一',
    ['valid', 'suspect', 'missing'].includes(latest.json?.quality),
    `quality=${latest.json?.quality}`);

  // —— 核对单第 2 行：对象存在但无观测 204 ——
  //     教学接口与完整后端的无观测对象是位移测点；lesson52 阶段是除 PZ-07 外的任意一个
  const emptyId = stage === 'lesson52' ? 'DAM-A-WL-01' : 'DAM-A-D-01';
  const empty = await call(`/api/assets/${emptyId}/readings/latest`, h);
  check(`GET …/${emptyId}/readings/latest 返回 204（无观测，不是 404 也不是 200）`,
    empty.status === 204, `status=${empty.status} body=${empty.text.slice(0, 120)}`);
  check('204 响应体为空', empty.text === '', JSON.stringify(empty.text));

  // —— 核对单第 3 行：对象不存在 404 + 契约错误体 ——
  const missing = await call('/api/assets/DAM-A-XX-99/readings/latest', h);
  check('GET …/DAM-A-XX-99/readings/latest 返回 404',
    missing.status === 404, `status=${missing.status}`);
  check('404 错误体为 {code:"ASSET_NOT_FOUND", message}',
    isContractError(missing.json, 'ASSET_NOT_FOUND'),
    missing.text.slice(0, 160));

  // —— 核对单第 4 行：from 晚于 to → 400 且 field 为 from ——
  const bad = await call('/api/assets/DAM-A-PZ-07/readings'
    + '?from=2026-07-02T00%3A00%3A00%2B08%3A00&to=2026-07-01T00%3A00%3A00%2B08%3A00', h);
  check('from 晚于 to 返回 400', bad.status === 400, `status=${bad.status}`);
  check('400 错误体为 {code:"INVALID_RANGE", field:"from"}',
    isContractError(bad.json, 'INVALID_RANGE', 'from'), bad.text.slice(0, 160));

  // —— 5.2.2“一个会遇到的失败”：+ 号未编码，解析失败发生在进入方法之前 ——
  const plus = await call('/api/assets/DAM-A-PZ-07/readings'
    + '?from=2026-07-01T00:00:00 08:00&to=2026-07-02T00%3A00%3A00%2B08%3A00', h);
  check('时间参数无法解析时返回 400', plus.status === 400, `status=${plus.status}`);
  check('该 400 也必须是契约错误体，而不是框架默认页面',
    isContractError(plus.json), plus.text.slice(0, 160));

  // —— 通用约定：未认证 401 ——
  if (stage !== 'lesson52') {
    const anon = await call('/api/assets');
    check('不带令牌访问返回 401', anon.status === 401, `status=${anon.status}`);
    check('401 错误体为契约形状', isContractError(anon.json), anon.text.slice(0, 160));
  }

  // —— 故障注入只有教学接口认识，真实后端必须忽略 teach= ——
  if (stage === 'teaching') {
    const t0 = Date.now();
    const delayed = await call('/api/assets/DAM-A-PZ-07/readings/latest?teach=delay:800', h);
    check('teach=delay:800 延迟后仍正常返回',
      delayed.status === 200 && Date.now() - t0 >= 700, `status=${delayed.status}`);
    const unauth = await call('/api/assets?teach=unauthorized', h);
    check('teach=unauthorized 返回 401 与契约错误体',
      unauth.status === 401 && isContractError(unauth.json), unauth.text.slice(0, 160));
    const invalid = await call('/api/assets?teach=invalid', h);
    check('teach=invalid 返回 400 且 field 为 from',
      invalid.status === 400 && isContractError(invalid.json, 'INVALID_RANGE', 'from'),
      invalid.text.slice(0, 160));
  } else {
    const ignored = await call('/api/assets?teach=unauthorized', h);
    check('真实后端忽略 teach= 参数（仍返回 200）',
      ignored.status === 200, `status=${ignored.status}`);
  }
};

run().then(() => {
  for (const [tag, name, detail] of results) {
    console.log(`  ${tag} ${name}${detail ? '  << ' + detail : ''}`);
  }
  console.log(`\n阶段 ${stage} @ ${base}：通过 ${pass}，失败 ${fail}`);
  finish(fail ? 1 : 0);
}).catch(err => {
  console.error(`无法连接 ${base}：${err.message}`);
  console.error('先启动对应的服务，再运行本脚本。');
  finish(2);
});

// 退出：设置退出码后主动关掉 fetch 的连接池再退出。
// 直接调 process.exit() 会与 undici 尚未关闭的 keep-alive 套接字竞争，
// 在 Windows 上偶发 libuv 断言（退出码 127），CI 里会被误读成脚本失败。
async function finish(code) {
  process.exitCode = code;
  try { await globalThis[Symbol.for('undici.globalDispatcher.1')]?.close(); } catch { /* 忽略 */ }
}
