import { defineStore } from "pinia";
import { ref, computed } from "vue";

const BASE = "http://localhost:3001/api";

async function apiFetch(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const useEsgStore = defineStore("esg", () => {
  const homeData      = ref(null);
  const loading       = ref({});
  const dfVersion     = ref(0);
  const selectedYear  = ref(null);

  async function fetchHomeData(company, year) {
    loading.value.home = true;
    try {
      const data = await apiFetch(
        `/home?company=${encodeURIComponent(company)}&year=${year}`
      );
      homeData.value = data;
      if (!selectedYear.value && data.available_years?.length)
        selectedYear.value = Math.max(...data.available_years);
    } catch (e) {
      console.error("fetchHomeData:", e.message);
    } finally {
      loading.value.home = false;
    }
  }

  const availableYears   = computed(() => homeData.value?.available_years || []);
  const nextYear         = computed(() => homeData.value?.next_year || null);
  const homeKpis         = computed(() => homeData.value?.kpis    || {});
  const homeYoy          = computed(() => homeData.value?.yoy     || {});
  const homeCharts       = computed(() => homeData.value?.charts  || {});
  const submissionStatus = computed(() => homeData.value?.submission_status || {});

  return {
    homeData, loading, dfVersion, selectedYear,
    availableYears, nextYear, homeKpis, homeYoy, homeCharts, submissionStatus,
    fetchHomeData,
  };
});