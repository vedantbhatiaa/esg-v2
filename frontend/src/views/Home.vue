<template>
  <div>
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Welcome, {{ firstName }} 👋</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ auth.companyName }} · Your Performance Dashboard</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="selectedYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <router-link to="/entry"
          class="h-8 px-3 text-white rounded-lg text-sm font-medium flex items-center hover:opacity-90 no-underline"
          style="background:#0A2240">
          📋 Submit Data
        </router-link>
      </div>
    </div>

    <!-- Submission status bar -->
    <div class="bg-white border border-gray-100 rounded-xl px-5 py-3 mb-4 flex items-center gap-4">
      <div class="flex-1">
        <div class="text-xs text-gray-400 mb-1.5">{{ selectedYear }} Submission Status</div>
        <div class="bg-gray-100 rounded h-1.5 overflow-hidden">
          <div class="h-full rounded transition-all duration-700"
            :style="{ width: statusPct + '%', background: statusColor }"></div>
        </div>
      </div>
      <div class="text-lg font-bold" :style="{ color: statusColor }">{{ statusDone }}/6</div>
      <div class="text-xs text-gray-400">sections complete</div>
      <div class="border-l border-gray-200 pl-4 text-xs font-semibold whitespace-nowrap" :style="{ color: verifColor }">
        {{ verifIcon }} {{ verifLabel }}
      </div>
    </div>

    <!-- 8 KPI cards -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <KPICard v-for="(card, i) in kpiCards" :key="card.label"
        :label="card.label" :value="card.value" :unit="card.unit"
        :delta="card.delta" :color="card.color" :delay="i * 60" />
    </div>

    <!-- Chart tabs -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden mb-4">
      <div class="flex border-b border-gray-100 overflow-x-auto">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap"
          :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
          {{ tab.label }}
        </button>
      </div>
      <div class="p-4">
        <div v-show="activeTab==='co2'"    style="height:260px"><canvas ref="co2Canvas"></canvas></div>
        <div v-show="activeTab==='energy'" style="height:260px"><canvas ref="energyCanvas"></canvas></div>
        <div v-show="activeTab==='water'"  style="height:260px"><canvas ref="waterCanvas"></canvas></div>
        <div v-show="activeTab==='waste'"  style="height:260px"><canvas ref="wasteCanvas"></canvas></div>
      </div>
    </div>

    <!-- Historical table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-50 text-sm font-semibold">
        Historical KPI Summary — {{ auth.companyName }}
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead><tr class="bg-gray-50">
            <th v-for="h in TABLE_HEADERS" :key="h"
              class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">
              {{ h }}
            </th>
          </tr></thead>
          <tbody>
            <tr v-if="!tableRows.length">
              <td :colspan="TABLE_HEADERS.length" class="px-5 py-6 text-center text-gray-400 text-sm">
                No data yet. Submit your first KPI report to see your dashboard.
              </td>
            </tr>
            <tr v-for="row in tableRows" :key="row.year"
              class="border-b border-gray-50 last:border-none hover:bg-gray-50">
              <td class="px-4 py-2.5 font-bold text-navy">{{ row.year }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.production }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.total_co2 }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.co2_kpi }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.energy_kpi }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.renew_pct }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.water_kpi }}</td>
              <td class="px-4 py-2 tabular-nums text-gray-600">{{ row.waste_rec }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { Chart } from "chart.js";
import KPICard from "@/components/KPICard.vue";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, TOOLTIP, ANIMATION, AXIS, YEARS, YEAR_LABELS, FALLBACK } from "@/composables/useCharts.js";

const auth = useAuthStore();
const selectedYear   = ref(2023);
const availableYears = ref(YEARS.slice().reverse()); // full range until API responds
const activeTab      = ref("co2");

// Data from API
const homeData  = ref(null);   // { kpis, yoy, charts, available_years, submission_status }
const seriesAll = ref([]);     // all years historical series for the table

const firstName = computed(() => (auth.companyName || "").split(" ")[0] || "there");

const TABLE_HEADERS = ["Year","Production (MT)","CO₂ Total (T)","CO₂ Intensity","Energy KPI (GJ/T)","Renew. %","Water KPI (m³/T)","Waste Rec. %"];

const tabs = [
  { id:"co2",    label:"📈 CO₂ Trend" },
  { id:"energy", label:"⚡ Energy Mix" },
  { id:"water",  label:"💧 Water" },
  { id:"waste",  label:"♻ Waste & Fuel" },
];

// ── KPI cards — map from get_home_data field names
const kpiCards = computed(() => {
  const k = homeData.value?.kpis || {};
  const y = homeData.value?.yoy  || {};
  const fmt = (v, d) => v != null && v > 0 ? Number(v).toFixed(d) : "—";
  const delta = (field) => y[field] != null ? `${y[field] > 0 ? "+" : ""}${y[field]}%` : null;
  return [
    { label:"CO₂ Intensity",    value:fmt(k.co2_kpi,3),                                       unit:"T.CO₂/T",  delta:delta("co2_kpi"),            color:C.co2    },
    { label:"Energy Intensity", value:fmt(k.energy_kpi,2),                                    unit:"GJ/T",     delta:delta("energy_kpi"),         color:C.energy },
    { label:"Water Intensity",  value:fmt(k.water_kpi,2),                                     unit:"m³/T",     delta:delta("water_kpi"),          color:C.water  },
    { label:"Renewable Elec.",  value:fmt(k.renewable_share_pct,1),                           unit:"%",        delta:delta("renewable_share_pct"),color:C.renew  },
    { label:"Total CO₂",        value:k.total_co2_t?(k.total_co2_t/1e6).toFixed(2)+"M":"—",  unit:"T.CO₂",    delta:delta("total_co2_t"),        color:C.co2    },
    { label:"Total Energy",     value:k.total_energy_gj?(k.total_energy_gj/1e6).toFixed(1)+"M":"—", unit:"GJ", delta:null,                        color:C.navy   },
    { label:"Waste Recovery",   value:k.waste_recovery_pct?k.waste_recovery_pct.toFixed(1):"—",unit:"%",      delta:delta("waste_recovery_pct"),  color:C.waste  },
    { label:"ISO 14001",        value:k.iso_certified_pct?k.iso_certified_pct.toFixed(0):"—",  unit:"%",      delta:null,                         color:C.renew  },
  ];
});

// ── Submission status
const sub = computed(() => homeData.value?.submission_status || {});
const statusDone  = computed(() => sub.value.sections_done || 0);
const statusPct   = computed(() => (statusDone.value / 6) * 100);
const statusColor = computed(() => statusPct.value===100?"#16A34A":statusPct.value>=50?"#F59E0B":"#DC2626");
const verifMap = { Verified:["✓","#16A34A","Verified by dss+"], Pending:["◉","#F59E0B","Pending Review"], Flagged:["⚑","#DC2626","Flagged"], Pending:["◉","#F59E0B","Pending Review"] };
const verifIcon  = computed(() => (verifMap[sub.value.verification] || ["○","#94A3B8"])[0]);
const verifColor = computed(() => (verifMap[sub.value.verification] || ["○","#94A3B8"])[1]);
const verifLabel = computed(() => (verifMap[sub.value.verification] || ["○","#94A3B8","Not Submitted"])[2]);

// ── Table: built from historical series
const tableRows = computed(() => seriesAll.value.slice().reverse().slice(0, 10).map(e => ({
  year:       e.year,
  production: e.production_t ? (e.production_t / 1e6).toFixed(3) : "—",
  total_co2:  e.total_co2_t  ? Number(e.total_co2_t).toLocaleString() : "—",
  co2_kpi:    e.co2_kpi?.toFixed(3)               ?? "—",
  energy_kpi: e.energy_kpi?.toFixed(2)             ?? "—",
  renew_pct:  e.renewable_share_pct?.toFixed(1)+"%"?? "—",
  water_kpi:  e.water_kpi?.toFixed(2)              ?? "—",
  waste_rec:  e.waste_recovery_pct?.toFixed(1)+"%"  ?? "—",
})));

// ── Charts
const co2Canvas=ref(null), energyCanvas=ref(null), waterCanvas=ref(null), wasteCanvas=ref(null);
const charts = {};

function destroyAll() { Object.values(charts).forEach(c => { try { c.destroy(); } catch(_) {} }); }

const OPT = () => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:11}, padding:9 } }, tooltip:TOOLTIP },
  scales:AXIS, interaction:{ mode:"index", intersect:false },
});

async function buildCharts() {
  await nextTick();
  destroyAll();

  // charts.years comes from get_home_data response
  const ch = homeData.value?.charts || {};
  const ys  = ch.years || YEARS;
  const labels = ys.map(y => `'${String(y).slice(2)}`);

  const arr = (key, fallbackKey) => {
    const a = ch[key];
    if (a && a.some(v=>v!=null&&v>0)) return a;
    return FALLBACK[fallbackKey] || Array(ys.length).fill(null);
  };

  // CO2: scope1 + scope2 stacked area
  if (co2Canvas.value) {
    charts.co2 = new Chart(co2Canvas.value, { type:"line", data:{ labels, datasets:[
      { label:"Scope 1", data:arr("scope1_mt","scope1"), borderColor:C.co2, backgroundColor:"rgba(71,85,105,.12)", fill:true, tension:0.4, pointRadius:2, borderWidth:2 },
      { label:"Scope 2", data:arr("scope2_mt","scope2"), borderColor:C.teal, backgroundColor:"rgba(8,145,178,.10)", fill:true, tension:0.4, pointRadius:2, borderWidth:2 },
    ]}, options:OPT() });
  }

  // Energy mix stacked bar
  if (energyCanvas.value) {
    const fuelColors = { "Natural Gas":C.energy, "Electricity":"#3B82F6", "LPG":"#8B5CF6", "Coal":"#6B7280", "Diesel":"#78716C", "Biomass":"#16A34A" };
    const fuelData = {
      "Natural Gas": arr("nat_gas_gj","fuel_mix.Natural Gas"),
      "Electricity":  arr("nonrenew_elec_gj","fuel_mix.Electricity"),
      "LPG":          FALLBACK.fuel_mix["LPG"]   || Array(ys.length).fill(0),
      "Coal":         arr("coal_gj","fuel_mix.Coal"),
      "Diesel":       arr("diesel_gj","fuel_mix.Other"),
      "Biomass":      arr("biomass_gj","fuel_mix.Other"),
    };
    charts.energy = new Chart(energyCanvas.value, { type:"bar", data:{ labels,
      datasets:Object.entries(fuelData).filter(([,d])=>d.some(v=>v>0)).map(([n,d])=>({
        label:n, data:d, backgroundColor:fuelColors[n]||"#999", stack:"s", borderWidth:0 }))
    }, options:{ ...OPT(), scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true} } } });
  }

  // Water bar
  if (waterCanvas.value) {
    const wData = arr("water_m3","water").map(v=>v?v/1e6:null);
    charts.water = new Chart(waterCanvas.value, { type:"bar", data:{ labels,
      datasets:[{ label:"Withdrawals (M m³)", data:wData, backgroundColor:C.teal+"80", borderColor:C.teal, borderWidth:1, borderRadius:3 }]
    }, options:OPT() });
  }

  // Waste recovery line
  if (wasteCanvas.value) {
    const wrData = arr("waste_recovery_pct","waste_recov");
    charts.waste = new Chart(wasteCanvas.value, { type:"line", data:{ labels,
      datasets:[{ label:"Recovery Rate (%)", data:wrData, borderColor:C.waste, backgroundColor:"rgba(124,58,237,.08)", fill:true, tension:0.4, pointRadius:3, borderWidth:2.5 }]
    }, options:{ ...OPT(), scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} } });
  }
}

async function loadData() {
  try {
    const data = await api.getHomeData(auth.companyName, selectedYear.value);
    homeData.value = data;
    if (data?.available_years?.length) {
      availableYears.value = data.available_years.slice().sort((a,b)=>b-a);
    }
    // Build table from charts.years + kpi fields
    if (data?.charts?.years) {
      const ch = data.charts;
      seriesAll.value = ch.years.map((yr, i) => ({
        year:               yr,
        production_t:       ch.production_t?.[i],
        total_co2_t:        ch.total_co2_t?.[i],
        co2_kpi:            ch.co2_kpi?.[i],
        energy_kpi:         ch.energy_kpi?.[i],
        renewable_share_pct:ch.renewable_pct?.[i],
        water_kpi:          ch.water_kpi?.[i],
        waste_recovery_pct: ch.waste_recovery_pct?.[i],
      }));
    }
    await buildCharts();
  } catch(e) {
    console.error("Home load:", e);
    await buildCharts();
  }
}

onMounted(loadData);
onUnmounted(destroyAll);
watch(selectedYear, loadData);
</script>