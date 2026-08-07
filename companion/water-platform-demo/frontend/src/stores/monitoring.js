import {computed, ref} from 'vue';
import {defineStore} from 'pinia';
import request from '../utils/request';

export const useMonitoringStore = defineStore('monitoring', () => {
  const assets = ref([]);
  const readings = ref([]);
  const selectedAssetId = ref('DAM-A-PZ-07');
  const range = ref({from: new Date(Date.now() - 86400000).toISOString(), to: new Date().toISOString(), agg: '5m'});
  const loading = ref(false);
  const error = ref('');
  const selectedAsset = computed(() => assets.value.find(a => a.assetId === selectedAssetId.value));
  async function loadAssets() { assets.value = await request.get('/api/assets'); }
  async function loadReadings() {
    if (!selectedAssetId.value) return;
    loading.value = true; error.value = '';
    try { readings.value = await request.get(`/api/assets/${selectedAssetId.value}/readings`, range.value); }
    catch (e) { error.value = e.status === 403 ? '当前角色无权查看该测点' : '读取观测失败'; }
    finally { loading.value = false; }
  }
  return {assets, readings, selectedAssetId, selectedAsset, range, loading, error, loadAssets, loadReadings};
});
