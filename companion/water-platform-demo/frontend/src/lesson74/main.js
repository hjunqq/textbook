// S5 阶段页（7.3–7.4 节）：真实观测曲线与三维对象联动。
// 运行依赖 S3 与 S4——先有能返回观测的接口（教学接口或第5章的后端），
// 再有第6章绑好测点的场景，本页只做“把两者连起来”这一件事。
//
// 启动：node teaching-api/server.mjs   然后 npm run dev，打开 /lesson74.html

import * as echarts from 'echarts';
import '../lesson61/first-scene.js';                 // 复用 S4 的场景（它把 scene 挂到 window）
import { bindAssets } from '../lesson61/bind-assets.js';
import { createSceneBus } from './scene-bus.js';
import { createLinkController } from './link.js';
import { PointPicker, firstAsset } from './picker.js';
import { toChartPoints, readingQuery, qualityText } from '../utils/readings.js';

const TOKEN_HEADER = token => ({ Authorization: `Bearer ${token}` });

async function login() {
  const r = await fetch('/api/auth/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'duty01', password: 'duty123' }),
  });
  return (await r.json()).accessToken;
}

const token = await login();
const auth = TOKEN_HEADER(token);

// —— 场景：复用 S4 的绑定结果 ——
const assets = await (await fetch('/api/assets', { headers: auth })).json();
const ledger = await (await fetch('/datasets/stations.json')).json();
const bound = bindAssets(window.scene,
  assets.map(a => ({ ...a, ...ledger.find(s => s.asset_id === a.assetId) })));
const sceneBus = createSceneBus(bound);

// 拾取：点击画布 → 射线求交 → 找回业务对象 → 广播 select
const picker = new PointPicker(window.camera, window.scene, window.renderer.domElement);
window.renderer.domElement.addEventListener('click', event => {
  const mesh = firstAsset(picker.pick(event.clientX, event.clientY));
  if (!mesh) { status.textContent = '未选中测点（点到的是坝体或空白处）'; return; }
  sceneBus.select(mesh);
});

// —— 曲线：取一个对象在时间窗内的观测 ——
const status = document.querySelector('#status');
const chart = echarts.init(document.querySelector('#chart'));

// 时间窗取数据集覆盖的那一天；readingQuery 会校验左闭右开与先后顺序
const range = readingQuery({ from: '2026-07-01T00:00:00+08:00', to: '2026-07-02T00:00:00+08:00' });

async function loadSeries(assetId) {
  const query = new URLSearchParams(range).toString();
  const res = await fetch(`/api/assets/${assetId}/readings?${query}`, { headers: auth });
  if (res.status === 204) return [];
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message ?? `读取观测失败（${res.status}）`);
  }
  return res.json();
}

let unlink = () => {};

async function showAsset(assetId) {
  status.textContent = `正在读取 ${assetId} 的观测…`;
  const readings = await loadSeries(assetId);
  if (readings.length === 0) {
    chart.clear();
    status.textContent = `${assetId}：暂无观测`;
    return;
  }
  chart.setOption({
    xAxis: { type: 'time' },
    yAxis: { type: 'value', scale: true, name: readings[0].unit },
    series: [{
      id: 'level', type: 'line', showSymbol: false,
      connectNulls: false,               // 缺测必须断开，不能连成一条直线
      data: toChartPoints(readings),
    }],
  }, true);

  // 每次换对象都重建联动：旧的解绑函数不调用，点击处理器会一层层叠加
  unlink();
  unlink = createLinkController(chart, sceneBus, readings);
  const bad = readings.filter(r => r.quality !== 'valid').length;
  status.textContent = `${assetId}：${readings.length} 条观测`
    + (bad ? `，其中 ${bad} 条非${qualityText.valid}` : '');
}

sceneBus.on('select', mesh => showAsset(mesh.userData.assetId));

// 打开页面时先显示一个有观测的对象，避免空白页
await showAsset('DAM-A-PZ-07');
sceneBus.focusAsset('DAM-A-PZ-07');

addEventListener('beforeunload', () => { unlink(); sceneBus.dispose(); chart.dispose(); });
window.sceneBus = sceneBus;   // 控制台可用：sceneBus.focusAsset('DAM-A-WL-01')
