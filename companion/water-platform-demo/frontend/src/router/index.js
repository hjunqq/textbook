import {createRouter, createWebHistory} from 'vue-router';
import {isLoggedIn} from '../utils/auth';
import MonitoringDashboard from '../components/MonitoringDashboard.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {path: '/', redirect: '/monitoring'},
    {path: '/login', name: 'login', component: () => import('../views/LoginView.vue')},
    {path: '/monitoring', component: MonitoringDashboard,
     meta: {requiresAuth: true, roles: ['DUTY', 'ANALYST', 'OPS']}},
  ],
});

router.beforeEach(to => {
  if (to.meta.requiresAuth && !isLoggedIn())
    return {name: 'login', query: {redirect: to.fullPath}};
});

export default router;
