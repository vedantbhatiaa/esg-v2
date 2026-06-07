import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";

const routes = [
  { path: "/",             redirect: "/home" },
  { path: "/login",        component: () => import("@/views/Login.vue"),        meta: { public: true } },
  // ── Client pages
  { path: "/home",         component: () => import("@/views/Home.vue"),          meta: { roles: ["client","dss"] } },
  { path: "/dashboard",    component: () => import("@/views/Dashboard.vue"),     meta: { roles: ["client","dss"] } },
  { path: "/my-records",   component: () => import("@/views/MyRecords.vue"),     meta: { roles: ["client","dss"] } },
  { path: "/reports",      component: () => import("@/views/Reports.vue"),       meta: { roles: ["client","dss"] } },
  { path: "/entry",        component: () => import("@/views/Entry.vue"),         meta: { roles: ["client"] } },
  { path: "/benchmarks",   component: () => import("@/views/Benchmarking.vue"), meta: { roles: ["client","dss"] } },
  { path: "/settings",     component: () => import("@/views/Settings.vue"),      meta: { roles: ["client","dss"] } },
  // ── DSS+ pages
  { path: "/portfolio",    component: () => import("@/views/Portfolio.vue"),     meta: { roles: ["dss"] } },
  { path: "/company-data", component: () => import("@/views/CompanyData.vue"),   meta: { roles: ["dss"] } },
  { path: "/verification", component: () => import("@/views/Verification.vue"),  meta: { roles: ["dss"] } },
  { path: "/analysis",     component: () => import("@/views/Analysis.vue"),      meta: { roles: ["dss"] } },
  { path: "/readiness",    component: () => import("@/views/Readiness.vue"),     meta: { roles: ["dss"] } },
  { path: "/admin",        component: () => import("@/views/Admin.vue"),         meta: { roles: ["dss"] } },
  { path: "/:pathMatch(.*)*", redirect: "/home" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  // Public route — always allow
  if (to.meta?.public) return true;

  // Not logged in — go to login
  if (!auth.isLoggedIn) return "/login";

  // Root redirect — send to role-appropriate landing page
  if (to.path === "/") {
    return auth.isDss ? "/portfolio" : "/home";
  }

  // Role guard — dss+ trying to access client-only, redirect to portfolio
  if (to.meta?.roles && !to.meta.roles.includes(auth.role)) {
    return auth.isDss ? "/portfolio" : "/home";
  }

  return true;
});

export default router;