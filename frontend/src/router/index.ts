import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ApplicationList from '../views/ApplicationList.vue'
import ApplicationDetail from '../views/ApplicationDetail.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/applications' },
    { path: '/dashboard', name: 'dashboard', component: Dashboard },
    { path: '/applications', name: 'applications', component: ApplicationList },
    {
      path: '/applications/:id',
      name: 'application-detail',
      component: ApplicationDetail,
      props: true,
    },
    { path: '/settings', name: 'settings', component: Settings },
  ],
})

export default router
