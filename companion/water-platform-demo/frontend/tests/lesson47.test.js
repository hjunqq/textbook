import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createApp, nextTick } from 'vue';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { useAssetStore } from '../src/stores/asset.js';
import { useAssetSetupStore } from '../src/stores/asset-setup.js';
import { FLOOD_LIMIT_LEVEL, needsWaterLevelAttention } from '../src/api/assets.js';
import Login from '../src/views/Login.vue';
import AssetDetail from '../src/views/AssetDetail.vue';

const A = 'DAM-A-PZ-07';
const B = 'DAM-A-WL-01';
const value = (assetId, extra = {}) => ({ assetId, value: 168, unit: 'm',
  quality: 'valid', occurredAt: '2026-07-01T00:00:00+08:00', ...extra });
let waiting;
let apps;

beforeEach(() => {
  waiting = []; apps = [];
  sessionStorage.clear();
  setActivePinia(createPinia());
  vi.stubGlobal('fetch', vi.fn((path, options) => new Promise((resolve, reject) => {
    waiting.push({ path, options, resolve, reject });
  })));
});

afterEach(() => {
  for (const app of apps) app.unmount();
  document.body.replaceChildren();
  vi.unstubAllGlobals();
});

function reply(index, data, status = 200) {
  waiting[index].resolve(new Response(status === 204 ? null : JSON.stringify(data), {
    status, headers: { 'Content-Type': 'application/json' },
  }));
}

async function flush() {
  for (let i = 0; i < 8; i++) await Promise.resolve();
  await nextTick();
}

for (const [name, useStore] of [['选项式', useAssetStore], ['setup 式', useAssetSetupStore]]) {
  describe(`4.7 ${name} Pinia 参考模块`, () => {
    it('后选对象先返回，迟到旧值不覆盖对象与读数', async () => {
      const store = useStore();
      const old = store.loadLatest(A);
      const selected = store.loadLatest(B);
      expect(store.currentId).toBe(B);
      expect(store.latest).toBeNull();
      reply(1, value(B)); await selected;
      reply(0, value(A)); await old;
      expect(store.currentId).toBe(B);
      expect(store.latest.assetId).toBe(B);
      expect(store.loading).toBe(false);
    });

    it('旧请求先结束不能提早结束当前加载状态', async () => {
      const store = useStore();
      const old = store.loadLatest(A);
      const selected = store.loadLatest(B);
      reply(0, value(A)); await old;
      expect(store.loading).toBe(true);
      expect(store.latest).toBeNull();
      reply(1, value(B)); await selected;
      expect(store.loading).toBe(false);
    });

    it('迟到旧错误不能覆盖当前成功；当前错误可重试', async () => {
      const store = useStore();
      const old = store.loadLatest(A);
      const selected = store.loadLatest(B);
      reply(1, value(B)); await selected;
      waiting[0].reject(new Error('old failure')); await old;
      expect(store.error).toBeNull();
      expect(store.latest.assetId).toBe(B);
      const failed = store.loadLatest(A);
      expect(store.latest).toBeNull();
      reply(2, { code: 'UNAVAILABLE' }, 503); await failed;
      expect(store.error.message).toBe('HTTP_503');
      const retry = store.loadLatest(A);
      reply(3, value(A)); await retry;
      expect(store.latest.assetId).toBe(A);
      expect(store.error).toBeNull();
    });

    it('204 保留选中对象且清空观测；清理后的迟到响应无效', async () => {
      const store = useStore();
      const empty = store.loadLatest(A);
      reply(0, null, 204); await empty;
      expect(store.currentId).toBe(A);
      expect(store.latest).toBeNull();
      expect(store.error).toBeNull();
      const pending = store.loadLatest(B);
      store.cancelLatest();
      reply(1, value(B)); await pending;
      expect(store.currentId).toBeNull();
      expect(store.latest).toBeNull();
      expect(store.loading).toBe(false);
    });
  });
}

it('界面提示限定为有效水位，汛限值与教材唯一参数源一致', () => {
  const source = readFileSync(resolve(process.cwd(), '../../../output/case-params.tex'), 'utf8');
  const threshold = Number(source.match(/\\newcommand\{\\cpFloodLimitLevel\}\{([^}]+)\}/)[1]);
  expect(FLOOD_LIMIT_LEVEL).toBe(threshold);
  expect(needsWaterLevelAttention(value(B, { value: threshold }))).toBe(true);
  expect(needsWaterLevelAttention(value(B, { value: threshold - 0.001 }))).toBe(false);
  for (const reading of [null, value(A), value(B, { quality: 'suspect' }),
    value(B, { quality: 'missing' }), value(B, { unit: 'mm' }), value(B, { value: null }),
    value(B, { value: Infinity }), value('DAM-A-RF-01', { value: 200 })]) {
    expect(needsWaterLevelAttention(reading)).toBe(false);
  }
});

async function mountLogin(redirect) {
  const router = createRouter({ history: createMemoryHistory(), routes: [
    { path: '/login', component: Login },
    { path: '/assets/:id?', component: { template: '<p>对象页面</p>' } },
  ] });
  await router.push({ path: '/login', query: { redirect } });
  const host = document.createElement('div'); document.body.append(host);
  const app = createApp(Login); app.use(router); app.mount(host); apps.push(app);
  const inputs = host.querySelectorAll('input');
  inputs[0].value = 'duty01'; inputs[0].dispatchEvent(new Event('input'));
  inputs[1].value = 'duty123'; inputs[1].dispatchEvent(new Event('input'));
  host.querySelector('form').dispatchEvent(new Event('submit', { cancelable: true }));
  return { host, router };
}

it('打印登录组件提交 username 和完整接口路径，并回到原详情', async () => {
  const { router } = await mountLogin(`/assets/${B}`);
  expect(waiting[0].path).toBe('/api/auth/login');
  expect(JSON.parse(waiting[0].options.body)).toEqual({ username: 'duty01', password: 'duty123' });
  reply(0, { accessToken: 'test-access-token', expiresInSeconds: 600, authorities: ['DUTY'] });
  await flush();
  await vi.waitFor(() => expect(router.currentRoute.value.path).toBe(`/assets/${B}`));
  expect(sessionStorage.getItem('access_token')).toBe('test-access-token');
});

it('登录 401 留在表单并显示失败，不保存令牌', async () => {
  const { host, router } = await mountLogin(`/assets/${B}`);
  reply(0, { code: 'UNAUTHORIZED', message: '凭据无效' }, 401);
  await flush();
  expect(host.querySelector('[role="alert"]').textContent).toContain('HTTP_401');
  expect(router.currentRoute.value.path).toBe('/login');
  expect(sessionStorage.getItem('access_token')).toBeNull();
});

it('详情组件卸载使尚未完成的请求失效', async () => {
  const pinia = createPinia();
  const host = document.createElement('div'); document.body.append(host);
  const app = createApp(AssetDetail, { id: B }); app.use(pinia); app.mount(host);
  const store = useAssetStore(pinia);
  expect(waiting[0].path).toBe(`/api/assets/${B}/readings/latest`);
  app.unmount();
  reply(0, value(B)); await flush();
  expect(store.latest).toBeNull();
  expect(store.currentId).toBeNull();
  expect(store.loading).toBe(false);
});
