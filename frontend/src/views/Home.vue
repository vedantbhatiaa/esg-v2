<template>
  <div>
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <h2 class="text-[20px] font-bold text-[#0F172A] leading-tight">Welcome, {{ firstName }} 👋</h2>
        <p class="text-[13px] text-[#64748B] mt-1">{{ auth.companyName }} · Your Performance Dashboard</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="selYear" @change="loadData"
          class="h-9 border border-[#E2E8F0] rounded-lg px-3 text-sm bg-white text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-green-500">
          <option v-for="y in availYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <router-link to="/entry"
          class="h-9 px-4 bg-[#0A2240] text-white rounded-lg text-sm font-semibold flex items-center gap-2 hover:bg-[#1a3560] transition-colors no-underline">
          📋 Submit Data
        </router-link>
      </div>
    </div>

    <!-- Submission status strip -->
    <div class="bg-white border border-[#E2E8F0] rounded-[8px] px-5 py-3 mb-4 flex items-center gap-4"
      style="animation:tipFadeIn 350ms ease-out">
      <div class="flex-1">
        <div class="text-[12px] text-[#64748B] mb-1.5">{{ selYear }} Submission Status</div>
        <div class="bg-[#F1F5F9] rounded h-[6px] overflow-hidden">
          <div class="h-full rounded transition-all duration-700"
            :style="{ width: statusPct + '%', background: statusColor }"></div>
        </div>
      </div>
      <div class="text-[18px] font-bold" :style="{ color: statusColor }">{{ statusDone }}/6</div>
      <div class="text-[12px] text-[#64748B]">sections complete</div>
      <div class="border-l border-[#E2E8F0] pl-4 text-[12px] font-semibold whitespace-nowrap"
        :style="{ color: verifColor }">
        {{ verifIcon }} {{ verifLabel }}
      </div>
    </div>

    <!-- 8 KPI cards (2 rows × 4) -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <div v-for="(card, i) in kpiCards" :key="card.label"
        class="bg-white border border-[#E2E8F0] rounded-[10px] px-[18px] py-4 flex flex-col justify-between cursor-default select-none hover:-translate-y-[2px] hover:shadow-[0_6px_20px_rgba(15,23,42,.1)] transition-all"
        style="height:110px"
        :style="{ animation: `tipFadeIn 400ms ease-out ${i*70}ms both` }">
        <div class="text-[10.5px] font-semibold text-[#64748B] uppercase tracking-[.6px] leading-none">{{ card.label }}</div>
        <div class="text-[26px] font-bold leading-none font-['Inter'] tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
          :style="{ color: card.color }">
          {{ card.value }}
          <span class="text-[11px] font-normal text-[#64748B] ml-[2px]">{{ card.unit }}</span>
        </div>
        <div v-if="card.chip" v-html="card.chip"></div>
      </div>
    </div>

    <!-- Chart tabs -->
    <div class="bg-white border border-[#E2E8F0] rounded-[10px] overflow-hidden mb-4">
      <div class="flex border-b border-[#F1F5F9] overflow-x-auto">
        <button v-for="tab in TABS" :key="tab.id" @click="activeTab=tab.id"
          class="px-4 py-3 text-[12.5px] font-medium border-b-2 whitespace-nowrap transition-colors"
          :class="activeTab===tab.id
            ? 'border-[#0A2240] text-[#0A2240] font-semibold'
            : 'border-transparent text-[#64748B] hover:text-[#0F172A]'">
          {{ tab.label }}
        </button>
      </div>
      <div class="p-4">
        <div v-show="activeTab==='co2'" style="height:320px"><canvas ref="co2Canvas"></canvas></div>
        <div v-show="activeTab==='energy'">
          <div style="height:320px"><canvas ref="energyCanvas"></canvas></div>
        </div>
        <div v-show="activeTab==='water'">
          <div style="height:320px"><canvas ref="waterCanvas"></canvas></div>
        </div>
        <div v-show="activeTab==='waste'" class="grid grid-cols-3 gap-3">
          <div class="col-span-2" style="height:300px"><canvas ref="wasteCanvas"></canvas></div>
          <div style="height:300px"><canvas ref="wasteRecCanvas"></canvas></div>
        </div>
      </div>
    </div>

    <!-- Historical KPI summary table -->
    <div class="bg-white border border-[#E2E8F0] rounded-[10px] overflow-hidden">
      <div class="px-5 py-3 border-b border-[#F8FAFC]">
        <span class="text-[13px] font-semibold text-[#0F172A]">Historical KPI Summary — {{ auth.companyName }}</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-[12px]">
          <thead>
            <tr class="bg-[#F8FAFC]">
              <th v-for="h in TABLE_HEADERS" :key="h"
                class="px-4 py-2.5 text-left text-[10px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0]">
                {{ h }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!tableRows.length">
              <td :colspan="TABLE_HEADERS.length" class="px-5 py-8 text-center text-[#64748B]">
                No data yet. Submit your first KPI report.
              </td>
            </tr>
            <tr v-for="row in tableRows" :key="row.year"
              class="border-b border-[#F8FAFC] last:border-none hover:bg-[#F8FAFC] transition-colors">
              <td class="px-4 py-2.5 font-bold text-[#0F172A]">{{ row.year }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.production }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.total_co2 }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.co2_kpi }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.energy_kpi }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.renew_pct }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.water_kpi }}</td>
              <td class="px-4 py-2 text-right tabular-nums">{{ row.waste_pct }}</td>
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
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, FALLBACK, YEARS, YEAR_LABELS, TOOLTIP, AXIS, ANIMATION } from "@/composables/useCharts.js";

const auth     = useAuthStore();
const selYear  = ref(2023);
const availYrs = ref(YEARS.slice().reverse());
const loading  = ref(false);

// Data from API (yr_kpis array matching Streamlit)
const homeData   = ref(null);
const yrKpis     = ref([]);   // [{year, scope1, scope2, co2_kpi, energy_kpi, ...}]
const kpiCards_  = ref({});
const yoy_       = ref({});
const sub_status = ref({sections_done:0, total_sections:6, verification:"Pending"});

const firstName = computed(() => (auth.companyName || "").split(" ")[0] || "there");

const TABLE_HEADERS = ["Year","Production (MT)","CO₂ Total (T)","CO₂ Intensity","Energy KPI (GJ/T)","Renew. Elec. %","Water KPI (m³/T)","Waste Recovery %"];
const TABS = [
  { id:"co2",    label:"📈 CO₂ Trend" },
  { id:"energy", label:"⚡ Energy Mix" },
  { id:"water",  label:"💧 Water" },
  { id:"waste",  label:"♻️ Waste & Fuel" },
];
const activeTab = ref("co2");

// ── Submission status (matches Streamlit logic)
const statusDone  = computed(() => sub_status.value.sections_done || 0);
const statusPct   = computed(() => (statusDone.value / 6) * 100);
const statusColor = computed(() => statusPct.value===100?"#16A34A":statusPct.value>=50?"#F59E0B":"#DC2626");
const VERIF_MAP = {
  Verified: { label:"Verified by dss+", color:"#16A34A", icon:"✓" },
  Pending:  { label:"Pending Review",   color:"#F59E0B", icon:"◉" },
  Flagged:  { label:"Flagged — see notes", color:"#DC2626", icon:"⚑" },
};
const verifInfo  = computed(() => VERIF_MAP[sub_status.value.verification] || { label:"Not Submitted", color:"#94A3B8", icon:"○" });
const verifColor = computed(() => verifInfo.value.color);
const verifLabel = computed(() => verifInfo.value.label);
const verifIcon  = computed(() => verifInfo.value.icon);

// ── KPI cards (exact match with Streamlit cards[] list)
const CAT_CO2    = "#475569";
const CAT_ENERGY = "#F59E0B";
const CAT_WATER  = "#0891B2";
const CAT_WASTE  = "#7C3AED";
const CAT_RENEW  = "#16A34A";

function yoyChip(pctChange, lowerGood = true) {
  if (pctChange == null) return "";
  const good = lowerGood ? pctChange <= 0 : pctChange >= 0;
  const bg   = good ? "#DCFCE7" : "#FEE2E2";
  const col  = good ? "#166534" : "#991B1B";
  const arr  = pctChange < 0 ? "▼" : "▲";
  const sign = pctChange > 0 ? "+" : "";
  return `<span style="background:${bg};color:${col};font-size:10px;font-weight:600;padding:2px 7px;border-radius:4px">${arr}${sign}${pctChange.toFixed(1)}%</span>`;
}

const kpiCards = computed(() => {
  const k = kpiCards_.value; const y = yoy_.value;
  if (!k.co2_abs && !k.co2_kpi && !k.energy_kpi) {
    // Show empty cards while loading
    return ["CO₂ Absolute","CO₂ Intensity","Energy Intensity","Renewable Share","Water Intensity","Water Withdrawal","Waste Recovery","ISO 14001"].map((label,i)=>({
      label, value:"—", unit:"", chip:"", color:[CAT_CO2,CAT_CO2,CAT_ENERGY,CAT_RENEW,CAT_WATER,CAT_WATER,CAT_WASTE,CAT_RENEW][i]
    }));
  }
  const fmt = (v,d) => v!=null&&v>0 ? Number(v).toFixed(d) : "—";
  const fmtInt = (v) => v>0 ? Number(v).toLocaleString() : "—";
  return [
    { label:"CO₂ Absolute",   value:fmtInt(k.co2_abs),          unit:"T.CO₂", chip:yoyChip(y.co2_abs),           color:CAT_CO2    },
    { label:"CO₂ Intensity",  value:fmt(k.co2_kpi,3),           unit:"T/T",   chip:yoyChip(y.co2_kpi),            color:CAT_CO2    },
    { label:"Energy Intensity",value:fmt(k.energy_kpi,2),        unit:"GJ/T",  chip:yoyChip(y.energy_kpi),         color:CAT_ENERGY },
    { label:"Renewable Share", value:fmt(k.renew_share_pct,1),   unit:"%",     chip:yoyChip(y.renew_share_pct,false), color:CAT_RENEW },
    { label:"Water Intensity", value:fmt(k.water_kpi,2),         unit:"m³/T",  chip:yoyChip(y.water_kpi),          color:CAT_WATER  },
    { label:"Water Withdrawal",value:fmtInt(k.water_withdrawals),unit:"m³",    chip:"",                            color:CAT_WATER  },
    { label:"Waste Recovery",  value:fmt(k.waste_recov_pct,1),   unit:"%",     chip:yoyChip(y.waste_recov_pct,false), color:CAT_WASTE },
    { label:"ISO 14001",       value:fmt(k.iso_pct,0),           unit:"%",     chip:"",                            color:CAT_RENEW  },
  ];
});

// ── Historical table
const tableRows = computed(() => {
  const yrs = yrKpis.value.filter(e => e.year >= 2014).slice().reverse().slice(0,10);
  return yrs.map(e => ({
    year:       e.year,
    production: e.production>0 ? (e.production/1e6).toFixed(3) : "—",
    total_co2:  e.total_co2>0  ? Number(e.total_co2).toLocaleString() : "—",
    co2_kpi:    e.co2_kpi>0    ? e.co2_kpi.toFixed(3) : "—",
    energy_kpi: e.energy_kpi>0 ? e.energy_kpi.toFixed(2) : "—",
    renew_pct:  e.renew_pct!=null ? e.renew_pct.toFixed(1)+"%" : "—",
    water_kpi:  e.water_kpi>0  ? e.water_kpi.toFixed(2) : "—",
    waste_pct:  e.waste_pct!=null ? e.waste_pct.toFixed(1)+"%" : "—",
  }));
});

// ── Charts
const co2Canvas=ref(null), energyCanvas=ref(null), waterCanvas=ref(null), wasteCanvas=ref(null), wasteRecCanvas=ref(null);
const charts = {};

function destroyAll() { Object.values(charts).forEach(c=>{ try{c.destroy()}catch(_){} }); }

const OPT = (extra={}) => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"bottom", labels:{ color:"#64748B", boxWidth:9, font:{size:11}, padding:12 } }, tooltip:TOOLTIP },
  scales:AXIS, interaction:{ mode:"index", intersect:false }, ...extra,
});

async function buildCharts() {
  await nextTick();
  destroyAll();
  const ys = yrKpis.value;
  if (!ys.length) return;
  const labels = ys.map(e => `\'${String(e.year).slice(2)}`);

  // CO2: Stacked area scope1+scope2 with intensity line (matches Streamlit t1)
  if (co2Canvas.value) {
    charts.co2 = new Chart(co2Canvas.value, {
      type:"line",
      data:{ labels, datasets:[
        { label:"Scope 2", data:ys.map(e=>e.scope2||0), fill:true, backgroundColor:"rgba(71,85,105,0.25)",
          borderColor:"transparent", tension:0.3, pointRadius:0, stack:"co2" },
        { label:"Scope 1", data:ys.map(e=>e.scope1||0), fill:true, backgroundColor:"rgba(71,85,105,0.5)",
          borderColor:"transparent", tension:0.3, pointRadius:0, stack:"co2" },
        { label:"CO₂ Intensity (T/T)", data:ys.map(e=>e.co2_kpi||0), yAxisID:"y2",
          borderColor:"#C8102E", borderWidth:2.5, borderDash:[5,3],
          pointRadius:5, pointBackgroundColor:"#C8102E", tension:0.3,
          backgroundColor:"transparent", fill:false },
      ]},
      options:{ ...OPT({
        scales:{ ...AXIS,
          y:{ ...AXIS.y, title:{ display:true, text:"T.CO₂", font:{size:11}, color:CAT_CO2 }, stacked:true },
          y2:{ type:"linear", position:"right", grid:{display:false}, ticks:{ color:"#C8102E", font:{size:10} },
               title:{ display:true, text:"T.CO₂/T prod.", font:{size:11}, color:"#C8102E" } },
        },
        hoverMode:"index",
      })}
    });
  }

  // Energy: Stacked bar by source (matches Streamlit t2)
  if (energyCanvas.value) {
    const fuelDefs = [
      { label:"Renewable Elec.",  key:"renew_elec",   color:CAT_RENEW  },
      { label:"Non-Renew. Elec.", key:"nonrenew_elec",color:"#94A3B8"  },
      { label:"Natural Gas",      key:"nat_gas",       color:CAT_ENERGY },
      { label:"Coal",             key:"coal",          color:"#475569"  },
      { label:"Diesel",           key:"diesel",        color:"#78716C"  },
      { label:"Biomass",          key:"biomass",       color:CAT_RENEW+"99" },
    ];
    const datasets = fuelDefs
      .filter(d => ys.some(e => (e[d.key]||0)>0))
      .map(d => ({ label:d.label, data:ys.map(e=>e[d.key]||0),
        backgroundColor:d.color, borderWidth:0, stack:"s" }));
    charts.energy = new Chart(energyCanvas.value, {
      type:"bar",
      data:{ labels, datasets },
      options:{ ...OPT({ scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true,
        title:{display:true,text:"GJ",font:{size:11},color:"#64748B"} }, }, bargap:0.3 }) },
    });
  }

  // Water: Bar withdrawals + intensity line (matches Streamlit t3)
  if (waterCanvas.value) {
    charts.water = new Chart(waterCanvas.value, {
      type:"bar",
      data:{ labels, datasets:[
        { label:"Total Withdrawals", data:ys.map(e=>e.water_m3||0),
          backgroundColor:CAT_WATER+"CC", borderWidth:0, borderRadius:2, order:2 },
        { label:"Intensity (m³/T)", data:ys.map(e=>e.water_kpi||0), type:"line",
          yAxisID:"y2", borderColor:"#0E7490", borderWidth:2.5,
          pointRadius:6, pointBackgroundColor:"#0E7490", pointStyle:"diamond",
          backgroundColor:"transparent", fill:false, order:1 },
      ]},
      options:{ ...OPT({
        scales:{ ...AXIS,
          y:{ ...AXIS.y, title:{display:true,text:"m³",font:{size:11},color:CAT_WATER} },
          y2:{ type:"linear", position:"right", grid:{display:false}, ticks:{color:"#0E7490",font:{size:10}},
               title:{display:true,text:"m³/T (intensity)",font:{size:11},color:"#0E7490"} },
        },
      })},
    });
  }

  // Waste: overlay bar + recovery % line (matches Streamlit t4 c1)
  if (wasteCanvas.value) {
    charts.waste = new Chart(wasteCanvas.value, {
      type:"bar",
      data:{ labels, datasets:[
        { label:"Total Waste", data:ys.map(e=>e.waste_total||0),
          backgroundColor:"#E2E8F0", borderWidth:0 },
        { label:"Recovered",   data:ys.map(e=>e.waste_recovery||0),
          backgroundColor:CAT_WASTE, borderWidth:0 },
        { label:"Recovery %",  data:ys.map(e=>e.waste_pct||0), type:"line",
          yAxisID:"y2", borderColor:"#6D28D9", borderWidth:2.5,
          pointRadius:6, pointBackgroundColor:"#6D28D9",
          backgroundColor:"transparent", fill:false },
      ]},
      options:{ ...OPT({
        scales:{ ...AXIS,
          y:{ ...AXIS.y, title:{display:true,text:"Metric T",font:{size:11},color:"#64748B"} },
          y2:{ type:"linear", position:"right", grid:{display:false}, min:0, max:110,
               ticks:{color:"#6D28D9",font:{size:10},callback:v=>v+"%"},
               title:{display:true,text:"Recovery %",font:{size:11},color:"#6D28D9"} },
        },
      })},
    });
  }

  // Waste recovery trend (matches Streamlit t4 c2)
  if (wasteRecCanvas.value) {
    charts.wasteRec = new Chart(wasteRecCanvas.value, {
      type:"line",
      data:{ labels, datasets:[
        { label:"Recovery %", data:ys.map(e=>e.waste_pct||0),
          borderColor:CAT_WASTE, borderWidth:2.5,
          backgroundColor:"rgba(124,58,237,0.10)", fill:true,
          pointRadius:6, pointBackgroundColor:CAT_WASTE,
          pointBorderColor:"white", pointBorderWidth:1.5, tension:0.3 },
        { label:"Target 90%", data:ys.map(()=>90),
          borderColor:CAT_RENEW, borderWidth:1.5, borderDash:[5,3],
          pointRadius:0, backgroundColor:"transparent", fill:false },
      ]},
      options:{ ...OPT({
        scales:{ ...AXIS,
          y:{ ...AXIS.y, min:0, max:105, ticks:{ ...AXIS.y.ticks, callback:v=>v+"%" } },
        },
        plugins:{ ...OPT().plugins, legend:{ display:false } },
      })},
    });
  }
}

async function loadData() {
  if (!auth.companyName) return;
  loading.value = true;
  try {
    // dss+ Analyst has no company CSV — use first real company or selected company
    const company = auth.isDss
      ? (dssSelectedCompany.value || "VerdaTyres Corp")
      : auth.companyName;
    const data = await api.getHomeData(company, selYear.value);
    homeData.value   = data;
    yrKpis.value     = data?.yr_kpis || [];
    kpiCards_.value  = data?.kpi_cards || {};
    yoy_.value       = data?.yoy || {};
    sub_status.value = data?.submission_status || { sections_done:0, total_sections:6, verification:"Pending" };
    if (data?.available_years?.length) {
      availYrs.value = data.available_years.slice().sort((a,b)=>b-a);
      if (!availYrs.value.includes(selYear.value)) selYear.value = availYrs.value[0];
    }
    await buildCharts();
  } catch(e) {
    console.error("Home load:", e);
    // Use fallback data for charts
    yrKpis.value = YEARS.map((y,i) => ({
      year:y, scope1:FALLBACK.scope1[i]*1e6, scope2:FALLBACK.scope2[i]*1e6,
      co2_kpi:FALLBACK.co2_kpi[i], energy_kpi:FALLBACK.energy_kpi[i],
      water_kpi:FALLBACK.water[i]/20,
      renew_pct:FALLBACK.renew_pct[i], waste_pct:FALLBACK.waste_recov[i],
      nat_gas:FALLBACK.fuel_mix["Natural Gas"][i]*1e5,
      nonrenew_elec:FALLBACK.fuel_mix["Electricity"][i]*1e5,
      renew_elec:FALLBACK.renew_pct[i]*1e4,
      coal:FALLBACK.fuel_mix["Coal"][i]*1e4,
      diesel:FALLBACK.fuel_mix["Other"][i]*1e4, biomass:0,
      water_m3:FALLBACK.water[i]*1e6,
      waste_total:335000, waste_recovery:285000, production:FALLBACK.prod[i]*1e6,
      total_co2:(FALLBACK.scope1[i]+FALLBACK.scope2[i])*1e6,
    }));
    await buildCharts();
  } finally { loading.value = false; }
}

onMounted(async () => {
  // Load company list for dss+ dropdown
  if (auth.isDss) {
    try {
      const cos = await api.getCompanies();
      if (Array.isArray(cos) && cos.length) {
        dssCompanies.value = cos.filter(n => n !== "dss+ Analyst");
        dssSelectedCompany.value = dssCompanies.value[0] || "VerdaTyres Corp";
      }
    } catch(_) {}
  }
  await loadData();
});
onUnmounted(destroyAll);
watch(selYear, loadData);
</script>