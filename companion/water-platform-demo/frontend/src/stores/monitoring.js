import {computed, ref} from 'vue';
import {defineStore} from 'pinia';
import request from '../utils/request';
import {readingQuery} from '../utils/readings';

export const useMonitoringStore = defineStore('monitoring', () => {
  const assets = ref([]);
  const readings = ref([]);
  const selectedAssetId = ref('DAM-A-PZ-07');
  const range = ref({from: new Date(Date.now() - 86400000).toISOString(), to: new Date().toISOString(), agg: '5m'});
  const loading = ref(false);
  const error = ref('');
  const selectedAsset = computed(() => assets.value.find(a => a.assetId === selectedAssetId.value));
  async function loadAssets() { assets.value = await request.get('/api/assets'); }
  let sequence = 0; // 4.5.4 节：切换测点时只接受最新一次请求的响应
  async function loadReadings() {
    if (!selectedAssetId.value) return;
    const mine = ++sequence;
    loading.value = true; error.value = '';
    try {
      const data = await request.get(`/api/assets/${selectedAssetId.value}/readings`, readingQuery(range.value));
      if (mine !== sequence) return; // 迟到的旧响应：丢弃
      readings.value = data;
    }
    catch (e) { if (mine === sequence) error.value = e.status === 403 ? '当前角色无权查看该测点' : '读取观测失败'; }
    finally { if (mine === sequence) loading.value = false; }
  }
  return {assets, readings, selectedAssetId, selectedAsset, range, loading, error, loadAssets, loadReadings};
});
