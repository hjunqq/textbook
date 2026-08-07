import {createApp} from 'vue';
import {createPinia} from 'pinia';
import router from './router';
import MonitoringDashboard from './components/MonitoringDashboard.vue';
createApp(MonitoringDashboard).use(createPinia()).use(router).mount('#app');
