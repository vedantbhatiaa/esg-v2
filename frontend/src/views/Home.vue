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
        <router-link to="/submit"
          class="h-8 px-3 text-white rounded-lg text-sm font-medium flex items-center hover:opacity-90 transition-opacity no-underline"
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
        {{ verifIcon }} {{ verifStatus }}
      </div>
    </div>

    <!-- 8 KPI cards (2 × 4) -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <KPICard v-for="(card, i) in kpiCards" :key="card.label"
        :label="card.label" :value="card.value" :unit="card.unit"
        :delta="card.delta" :color="card.color" :delay="i * 60" />
    </div>

    <!-- 4 chart tabs -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden mb-4">
      <div class="flex border-b border-gray-100 overflow-x-auto">
        <button v-for="tab in tabs" :key="tab.id" @click="setTab(tab.id)"
          class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap"
          :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
          {{ tab.label }}
        </button>
      </div>
      <div class="p-4">
        <div v-show="activeTab==='co2'"    style="height:260px"><canvas ref="co2Chart"></canvas></div>
        <div v-show="activeTab==='energy'" style="height:260px"><canvas ref="energyChart"></canvas></div>
        <div v-show="activeTab==='water'"  style="height:260px"><canvas ref="waterChart"></canvas></div>
        <div v-show="activeTab==='waste'"  style="height:260px"><canvas ref="wasteChart"></canvas></div>
      </div>
    </div>

    <!-- Historical table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-50 text-sm font-semibold">
        Historical KPI Summary — {{ auth.companyName }}
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-xs border-collapse">
          <thead><tr class="bg-gray-50">
            <th v-for="col in tableHeaders" :key="col"
              class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">
              {{ col }}
            </th>
          </tr></thead>
          <tbody>
            <tr v-if="!tableRows.length">
              <td :colspan="tableHeaders.length" class="px-5 py-6 text-center text-gray-400">
                No historical data. Submit your first KPI report.
              </td>
            </tr>
            <tr v-for="row in tableRows" :key="row.year"
              class="border-b border-gray-50 last:border-none hover:bg-gray-50 transition-colors">
              <td class="px-4 py-2.5 font-bold text-navy">{{ row.year }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.production }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.co2_total }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.co2_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.energy_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.renew_pct }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.water_kpi }}</td>
              <td class="px-4 py-2.5 tabular-nums">{{ row.waste_rec }}</td>
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
import { C, TOOLTIP, ANIMATION, AXIS, YEAR_LABELS, YEARS, FALLBACK, mergeSeries } from "@/composables/useCharts.js";

const auth = useAuthStore();
const selectedYear   = ref(2023);
const availableYears = ref([]);     // populated from API — not hardcoded
const activeTab      = ref("co2");
const companyKPIs    = ref(null);
const companySeries  = ref({});
const tableRows      = ref([]);

const firstName = computed(() => (auth.userName || "").split(" ")[0] || "there");

const tabs = [
  { id:"co2",    label:"📈 CO₂ Trend" },
  { id:"energy", label:"⚡ Energy Mix" },
  { id:"water",  label:"💧 Water" },
  { id:"waste",  label:"♻ Waste & Fuel" },
];

// ── Year options: use all YEARS as fallback, override with API data
const yearOptions = computed(() => availableYears.value.length ? availableYears.value : YEARS.slice().reverse());

// ── KPI cards
const kpiCards = computed(() => {
  const k = companyKPIs.value;
  const fmt = (v, d) => v != null && v > 0 ? Number(v).toFixed(d) : "—";
  const delta = (cur, prev) => {
    if (!prev || prev === 0 || !cur) return null;
    const pct = ((cur - prev) / Math.abs(prev) * 100).toFixed(1);
    return `${pct > 0 ? "+" : ""}${pct}%`;
  };

  if (!k) return [
    { label:"CO₂ Intensity",   value:"—", unit:"T.CO₂/T",  delta:null, color:C.co2    },
    { label:"Energy Intensity",value:"—", unit:"GJ/T",      delta:null, color:C.energy },
    { label:"Water Intensity", value:"—", unit:"m³/T",      delta:null, color:C.water  },
    { label:"Renewable Elec.", value:"—", unit:"%",         delta:null, color:C.renew  },
    { label:"Total CO₂",       value:"—", unit:"T.CO₂",     delta:null, color:C.co2    },
    { label:"Total Energy",    value:"—", unit:"GJ",        delta:null, color:C.navy   },
    { label:"Waste Recovery",  value:"—", unit:"%",         delta:null, color:C.waste  },
    { label:"ISO 14001",       value:"—", unit:"%",         delta:null, color:C.renew  },
  ];
  const p = k.prev_kpis;
  return [
    { label:"CO₂ Intensity",   value:fmt(k.co2_kpi,3),                                   unit:"T.CO₂/T",  delta:p?delta(k.co2_kpi,p.co2_kpi):null,       color:C.co2    },
    { label:"Energy Intensity",value:fmt(k.energy_kpi,2),                                 unit:"GJ/T",     delta:p?delta(k.energy_kpi,p.energy_kpi):null,   color:C.energy },
    { label:"Water Intensity", value:fmt(k.water_kpi,2),                                  unit:"m³/T",     delta:p?delta(k.water_kpi,p.water_kpi):null,     color:C.water  },
    { label:"Renewable Elec.", value:k.renew_share_pct!=null?k.renew_share_pct.toFixed(1):"—", unit:"%", delta:null, color:C.renew },
    { label:"Total CO₂",       value:k.total_co2?(k.total_co2/1e6).toFixed(2)+"M":"—",   unit:"T.CO₂",    delta:null,                                       color:C.co2    },
    { label:"Total Energy",    value:k.total_energy?(k.total_energy/1e6).toFixed(1)+"M":"—", unit:"GJ",   delta:null,                                       color:C.navy   },
    { label:"Waste Recovery",  value:k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1):"—", unit:"%", delta:null, color:C.waste },
    { label:"ISO 14001",       value:k.pct_certified?(k.pct_certified*100).toFixed(0):"—", unit:"%",      delta:null,                                       color:C.renew  },
  ];
});

// ── Submission status
const statusDone  = computed(() => {
  const k = companyKPIs.value;
  if (!k) return 0;
  return [k.co2_kpi, k.energy_kpi, k.water_kpi, k.renew_share_pct, k.waste_recovery_pct, k.pct_certified]
    .filter(v => v != null && v > 0).length;
});
const statusPct   = computed(() => statusDone.value / 6 * 100);
const statusColor = computed(() => statusPct.value===100?"#16A34A":statusPct.value>=50?"#F59E0B":"#DC2626");
const verifStatus = ref("Not Submitted");
const verifColor  = ref("#94A3B8");
const verifIcon   = ref("○");

const tableHeaders = ["Year","Production (MT)","CO₂ Total (T)","CO₂ Intensity","Energy KPI (GJ/T)","Renew. Elec. %","Water KPI (m³/T)","Waste Recovery %"];

// ── Charts
const co2Chart = ref(null), energyChart = ref(null), waterChart = ref(null), wasteChart = ref(null);
const charts = {};

function destroyAll() { Object.values(charts).forEach(c => { try { c.destroy(); } catch(_) {} }); }

const OPT = (stacked) => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:11}, padding:9 } }, tooltip:TOOLTIP },
  scales: stacked
    ? { x:{...AXIS.x, stacked:true}, y:{...AXIS.y, stacked:true} }
    : AXIS,
  interaction:{ mode:"index", intersect:false },
});

async function buildCharts() {
  await nextTick();
  destroyAll();

  const s = companySeries.value;
  const ys = availableYears.value.length ? availableYears.value.slice().sort((a,b)=>a-b) : YEARS;
  const labels = ys.map(y => `'${String(y).slice(2)}`);

  // helper: get company series for a key
  const coSeries = (key) => ys.map(y => s[y]?.[key] ?? null);

  if (co2Chart.value) {
    const scope1 = coSeries("scope1"); const scope2 = coSeries("scope2");
    const hasCo2 = scope1.some(v=>v!=null);
    charts.co2 = new Chart(co2Chart.value, { type:"line", data:{ labels, datasets:[
      { label:"Scope 1", data: hasCo2 ? scope1 : mergeSeries(null, FALLBACK.scope1),
        borderColor:C.co2, backgroundColor:"rgba(71,85,105,.12)", fill:true, tension:0.4, pointRadius:3, borderWidth:2 },
      { label:"Scope 2", data: hasCo2 ? scope2 : mergeSeries(null, FALLBACK.scope2),
        borderColor:C.teal, backgroundColor:"rgba(8,145,178,.10)", fill:true, tension:0.4, pointRadius:3, borderWidth:2 },
    ]}, options:OPT(false) });
  }

  if (energyChart.value) {
    const fuelColors = {"Natural Gas":C.energy, "Electricity":"#3B82F6", "Fuel Oil":"#EF4444", "LPG":"#8B5CF6", "Coal":"#6B7280", "Other":"#D1D5DB"};
    const fm = FALLBACK.fuel_mix;
    charts.energy = new Chart(energyChart.value, { type:"bar", data:{ labels, datasets:
      Object.entries(fm).map(([name,vals])=>({ label:name, data:vals, backgroundColor:fuelColors[name]||"#999", borderWidth:0 }))
    }, options:{ ...OPT(true), plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:11} } }, tooltip:TOOLTIP } } });
  }

  if (waterChart.value) {
    const wm3 = coSeries("water_m3").map((v,i)=>v!=null?v/1e6:FALLBACK.water[i]);
    charts.water = new Chart(waterChart.value, { type:"bar", data:{ labels, datasets:[
      { label:"Withdrawals (M m³)", data:wm3, backgroundColor:C.teal+"80", borderColor:C.teal, borderWidth:1, borderRadius:3 }
    ]}, options:OPT(false) });
  }

  if (wasteChart.value) {
    const wr = coSeries("waste_pct").map((v,i)=>v!=null?v:FALLBACK.waste_recov[i]);
    charts.waste = new Chart(wasteChart.value, { type:"line", data:{ labels, datasets:[
      { label:"Recovery Rate (%)", data:wr, borderColor:C.waste, backgroundColor:"rgba(124,58,237,.08)", fill:true, tension:0.4, pointRadius:3, borderWidth:2.5 }
    ]}, options:{ ...OPT(false), scales:{ ...AXIS, y:{ ...AXIS.y, ticks:{ ...AXIS.y.ticks, callback:v=>v+"%" } } } } });
  }
}

function setTab(id) { activeTab.value = id; }

async function loadData() {
  try {
    // Load company-specific data (all years summary)
    const cd = await api.getCompanyData(auth.companyName);
    if (cd?.years) {
      availableYears.value = cd.years.slice().sort((a,b)=>b-a);
      if (!availableYears.value.includes(selectedYear.value))
        selectedYear.value = availableYears.value[0] || 2023;
    }

    if (cd?.summary) {
      tableRows.value = cd.summary.slice().sort((a,b)=>b.year-a.year).slice(0,10).map(r => ({
        year:       r.year,
        production: r.kpis?.total_energy ? ((r.kpis.production||0)/1e6).toFixed(3) : "—",
        co2_total:  r.kpis?.total_co2 ? Number(r.kpis.total_co2).toLocaleString() : "—",
        co2_kpi:    r.kpis?.co2_kpi?.toFixed(3) ?? "—",
        energy_kpi: r.kpis?.energy_kpi?.toFixed(2) ?? "—",
        renew_pct:  r.kpis?.renew_share_pct?.toFixed(1)+"%" ?? "—",
        water_kpi:  r.kpis?.water_kpi?.toFixed(2) ?? "—",
        waste_rec:  r.kpis?.waste_recovery_pct ? (r.kpis.waste_recovery_pct*100).toFixed(1)+"%" : "—",
      }));

      // Build company_series for charts
      const ser = {};
      for (const s of cd.summary) {
        const k = s.kpis || {};
        ser[s.year] = {
          scope1: k.total_co2_scope1, scope2: k.total_co2_scope2,
          co2_kpi: k.co2_kpi, energy_kpi: k.energy_kpi, water_kpi: k.water_kpi,
          water_m3: null, waste_pct: k.waste_recovery_pct!=null?k.waste_recovery_pct*100:null,
          renew_pct: k.renew_share_pct,
        };
      }
      companySeries.value = ser;
    }

    // Load selected year detail
    await loadYearDetail();
    await buildCharts();
  } catch(e) {
    console.error("HomeView loadData:", e);
    await buildCharts();
  }
}

async function loadYearDetail() {
  try {
    const yr = await api.getCompanyData(auth.companyName, selectedYear.value);
    if (yr?.kpis) {
      companyKPIs.value = yr.kpis;
      // Try to get raw for water m3
      if (yr.raw) {
        companySeries.value[selectedYear.value] = {
          ...(companySeries.value[selectedYear.value]||{}),
          water_m3: yr.raw.water_withdrawals,
        };
      }
    }
    if (yr?.verification_status) {
      const vs = yr.verification_status;
      verifStatus.value = vs==="Verified"?"Verified by dss+":vs==="Pending"?"Pending Review":vs==="Flagged"?"Flagged — see notes":"Not Submitted";
      verifColor.value  = vs==="Verified"?"#16A34A":vs==="Flagged"?"#DC2626":"#F59E0B";
      verifIcon.value   = vs==="Verified"?"✓":vs==="Flagged"?"⚑":"◉";
    }
  } catch(_) {}
}

onMounted(loadData);
onUnmounted(destroyAll);
watch(selectedYear, async () => { await loadYearDetail(); });
</script>