<template>
  <div>
    <div class="flex items-center justify-between mb-5">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Portfolio</h2>
        <p class="text-sm text-gray-400 mt-0.5">All TIP member companies · {{ currentYear }} data</p>
      </div>
      <select v-model="selYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
        <option v-for="y in YEARS.slice().reverse()" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <!-- Sector summary cards -->
    <div class="grid grid-cols-4 gap-3 mb-5">
      <div v-for="m in sectorMetrics" :key="m.label" class="bg-white border border-gray-100 rounded-xl p-4">
        <div class="text-xs text-gray-400 mb-1">{{ m.label }}</div>
        <div class="text-2xl font-bold" :style="{color: m.color}">{{ m.value }}</div>
        <div class="text-xs text-gray-400 mt-0.5">{{ m.unit }}</div>
      </div>
    </div>

    <!-- Companies table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 flex items-center gap-3">
        <span class="text-sm font-semibold">Company KPIs — {{ selYear }}</span>
        <div class="ml-auto flex gap-2">
          <input v-model="search" placeholder="Search company…" class="h-7 border border-gray-200 rounded-lg px-2 text-xs w-40" />
        </div>
      </div>
      <div v-if="loading" class="px-5 py-8 text-center text-sm text-gray-400">Loading portfolio data…</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th v-for="col in cols" :key="col.key" class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100 cursor-pointer hover:text-gray-600"
                @click="sortBy(col.key)">
                {{ col.label }} {{ sortKey===col.key ? (sortDir>0?'↑':'↓') : '' }}
              </th>
              <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.company"
              class="border-b border-gray-50 last:border-none hover:bg-blue-50/40 transition-colors">
              <td class="px-4 py-2.5 font-semibold text-navy">{{ row.company }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.co2_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.energy_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.water_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.renew_pct }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.waste_pct }}</td>
              <td class="px-4 py-2.5">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold"
                  :class="statusClass(row.verif_status)">{{ row.verif_status || 'Pending' }}</span>
              </td>
              <td class="px-4 py-2.5">
                <button @click="openCompany(row.company)"
                  class="px-2.5 py-1 bg-navy text-white rounded text-[10px] font-medium hover:opacity-80">
                  Open Template →
                </button>
              </td>
            </tr>
            <tr v-if="!filteredRows.length">
              <td :colspan="cols.length+1" class="px-5 py-8 text-center text-gray-400">
                {{ loading ? 'Loading…' : 'No companies found. Ensure the master CSV exists and Python service is running.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api.js";
import { YEARS } from "@/composables/useCharts.js";

const router  = useRouter();
const selYear = ref(2023);
const loading = ref(false);
const search  = ref("");
const rows    = ref([]);
const sortKey = ref("co2_kpi");
const sortDir = ref(1);
const currentYear = computed(() => selYear.value);

const cols = [
  { key:"company",    label:"Company" },
  { key:"co2_kpi",    label:"CO₂ KPI (T/T)" },
  { key:"energy_kpi", label:"Energy KPI (GJ/T)" },
  { key:"water_kpi",  label:"Water KPI (m³/T)" },
  { key:"renew_pct",  label:"Renewable %" },
  { key:"waste_pct",  label:"Waste Rec. %" },
  { key:"verif_status",label:"Status" },
];

const sectorMetrics = computed(() => {
  const n = rows.value.length;
  if (!n) return [];
  const avg = k => (rows.value.reduce((s,r)=>s+(parseFloat(r[k])||0),0)/n).toFixed(3);
  const verified = rows.value.filter(r=>r.verif_status==="Verified").length;
  return [
    { label:"Companies", value:n, unit:"reporting", color:"#0A2240" },
    { label:"Avg CO₂ KPI", value:avg("co2_kpi"), unit:"T.CO₂/T", color:"#475569" },
    { label:"Avg Energy KPI", value:avg("energy_kpi"), unit:"GJ/T", color:"#F59E0B" },
    { label:"Verified", value:`${verified}/${n}`, unit:"submissions", color:"#16A34A" },
  ];
});

function sortBy(key) {
  if (sortKey.value === key) sortDir.value *= -1;
  else { sortKey.value = key; sortDir.value = 1; }
}

const filteredRows = computed(() => {
  let r = rows.value.filter(row => !search.value || row.company.toLowerCase().includes(search.value.toLowerCase()));
  r = r.slice().sort((a,b) => {
    const av = parseFloat(a[sortKey.value]) || 0;
    const bv = parseFloat(b[sortKey.value]) || 0;
    return (av - bv) * sortDir.value;
  });
  return r;
});

function statusClass(s) {
  if (s==="Verified") return "bg-green-100 text-green-700";
  if (s==="Flagged")  return "bg-red-100 text-red-700";
  return "bg-yellow-100 text-yellow-700";
}

function openCompany(company) {
  router.push({ path:"/company-data", query:{ company } });
}

async function loadData() {
  loading.value = true;
  try {
    const bench = await api.getBenchmarks(selYear.value);
    if (bench?.scorecard) {
      rows.value = bench.scorecard.map(r => ({
        company:    r.company,
        co2_kpi:    r.co2_kpi?.toFixed(3) ?? "—",
        energy_kpi: r.energy_kpi?.toFixed(2) ?? "—",
        water_kpi:  r.water_kpi?.toFixed(2) ?? "—",
        renew_pct:  r.renew_pct?.toFixed(1) ?? "—",
        waste_pct:  r.waste_pct?.toFixed(1) ?? "—",
        verif_status: r.verif_status || "Pending",
      }));
    }
  } catch(e) { console.error("Portfolio load:", e); }
  finally { loading.value = false; }
}

onMounted(loadData);
watch(selYear, loadData);
</script>