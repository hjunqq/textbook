<script setup>
import { onMounted, onUnmounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useAssetStore } from '../stores/asset.js';

const assetStore = useAssetStore();
const { latest, loading, needsAttention } = storeToRefs(assetStore);
const { loadLatest } = assetStore;

onMounted(() => loadLatest('DAM-A-WL-01'));
onUnmounted(() => assetStore.cancelLatest());
</script>

<template>
  <p v-if="loading" role="status">正在读取最新水位……</p>
  <p v-else-if="latest">{{ latest.value }} {{ latest.unit }} <strong v-if="needsAttention">需要关注</strong></p>
  <p v-else>暂无读数</p>
</template>
