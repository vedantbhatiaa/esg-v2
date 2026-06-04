<template>
  <div>
    <!-- Header with year selector + download -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900">{{ auth.companyName }}</h2>
        <p class="text-sm text-gray-400 mt-0.5">TIP ESG Sustainability Report · Tire Industry Project</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="selYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="h-8 px-4 bg-navy text-white rounded-lg text-sm font-medium hover:opacity-90" @click="printReport">
          ⬇ Download Report
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">Loading report data…</div>

    <template v-else>
      <!-- Cover band -->
      <div class="rounded-xl px-7 py-6 mb-5 relative overflow-hidden"
        style="background:linear-gradient(135deg,#0A2240 0%,#164E63 100%)">
        <div class="absolute -right-10 -top-10 w-40 h-40 rounded-full opacity-10 bg-white"></div>
        <div class="text-[20px] font-black text-white mb-1">{{ auth.companyName }}</div>
        <div class="text-[11.5px] text-white/40 mb-5">Sustainability Performance Report · {{ selYear }} · Verified by dss+ · Confidential</div>
        <div class="flex gap-8 flex-wrap">
          <div v-for="h in headlines" :key="h.label">
            <div class="text-[9.5px] text-white/35 uppercase tracking-wider">{{ h.label }}</div>
            <div class="text-[21px] font-bold text-white mt-0.5 leading-none">
              {{ h.value }}<span class="text-[12px] text-white/30 ml-1">{{ h.unit }}</span>
            </div>
            <div class="text-[10px] font-semibold mt-1" :class="h.good ? 'text-green-400' : 'text-red-400'">
              {{ h.delta }}
            </div>
          </div>
        </div>
      </div>

      <!-- 6 KPI cards -->
      <div class="grid grid-cols-6 gap-3 mb-5">
        <div v-for="k in kpiCards" :key="k.label"
          class="bg-white border border-gray-100 rounded-xl p-3 text-center">
          <div class="text-[9px] text-gray-400 uppercase tracking-wide font-semibold mb-1">{{ k.label }}</div>
          <div class="text-[19px] font-bold leading-none" :style="{color:k.color}">{{ k.value }}</div>
          <div class="text-[9px] text-gray-400 mt-0.5">{{ k.unit }}</div>
          <div v-if="k.yoy" class="text-[10px] font-semibold mt-1" :class="k.good?'text-green-600':'text-red-500'">{{ k.yoy }}</div>
        </div>
      </div>

      <!-- Section 1: Environmental -->
      <div class="border-l-4 border-[#475569] pl-3 mb-3">
        <div class="text-sm font-bold text-gray-800">1. Environmental Performance</div>
        <div class="text-xs text-gray-400">CO₂ emissions, energy consumption and climate targets</div>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-5">
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-xs font-semibold">Total CO₂ Emissions (T.CO₂)</div>
          <div class="p-3" style="height:180px"><canvas ref="co2ChartRef"></canvas></div>
        </div>
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-xs font-semibold">Energy Mix by Source (GJ)</div>
          <div class="p-3" style="height:180px"><canvas ref="fuelChartRef"></canvas></div>
        </div>
      </div>

      <!-- Section 2: Resource Efficiency -->
      <div class="border-l-4 border-[#0891B2] pl-3 mb-3">
        <div class="text-sm font-bold text-gray-800">2. Resource Efficiency</div>
        <div class="text-xs text-gray-400">Water withdrawals, waste management and circular economy</div>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-5">
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-xs font-semibold">Water Withdrawals (M m³)</div>
          <div class="p-3" style="height:180px"><canvas ref="waterChartRef"></canvas></div>
        </div>
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-xs font-semibold">Waste Recovery Rate (%)</div>
          <div class="p-3" style="height:180px"><canvas ref="wasteChartRef"></canvas></div>
        </div>
      </div>

      <!-- Section 3: Historical table -->
      <div class="border-l-4 border-[#16A34A] pl-3 mb-3">
        <div class="text-sm font-bold text-gray-800">3. Historical Performance Data</div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden mb-5">
        <div class="overflow-x-auto">
          <table class="w-full text-xs border-collapse">
            <thead><tr class="bg-gray-50">
              <th v-for="col in tableHeaders" :key="col"
                class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">
                {{ col }}
              </th>
            </tr></thead>
            <tbody>
              <tr v-for="row in tableRows" :key="row.year" class="border-b border-gray-50 last:border-none hover:bg-gray-50">
                <td class="px-4 py-2 font-bold text-navy">{{ row.year }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.co2_kpi }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.renew_pct }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.water_kpi }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.waste_rec }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.energy_kpi }}</td>
                <td class="px-4 py-2 tabular-nums">{{ row.production }}</td>
                <td class="px-4 py-2 font-medium" :class="row.trendClass">{{ row.trend }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center bg-gray-50 rounded-xl px-5 py-3 text-xs text-gray-400">
        <span>Methodology: GHG Protocol (Scope 1+2) · TIP KPI definitions v3.1 · IEA 2023 emission factors</span>
        <span>Generated {{ today }} · TIP ESG Platform powered by dss+</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { Chart } from "chart.js";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, TOOLTIP, ANIMATION, AXIS, YEARS, YEAR_LABELS } from "@/composables/useCharts.js";

const auth = useAuthStore();
const selYear = ref(2023);
const availableYears = ref([]);
const loading = ref(false);
const histData = ref({});   // { year: { kpis, raw } }

const today = new Date().toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric" });

const histYears = computed(() => Object.keys(histData.value).map(Number).sort((a,b)=>a-b));

const kpi = (yr) => histData.value[yr]?.kpis || {};
const raw = (yr) => histData.value[yr]?.raw || {};

const currentKPIs = computed(() => kpi(selYear.value));
const prevKPIs    = computed(() => kpi(selYear.value - 1));

function pct(cur, prev, down=true) {
  if (!prev || prev===0) return null;
  const p = ((cur-prev)/Math.abs(prev)*100).toFixed(1);
  return { val:`${p>0?"+":""}${p}%`, good:(p<0)===down };
}

const headlines = computed(() => {
  const k=currentKPIs.value; const p=prevKPIs.value;
  const re = k.renew_share_pct;
  const d1=pct(k.co2_kpi,p.co2_kpi); const d2=pct(k.energy_kpi,p.energy_kpi);
  const d3=re!=null&&p.renew_share_pct!=null?{val:`${(re-p.renew_share_pct).toFixed(1)}pp`,good:true}:null;
  const d4=pct(k.waste_recovery_pct,p.waste_recovery_pct,false);
  return [
    { label:"CO₂ Intensity",    value:k.co2_kpi?.toFixed(3)??"—",              unit:"T/T",  delta:d1?.val??"—", good:d1?.good??true },
    { label:"Energy KPI",       value:k.energy_kpi?.toFixed(2)??"—",           unit:"GJ/T", delta:d2?.val??"—", good:d2?.good??true },
    { label:"Renew. Share",     value:re?.toFixed(1)??"—",                     unit:"%",    delta:d3?.val??"—", good:true },
    { label:"Waste Recovery",   value:k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1):"—", unit:"%", delta:d4?.val??"—", good:d4?.good??true },
  ];
});

const kpiCards = computed(() => {
  const k=currentKPIs.value; const p=prevKPIs.value;
  const d=(cur,prv,dn=true)=>{ const r=pct(cur,prv,dn); return r?{yoy:r.val,good:r.good}:{}; };
  const re = k.renew_share_pct;
  return [
    { label:"CO₂ Intensity",  value:k.co2_kpi?.toFixed(3)??"—",             unit:"T.CO₂/T", color:C.co2,    ...d(k.co2_kpi,p.co2_kpi)       },
    { label:"Renewable Elec.",value:re?.toFixed(1)??"—",                    unit:"%",       color:C.renew,  ...d(re,p.renew_share_pct,false)  },
    { label:"Water KPI",      value:k.water_kpi?.toFixed(2)??"—",           unit:"m³/T",    color:C.water,  ...d(k.water_kpi,p.water_kpi)     },
    { label:"Waste Recovery", value:k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1):"—", unit:"%", color:C.waste, ...d(k.waste_recovery_pct,p.waste_recovery_pct,false) },
    { label:"Energy KPI",     value:k.energy_kpi?.toFixed(2)??"—",          unit:"GJ/T",    color:C.energy, ...d(k.energy_kpi,p.energy_kpi)   },
    { label:"Production",     value:raw(selYear.value).production?(raw(selYear.value).production/1e6).toFixed(2):"—", unit:"M T", color:C.navy },
  ];
});

const tableHeaders = ["Year","CO₂ KPI (T/T)","Renew. %","Water KPI (m³/T)","Waste Rec. %","Energy KPI (GJ/T)","Production (M T)","Trend"];
const tableRows = computed(() => histYears.value.slice().reverse().slice(0,10).map((y,i,arr) => {
  const k=kpi(y); const pk=i<arr.length-1?kpi(arr[i+1]):null;
  const co2=k.co2_kpi; const pco2=pk?.co2_kpi;
  const good = pco2&&co2 ? co2<pco2 : null;
  return {
    year:       y,
    co2_kpi:    co2?.toFixed(3)??"—",
    renew_pct:  k.renew_share_pct?.toFixed(1)+"%"??"—",
    water_kpi:  k.water_kpi?.toFixed(2)??"—",
    waste_rec:  k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1)+"%":"—",
    energy_kpi: k.energy_kpi?.toFixed(2)??"—",
    production: raw(y).production?(raw(y).production/1e6).toFixed(2):"—",
    trend:      good===null?"—":good?"▼ improving":"▲ watch",
    trendClass: good===null?"text-gray-400":good?"text-green-600":"text-red-500",
  };
}));

// Charts
const co2ChartRef=ref(null), fuelChartRef=ref(null), waterChartRef=ref(null), wasteChartRef=ref(null);
const charts = {};

function destroyAll() { Object.values(charts).forEach(c=>{ try{c.destroy()}catch(_){} }); }

const OPT = (extra={}) => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:false }, tooltip:TOOLTIP },
  scales:AXIS, ...extra
});

async function buildCharts() {
  await nextTick();
  const ys = histYears.value;
  const labels = ys.map(y=>`'${String(y).slice(2)}`);

  // CO2 total trend
  if (co2ChartRef.value) {
    if (charts.co2) { try{charts.co2.destroy()}catch(_){} }
    charts.co2 = new Chart(co2ChartRef.value, { type:"line", data:{ labels, datasets:[{
      label:"Total CO₂", data:ys.map(y=>kpi(y).total_co2||null),
      borderColor:C.co2, backgroundColor:"rgba(71,85,105,.08)", fill:true, tension:0.4, pointRadius:3, borderWidth:2
    }]}, options:OPT() });
  }

  // Fuel mix donut for selected year
  if (fuelChartRef.value) {
    if (charts.fuel) { try{charts.fuel.destroy()}catch(_){} }
    const r = raw(selYear.value);
    const fuelData=[r.nat_gas||0,r.nonrenew_elec_purchased||0,r.lpg||0,r.coal_sub||0,r.diesel||0,(r.other_fuels||0)+(r.biomass||0)];
    charts.fuel = new Chart(fuelChartRef.value, { type:"doughnut", data:{ labels:["Natural Gas","Electricity","LPG","Coal","Diesel","Other"],
      datasets:[{ data:fuelData, backgroundColor:[C.energy,"#3B82F6","#8B5CF6","#6B7280","#78716C","#94A3B8"], borderWidth:0, hoverOffset:5 }]},
      options:{ ...OPT(), scales:undefined, cutout:"55%", plugins:{ legend:{ display:true, position:"right", labels:{ color:"#64748B", boxWidth:9, font:{size:10} } }, tooltip:TOOLTIP } }
    });
  }

  // Water bar
  if (waterChartRef.value) {
    if (charts.water) { try{charts.water.destroy()}catch(_){} }
    charts.water = new Chart(waterChartRef.value, { type:"bar", data:{ labels, datasets:[{
      label:"Water (M m³)", data:ys.map(y=>(raw(y).water_withdrawals||0)/1e6||null),
      backgroundColor:C.water+"80", borderColor:C.water, borderWidth:1, borderRadius:3
    }]}, options:OPT() });
  }

  // Waste recovery line
  if (wasteChartRef.value) {
    if (charts.waste) { try{charts.waste.destroy()}catch(_){} }
    charts.waste = new Chart(wasteChartRef.value, { type:"line", data:{ labels, datasets:[
      { label:"Recovery %", data:ys.map(y=>kpi(y).waste_recovery_pct!=null?kpi(y).waste_recovery_pct*100:null),
        borderColor:C.waste, backgroundColor:"rgba(124,58,237,.08)", fill:true, tension:0.4, pointRadius:3, borderWidth:2.5 },
      { label:"Target 90%", data:ys.map(()=>90), borderColor:C.renew, borderDash:[6,3], pointRadius:0, borderWidth:1.5, backgroundColor:"transparent" },
    ]}, options:{ ...OPT(), scales:{...AXIS, y:{...AXIS.y, ticks:{...AXIS.y.ticks, callback:v=>v+"%"}}} } });
  }
}

async function loadData() {
  loading.value = true;
  try {
    const summary = await api.getCompanyData(auth.companyName);
    if (summary?.years) {
      availableYears.value = summary.years.slice().sort((a,b)=>b-a);
      if (!availableYears.value.includes(selYear.value)) selYear.value = availableYears.value[0] || 2023;
    }
    // Load raw+kpis for all years in parallel
    await Promise.all((summary?.years||[]).map(async y => {
      try {
        const d = await api.getCompanyData(auth.companyName, y);
        if (d) histData.value[y] = { raw: d.raw||{}, kpis: d.kpis||{} };
      } catch(_) {}
    }));
    await buildCharts();
  } catch(e) { console.error("Reports:", e); }
  finally { loading.value = false; }
}

function printReport() { window.print(); }

onMounted(loadData);
onUnmounted(destroyAll);
watch(selYear, buildCharts);
</script>

<style>
@media print {
  aside, nav, button, select { display: none !important; }
  main { padding: 0 !important; }
}
</style>