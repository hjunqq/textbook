import {createRouter, createWebHistory} from 'vue-router';
import MonitoringDashboard from '../components/MonitoringDashboard.vue';

export default createRouter({
  history: createWebHistory(),
  routes: [{path: '/monitoring', component: MonitoringDashboard, meta: {roles: ['DUTY', 'ANALYST', 'OPS']}}],
});
