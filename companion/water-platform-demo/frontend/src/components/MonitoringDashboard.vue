<script setup>
import {computed, onMounted, onUnmounted, ref, watch} from 'vue';
import * as echarts from 'echarts';
import {useMonitoringStore} from '../stores/monitoring';

const store = useMonitoringStore();
const chartElement = ref();
let chart;
import {qualityText, toChartPoints} from '../utils/readings';
const points = computed(() => toChartPoints(store.readings));
function renderChart() {
  chart ??= echarts.init(chartElement.value);
  chart.setOption({tooltip: {trigger: 'axis'}, xAxis: {type: 'time'}, yAxis: {type: 'value', name: store.selectedAsset?.unit || ''}, series: [{type: 'line', connectNulls: false, data: points.value.map(p => p.value)}]});
}
function resize() { chart?.resize(); }
watch(() => [store.selectedAssetId, store.range.from, store.range.to], async () => { await store.loadReadings(); renderChart(); });
onMounted(async () => { await store.loadAssets(); await store.loadReadings(); renderChart(); window.addEventListener('resize', resize); });
onUnmounted(() => { window.removeEventListener('resize', resize); chart?.dispose(); });
</script>

<template>
  <main class="monitoring-dashboard">
    <h1>水利工程安全监测</h1>
    <p v-if="store.error" role="alert">{{ store.error }}</p>
    <div class="asset-list"><button v-for="asset in store.assets" :key="asset.assetId" :class="{active: asset.assetId === store.selectedAssetId}" @click="store.selectedAssetId = asset.assetId">{{ asset.displayName }}</button></div>
    <div ref="chartElement" class="reading-chart" aria-label="测点观测曲线"></div>
    <ul><li v-for="item in store.readings.slice(-10)" :key="item.eventId">{{ item.occurredAt }}：{{ item.value ?? '—' }}（{{ qualityText[item.quality] }}）</li></ul>
  </main>
</template>

<style scoped>.monitoring-dashboard{display:grid;gap:.75rem}.asset-list{display:flex;flex-wrap:wrap;gap:.5rem}.reading-chart{min-height:20rem}.active{outline:2px solid #1565c0}</style>
