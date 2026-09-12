<script setup>
import { watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useAssetStore } from '../stores/asset.js';

const props = defineProps({ id: { type: String, required: true } });
const assetStore = useAssetStore();
const { latest, loading, error } = storeToRefs(assetStore);

watch(() => props.id, (id, previous, onCleanup) => {
  void assetStore.loadLatest(id);
  onCleanup(() => assetStore.cancelLatest());
}, { immediate: true });
</script>

<template>
  <article aria-labelledby="station-detail-title">
    <h1 id="station-detail-title">测站 {{ props.id }}</h1>
    <p v-if="loading" role="status">正在加载……</p>
    <p v-else-if="error" role="alert">{{ error.message }}</p>
    <dl v-else-if="latest"><dt>最新观测</dt><dd>{{ latest.value }} {{ latest.unit }}</dd></dl>
    <p v-else>暂无有效读数</p>
  </article>
</template>
