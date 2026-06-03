<template>
  <header class="h-12 bg-white border-b border-gray-100 px-5 flex items-center justify-between flex-shrink-0">
    <div>
      <h1 class="font-head text-[15px] font-bold text-gray-900">{{ pageTitle }}</h1>
      <p class="text-[11px] text-gray-400 leading-none mt-0.5">{{ pageSubtitle }}</p>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[11px] text-gray-400">2023 reporting cycle</span>
      <div class="w-7 h-7 rounded-full bg-navy flex items-center justify-center text-white text-[11px] font-bold">
        {{ auth.displayName?.[0] ?? "U" }}
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";

const route = useRoute();
const auth  = useAuthStore();

const TITLES = {
  "/dashboard":   ["Dashboard",    "KPI overview · VerdaTyres Corp · 2023"],
  "/entry":       ["Submit Data",  "Step-by-step guided KPI data entry"],
  "/analysis":    ["Analytics",    "15-year KPI trends · Sector · 2009–2023"],
  "/benchmarking":["Benchmarking", "Quartile comparison · All TIP companies"],
  "/reports":     ["Reports",      "CSR annual summary · 2023"],
  "/admin":       ["Admin",        "dss+ analyst portal · TIP reporting cycle"],
};

const pageTitle    = computed(() => TITLES[route.path]?.[0] ?? "ESG Platform");
const pageSubtitle = computed(() => TITLES[route.path]?.[1] ?? "");
</script>
