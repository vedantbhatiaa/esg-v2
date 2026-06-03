<template>
  <aside class="w-52 bg-navy flex flex-col flex-shrink-0 overflow-hidden">
    <!-- Logo -->
    <div class="px-4 pt-4 pb-3 border-b border-white/5">
      <div class="flex items-baseline gap-0.5">
        <span class="font-head text-xl font-black text-dss tracking-tight">dss</span>
        <span class="font-head text-sm font-semibold text-[#9B9B9B]">+</span>
      </div>
      <div class="text-[9px] text-white/20 mt-0.5 uppercase tracking-widest">ESG Reporting · TIP</div>
    </div>

    <!-- User chip -->
    <div class="mx-3 mt-2 mb-1 px-3 py-2 bg-white/[0.04] border border-white/[0.06] rounded-lg">
      <div class="text-xs font-semibold text-white/85">{{ auth.displayName }}</div>
      <div class="text-[10px] text-white/30 mt-0.5">
        {{ auth.role === 'dss' ? 'dss+ Analyst' : auth.companyName + ' · 2023' }}
      </div>
    </div>

    <!-- Navigation -->
    <nav class="px-2 pt-1 flex-1">
      <template v-for="item in navItems" :key="item.name">
        <router-link
          :to="item.path"
          class="flex items-center gap-2 px-2.5 py-1.5 text-[12.5px] text-white/40 rounded-lg
                 border-l-[2.5px] border-transparent hover:bg-white/5 hover:text-white/75
                 transition-all duration-150 mb-0.5 no-underline"
          active-class="!bg-dss/10 !text-white !border-dss font-medium"
        >
          <span class="w-1 h-1 rounded-full bg-current opacity-50 flex-shrink-0"></span>
          {{ item.name }}
        </router-link>
      </template>
    </nav>

    <!-- Footer -->
    <div class="px-4 py-3 border-t border-white/5">
      <button
        @click="auth.logout(); $router.push('/login')"
        class="text-[11px] text-white/20 underline hover:text-white/50 transition-colors"
      >
        Sign out
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth.js";

const auth = useAuthStore();

const CLIENT_NAV = [
  { name: "Dashboard",    path: "/dashboard" },
  { name: "Submit Data",  path: "/entry" },
  { name: "Analysis",     path: "/analysis" },
  { name: "Benchmarking", path: "/benchmarking" },
  { name: "Reports",      path: "/reports" },
];

const DSS_NAV = [
  { name: "Portfolio",          path: "/dashboard" },
  { name: "Data Entry Review",  path: "/entry" },
  { name: "Analytics",          path: "/analysis" },
  { name: "Benchmarking",       path: "/benchmarking" },
  { name: "Reports",            path: "/reports" },
  { name: "Admin",              path: "/admin" },
];

const navItems = computed(() =>
  auth.role === "dss" ? DSS_NAV : CLIENT_NAV
);
</script>
