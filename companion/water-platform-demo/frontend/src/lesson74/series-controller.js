// 第7章复用第4章的异步状态规则；依赖注入使乱序响应可以稳定复现。
import { createLinkController } from './link.js';
import { toChartPoints, qualityText } from '../utils/readings.js';

export function createSeriesController({ chart, scene, status, loadSeries }) {
  let sequence = 0;
  let pending;
  let disposed = false;
  let unlink = () => {};

  async function showAsset(assetId) {
    if (disposed) return;
    const current = ++sequence;
    pending?.abort();
    const request = new AbortController();
    pending = request;
    // 切换一开始就解除旧联动，空结果与失败路径同样适用。
    unlink();
    unlink = () => {};
    chart.clear();
    status.textContent = `正在读取 ${assetId} 的观测…`;
    try {
      const readings = await loadSeries(assetId, request.signal);
      if (disposed || current !== sequence) return;
      if (readings.length === 0) {
        status.textContent = `${assetId}：暂无观测`;
        return;
      }
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'time' },
        yAxis: { type: 'value', scale: true, name: readings[0].unit },
        series: [{
          id: 'level', type: 'line', showSymbol: true,
          connectNulls: false,
          data: toChartPoints(readings),
        }],
      }, true);
      unlink = createLinkController(chart, scene, readings);
      const bad = readings.filter(r => r.quality !== 'valid').length;
      status.textContent = `${assetId}：${readings.length} 条观测`
        + (bad ? `，其中 ${bad} 条非${qualityText.valid}` : '');
    } catch (error) {
      if (disposed || current !== sequence) return;
      status.textContent = `${assetId}：读取失败（${error.message}），请重新选择测点重试`;
    }
  }

  function dispose() {
    disposed = true;
    ++sequence;
    pending?.abort();
    unlink();
    unlink = () => {};
  }

  return { showAsset, dispose };
}
