// S1 阶段包的验收自动化：对应表 tab:ch04-stage-acceptance 的 S1 行。
// 四条必须能演示的行为各一组用例，外加故意注入的故障（DAM-A-XX-99）。
import { describe, it, expect, beforeEach } from 'vitest';
import { assets } from '../src/lesson44/assets.js';
import {
  filterByKeyword, sortByValue, parseAssetId, findAsset, formatReading,
} from '../src/lesson44/query.js';
import { renderAssetList, renderAssetDetail } from '../src/lesson44/render.js';

describe('固定数据与契约一致', () => {
  it('28 个测点，8 个位移测点没有观测', () => {
    expect(assets).toHaveLength(28);
    expect(assets.filter(a => a.value === null)).toHaveLength(8);
  });

  it('取值与教学接口同源（datasets 的最新一条）', () => {
    expect(findAsset(assets, 'DAM-A-WL-01').value).toBe(166.84);
    expect(findAsset(assets, 'DAM-A-PZ-07').value).toBe(185.09);
  });
});

describe('按名称筛选', () => {
  it('关键字为空返回全部', () => {
    expect(filterByKeyword(assets, '   ')).toHaveLength(28);
  });

  it('中文名称与编码都能命中，且大小写不敏感', () => {
    expect(filterByKeyword(assets, '渗压')).toHaveLength(12);
    expect(filterByKeyword(assets, 'dam-a-wl')).toHaveLength(3);
  });

  it('不修改入参', () => {
    const before = assets.length;
    filterByKeyword(assets, '雨量');
    expect(assets).toHaveLength(before);
  });
});

describe('按值排序', () => {
  it('升序时没有观测的排在最后，不被当成 0', () => {
    const ordered = sortByValue(assets, 'asc');
    expect(ordered[0].value).toBe(0.00);
    expect(ordered.slice(-8).every(a => a.value === null)).toBe(true);
  });

  it('降序时没有观测的仍然排在最后', () => {
    const ordered = sortByValue(assets, 'desc');
    expect(ordered[0].assetId).toBe('DAM-A-PZ-12');
    expect(ordered.slice(-8).every(a => a.value === null)).toBe(true);
  });
});

describe('非法输入有提示', () => {
  it('空输入与格式错误各给一条可读消息', () => {
    expect(parseAssetId('').ok).toBe(false);
    expect(parseAssetId('').message).toContain('DAM-A-PZ-07');
    expect(parseAssetId('PZ7').ok).toBe(false);
    expect(parseAssetId('PZ7').message).toContain('PZ7');
  });

  it('合法编码统一转成大写', () => {
    expect(parseAssetId(' dam-a-pz-07 ')).toEqual({ ok: true, assetId: 'DAM-A-PZ-07' });
  });
});

describe('渲染', () => {
  beforeEach(() => { document.body.innerHTML = '<ul id="list"></ul><div id="detail"></div>'; });

  it('空结果显示“暂无测点”而不是留白', () => {
    const list = document.querySelector('#list');
    expect(renderAssetList(list, [])).toBe(0);
    expect(list.textContent).toBe('暂无测点');
  });

  it('对象名称走 textContent，不会被当成标签解析', () => {
    const list = document.querySelector('#list');
    renderAssetList(list, [{
      assetId: 'DAM-A-PZ-07', displayName: '<img src=x onerror=alert(1)>',
      assetType: '渗压', unit: 'kPa', value: 185.09, quality: 'valid',
      occurredAt: '2026-07-01T23:55:00+08:00',
    }]);
    expect(list.querySelector('img')).toBeNull();
    expect(list.querySelector('.asset-name').textContent).toContain('<img');
  });

  it('没有观测时显示“暂无观测”', () => {
    expect(formatReading(findAsset(assets, 'DAM-A-D-01'))).toBe('暂无观测');
  });

  // 故意注入的故障：格式合法但台账里没有的编码
  it('DAM-A-XX-99 走到详情页时说明未找到，并回显输入的编码', () => {
    const detail = document.querySelector('#detail');
    const parsed = parseAssetId('DAM-A-XX-99');
    expect(parsed.ok).toBe(true);
    const found = renderAssetDetail(detail, findAsset(assets, parsed.assetId), parsed.assetId);
    expect(found).toBe(false);
    expect(detail.dataset.state).toBe('not-found');
    expect(detail.textContent).toContain('DAM-A-XX-99');
  });
});
