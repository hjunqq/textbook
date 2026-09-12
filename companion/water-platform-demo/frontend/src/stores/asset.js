import { defineStore } from 'pinia';
import { loadLatest as fetchLatest, needsWaterLevelAttention } from '../api/assets.js';

export const useAssetStore = defineStore('asset', {
  state: () => ({ currentId: null, latest: null, loading: false, error: null,
    requestVersion: 0 }),
  getters: {
    needsAttention: state => needsWaterLevelAttention(state.latest)
  },
  actions: {
    cancelLatest() {
      this.requestVersion++;
      this.currentId = null; this.latest = null;
      this.loading = false; this.error = null;
    },
    async loadLatest(id) {
      const mine = ++this.requestVersion;
      this.currentId = id; this.latest = null;
      this.loading = true; this.error = null;
      try {
        const reading = await fetchLatest(id);
        if (mine !== this.requestVersion) return null;
        this.latest = reading;
        return reading;
      } catch (error) {
        if (mine === this.requestVersion) this.error = error;
        return null;
      } finally {
        if (mine === this.requestVersion) this.loading = false;
      }
    }
  }
});
