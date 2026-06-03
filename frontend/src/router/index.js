import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";

// Stub component for pages not yet built
const Soon = { template: '<div class="p-8 text-center text-gray-400">Page coming soon</div>' }

const routes = [
  { path: "/",          redirect: "/home" },
  { path: "/login",     component: () => import("@/views/Login.vue"),       meta: { public: true } },
  { path: "/home",      component: () => import("@/views/Home.vue"),        meta: { roles: ["client","dss"] } },
  { path: "/benchmarks",component: () => import("@/views/Benchmarking.vue"),meta: { roles: ["client","dss"] } },

  // Stubs — replace each with a real view when ready
  { path: "/dashboard",    component: Soon, meta: { roles: ["client","dss"] } },
  { path: "/my-records",   component: Soon, meta: { roles: ["client","dss"] } },
  { path: "/reports",      component: Soon, meta: { roles: ["client","dss"] } },
  { path: "/entry",        component: Soon, meta: { roles: ["client"] } },
  { path: "/settings",     component: Soon, meta: { roles: ["client","dss"] } },
  { path: "/portfolio",    component: Soon, meta: { roles: ["dss"] } },
  { path: "/company-data", component: Soon, meta: { roles: ["dss"] } },
  { path: "/verification", component: Soon, meta: { roles: ["dss"] } },
  { path: "/analysis",     component: Soon, meta: { roles: ["dss"] } },
  { path: "/admin",        component: Soon, meta: { roles: ["dss"] } },

  { path: "/:pathMatch(.*)*", redirect: "/home" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.public) return true;
  if (!auth.isLoggedIn)    return "/login";
  if (to.meta.roles && !to.meta.roles.includes(auth.role)) return "/home";
  return true;
});

export default router;