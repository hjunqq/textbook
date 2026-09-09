// 4.5.4 节故障单元的自动化验证：先发的请求延迟 200 ms，后发的 20 ms，页面最终必须属于后点击的对象
import { describe, it, expect, vi, beforeEach } from 'vitest';

const encoder = (obj, status = 200) => ({
  ok: status < 400, status,
  json: async () => obj,
});

describe('showAsset 竞态', () => {
  beforeEach(() => { vi.resetModules(); document.body.innerHTML = '<p id="latest"></p>'; });

  it('迟到的旧响应不会覆盖新对象', async () => {
    const aborted = [];
    globalThis.fetch = vi.fn((url, opts = {}) => new Promise((resolve, reject) => {
      const delay = url.includes('PZ-07') ? 200 : 20;
      const timer = setTimeout(() => resolve(encoder(url.includes('PZ-07')
        ? { value: 185.091, unit: 'kPa', quality: 'valid' }
        : { value: 166.837, unit: 'm', quality: 'valid' })), delay);
      opts.signal?.addEventListener('abort', () => {
        clearTimeout(timer); aborted.push(url);
        reject(Object.assign(new Error('aborted'), { name: 'AbortError' }));
      });
    }));
    const { showAsset } = await import('../src/lesson45/controller.js');
    const el = document.querySelector('#latest');
    const pz = { assetId: 'DAM-A-PZ-07', displayName: '案例渗压07' };
    const wl = { assetId: 'DAM-A-WL-01', displayName: '案例水位01' };
    const first = showAsset(el, pz);
    expect(el.dataset.state).toBe('loading');
    const second = showAsset(el, wl);
    await Promise.all([first, second]);
    await new Promise(r => setTimeout(r, 250));
    expect(el.textContent).toContain('案例水位01：166.837 m');
    expect(aborted).toHaveLength(1);
    expect(aborted[0]).toContain('PZ-07');
  });

  it('204 进入 empty 状态而不是 error', async () => {
    globalThis.fetch = vi.fn(async () => ({ ok: true, status: 204, json: async () => null }));
    const { showAsset } = await import('../src/lesson45/controller.js');
    const el = document.querySelector('#latest');
    await showAsset(el, { assetId: 'DAM-A-RF-01', displayName: '案例雨量01' });
    expect(el.dataset.state).toBe('empty');
    expect(el.textContent).toBe('案例雨量01：暂无观测');
  });
});
