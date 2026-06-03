import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { public: true },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/Dashboard.vue"),
  },
  {
    path: "/entry",
    name: "Entry",
    component: () => import("@/views/Entry.vue"),
  },
  {
    path: "/analysis",
    name: "Analysis",
    component: () => import("@/views/Analysis.vue"),
  },
  {
    path: "/benchmarking",
    name: "Benchmarking",
    component: () => import("@/views/Benchmarking.vue"),
  },
  {
    path: "/reports",
    name: "Reports",
    component: () => import("@/views/Reports.vue"),
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("@/views/Admin.vue"),
    meta: { requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guard — redirect to login if not authenticated
router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isLoggedIn) {
    return { name: "Login" };
  }
  if (to.meta.requiresAdmin && auth.role !== "dss") {
    return { name: "Dashboard" };
  }
});

export default router;
