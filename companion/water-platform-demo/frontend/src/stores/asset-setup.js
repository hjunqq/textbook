import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { loadLatest as fetchLatest, needsWaterLevelAttention } from '../api/assets.js';

export const useAssetSetupStore = defineStore('asset-setup', () => {
  const currentId = ref(null);
  const latest = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const needsAttention = computed(() => needsWaterLevelAttention(latest.value));
  let requestVersion = 0;

  function cancelLatest() {
    requestVersion++;
    currentId.value = null; latest.value = null;
    loading.value = false; error.value = null;
  }
  async function loadLatest(id) {
    const mine = ++requestVersion;
    currentId.value = id; latest.value = null;
    loading.value = true; error.value = null;
    try {
      const reading = await fetchLatest(id);
      if (mine !== requestVersion) return null;
      latest.value = reading;
      return reading;
    } catch (cause) {
      if (mine === requestVersion) error.value = cause;
      return null;
    } finally {
      if (mine === requestVersion) loading.value = false;
    }
  }
  return { currentId, latest, loading, error, needsAttention, loadLatest, cancelLatest };
});
