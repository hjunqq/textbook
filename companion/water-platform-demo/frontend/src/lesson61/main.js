// 6.1 节阶段页：先跑通 first-scene.js（坝体长方体），再把教学接口的对象挂上去
import './first-scene.js';
import { bindAssets } from './bind-assets.js';

// first-scene.js 把 scene 挂在模块作用域里；为了教学页简单，这里重新取一份对象列表并附上台账坐标
async function login() {
  const r = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'duty01', password: 'duty123' }) });
  return (await r.json()).accessToken;
}
const token = await login();
const assets = await (await fetch('/api/assets', { headers: { Authorization: `Bearer ${token}` } })).json();
// 台账坐标（stations.csv）教学接口的 AssetDto 不含坐标，这里从随包的 stations.json 读取
const ledger = await (await fetch('/datasets/stations.json')).json();
const withCoords = assets.map(a => ({ ...a, ...ledger.find(s => s.asset_id === a.assetId) }));
window.bound = bindAssets(window.scene, withCoords);
console.log('已绑定测点数', window.bound.group.children.length);
