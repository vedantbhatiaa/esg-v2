<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900">My Dashboard</h2>
        <p class="text-sm text-gray-400 mt-0.5">TIP Sector Analysis · {{ auth.companyName }} highlighted</p>
      </div>
      <div class="flex gap-2 items-center">
        <select v-model="yearFrom" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option>
        </select>
        <span class="text-gray-400 text-sm">to</span>
        <select v-model="yearTo" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in YEARS.slice().reverse()" :key="y" :value="y">{{ y }}</option>
        </select>
        <label class="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer select-none">
          <input type="checkbox" v-model="highlightCompany" class="rounded" />
          Highlight {{ auth.companyName?.split(" ")[0] }}
        </label>
      </div>
    </div>

    <!-- 4 metric cards -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <div v-for="m in metrics" :key="m.label" class="bg-white border border-gray-100 rounded-xl p-4">
        <div class="text-xs text-gray-400 mb-1">{{ m.label }}</div>
        <div class="text-xl font-bold" :style="{color:m.color}">{{ m.value }}</div>
        <div class="text-xs text-gray-400">{{ m.unit }}</div>
        <div v-if="m.delta" class="text-[10px] font-medium mt-1" :class="m.deltaGood?'text-green-600':'text-red-500'">
          {{ m.delta }}
        </div>
      </div>
    </div>

    <!-- 2×2 chart grid -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">Sector CO₂ vs {{ shortName }}</div>
        <div class="p-3" style="height:240px"><canvas ref="co2Chart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">CO₂ Intensity Trend (T.CO₂/T)</div>
        <div class="p-3" style="height:240px"><canvas ref="co2KpiChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">Energy KPI vs Renewable Share</div>
        <div class="p-3" style="height:240px"><canvas ref="energyChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">Water Intensity Trend (m³/T)</div>
        <div class="p-3" style="height:240px"><canvas ref="waterChart"></canvas></div>
      </div>
    </div>

    <!-- Additional chart row -->
    <div class="grid grid-cols-2 gap-3">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">Renewable Electricity Share (%)</div>
        <div class="p-3" style="height:220px"><canvas ref="renewChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-sm font-semibold">CO₂ Intensity YoY Change (%)</div>
        <div class="p-3" style="height:220px"><canvas ref="yoyChart"></canvas></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { Chart } from "chart.js";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, TOOLTIP, ANIMATION, AXIS, YEARS, YEAR_LABELS, FALLBACK, mergeSeries } from "@/composables/useCharts.js";

const auth = useAuthStore();
const yearFrom = ref(2009);
const yearTo   = ref(2023);
const highlightCompany = ref(true);
const sectorData = ref(null);
const coSeries   = ref({});

const shortName = computed(() => auth.companyName?.split(" ")[0] || "You");

// ── filtered year range
const rangeYears  = computed(() => YEARS.filter(y => y>=yearFrom.value && y<=yearTo.value));
const rangeLabels = computed(() => rangeYears.value.map(y=>`'${String(y).slice(2)}`));

// ── sector series for range
function secSeries(key, div=1) {
  const raw = sectorData.value?.series?.[key];
  if (!raw || !raw.length) return rangeYears.value.map(y => { const i=YEARS.indexOf(y); return FALLBACK[key]?.[i]??null; });
  // analytics returns [{year,value}] — map to year range
  if (typeof raw[0] === "object" && "year" in raw[0]) {
    return rangeYears.value.map(y => {
      const item = raw.find(r => r.year === y);
      return item?.value != null ? item.value / div : null;
    });
  }
  return rangeYears.value.map(y => { const i=YEARS.indexOf(y); return raw[i]!=null?raw[i]/div:null; });
}
function coSeriesForRange(key) {
  return rangeYears.value.map(y => coSeries.value[y]?.[key]??null);
}

const secCo2Total  = computed(() => secSeries("scope1").map((v,i)=>(v||0)+(secSeries("scope2")[i]||0)));
const secEnergyKPI = computed(() => secSeries("energy_kpi"));
const secCo2KPI    = computed(() => secSeries("co2_kpi"));
const secWaterKPI  = computed(() => secSeries("water_kpi"));
const secRenewPct  = computed(() => secSeries("renew_pct"));

const coCo2KPI    = computed(() => coSeriesForRange("co2_kpi"));
const coEnergyKPI = computed(() => coSeriesForRange("energy_kpi"));
const coWaterKPI  = computed(() => coSeriesForRange("water_kpi"));
const coRenewPct  = computed(() => coSeriesForRange("renew_pct"));

// ── Metrics
const metrics = computed(() => {
  const s = sectorData.value?.series;
  const last = i => { const a = secSeries(i); return a[a.length-1]; };
  const dlta = (cur, prev, down=true) => {
    if (!cur||!prev||prev===0) return null;
    const pct = ((cur-prev)/Math.abs(prev)*100).toFixed(1);
    return { delta:`${pct>0?"+":""}${pct}%`, good:(pct<0)===down };
  };
  const ck = secSeries("co2_kpi"); const ek = secSeries("energy_kpi");
  const wk = secSeries("water_kpi"); const rp = secSeries("renew_pct");
  const d1=dlta(ck[ck.length-1],ck[ck.length-2]); const d2=dlta(ek[ek.length-1],ek[ek.length-2]);
  return [
    { label:"Sector CO₂ Intensity", value:ck[ck.length-1]?.toFixed(3)??"—", unit:"T.CO₂/T avg", color:C.co2,    delta:d1?.delta, deltaGood:d1?.good },
    { label:"Sector Energy KPI",    value:ek[ek.length-1]?.toFixed(2)??"—", unit:"GJ/T avg",     color:C.energy, delta:d2?.delta, deltaGood:d2?.good },
    { label:"Sector Water KPI",     value:wk[wk.length-1]?.toFixed(2)??"—", unit:"m³/T avg",     color:C.water   },
    { label:"Avg Renewable %",      value:rp[rp.length-1]?.toFixed(1)??"—", unit:"of electricity",color:C.renew  },
  ];
});

// ── Charts
const co2Chart=ref(null), co2KpiChart=ref(null), energyChart=ref(null), waterChart=ref(null);
const renewChart=ref(null), yoyChart=ref(null);
const charts = {};

function destroyAll() { Object.values(charts).forEach(c=>{ try{c.destroy()}catch(_){} }); }

const OPT = () => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:10}, padding:7 } }, tooltip:TOOLTIP },
  scales:AXIS, interaction:{ mode:"index", intersect:false }
});

function mkChart(key, el, type, datasets, extra={}) {
  if (!el.value) return;
  if (charts[key]) { try{charts[key].destroy()}catch(_){} }
  charts[key] = new Chart(el.value, { type, data:{ labels:rangeLabels.value, datasets }, options:{ ...OPT(), ...extra } });
}

async function buildCharts() {
  await nextTick();
  const showCo = highlightCompany.value;
  const coLabel = shortName.value;

  // CO2 total
  const ds1 = [{ label:"Sector CO₂ (M T)", data:secCo2Total.value.map(v=>v!=null?v:null), backgroundColor:C.co2+"50", borderColor:C.co2, type:"bar", borderWidth:0, borderRadius:2 }];
  if (showCo && coCo2KPI.value.some(v=>v!=null))
    ds1.push({ label:coLabel+" CO₂ KPI", data:coCo2KPI.value, borderColor:"#8B0000", backgroundColor:"transparent", type:"line", tension:0.4, pointRadius:5, borderWidth:2.5, yAxisID:"y2" });
  mkChart("co2", co2Chart, "bar", ds1, { scales:{ ...AXIS, y2:{ type:"linear", position:"right", grid:{display:false}, ticks:{ color:"#94A3B8", font:{size:10} } } } });

  // CO2 KPI trend
  const ds2 = [{ label:"Sector Median", data:secCo2KPI.value, borderColor:"#94A3B8", backgroundColor:"rgba(148,163,184,.08)", fill:true, tension:0.4, pointRadius:2, borderWidth:1.5, borderDash:[4,3] }];
  if (showCo && coCo2KPI.value.some(v=>v!=null))
    ds2.push({ label:coLabel, data:coCo2KPI.value, borderColor:"#8B0000", backgroundColor:"transparent", tension:0.4, pointRadius:6, pointStyle:"diamond", borderWidth:2.5 });
  mkChart("co2kpi", co2KpiChart, "line", ds2);

  // Energy + renew
  const ds3 = [{ label:"Sector Energy KPI (GJ/T)", data:secEnergyKPI.value, backgroundColor:C.energy+"70", borderColor:C.energy, type:"bar", borderWidth:0, borderRadius:2 }];
  if (showCo && coEnergyKPI.value.some(v=>v!=null))
    ds3.push({ label:coLabel, data:coEnergyKPI.value, borderColor:"#5C2700", backgroundColor:"transparent", type:"line", tension:0.4, pointRadius:5, borderWidth:2.5 });
  ds3.push({ label:"Renew. %", data:secRenewPct.value, borderColor:C.renew, backgroundColor:"transparent", type:"line", tension:0.4, pointRadius:2, borderWidth:1.5, borderDash:[4,3], yAxisID:"y2" });
  mkChart("energy", energyChart, "bar", ds3, { scales:{ ...AXIS, y2:{ type:"linear", position:"right", grid:{display:false}, ticks:{color:"#94A3B8",font:{size:10},callback:v=>v+"%"} } } });

  // Water
  const ds4 = [{ label:"Sector avg", data:secWaterKPI.value, borderColor:C.water, backgroundColor:"rgba(8,145,178,.10)", fill:true, tension:0.4, pointRadius:2, borderWidth:1.5, borderDash:[4,3] }];
  if (showCo && coWaterKPI.value.some(v=>v!=null))
    ds4.push({ label:coLabel, data:coWaterKPI.value, borderColor:"#0C4A6E", backgroundColor:"transparent", tension:0.4, pointRadius:5, pointStyle:"rect", borderWidth:2.5 });
  mkChart("water", waterChart, "line", ds4);

  // Renew trend
  const ds5 = [{ label:"Sector IQR", data:secRenewPct.value, backgroundColor:C.renew+"15", borderColor:"transparent", fill:true, tension:0.4, pointRadius:0, borderWidth:0 },
    { label:"Sector Median", data:secRenewPct.value, borderColor:C.renew+"60", backgroundColor:"transparent", tension:0.4, pointRadius:2, borderWidth:1.5, borderDash:[4,3] }];
  if (showCo && coRenewPct.value.some(v=>v!=null))
    ds5.push({ label:coLabel, data:coRenewPct.value, borderColor:C.renew, backgroundColor:"transparent", tension:0.4, pointRadius:5, borderWidth:2.5 });
  mkChart("renew", renewChart, "line", ds5, { scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });

  // YoY CO2 change
  const co2kpiArr = coCo2KPI.value;
  const yoyVals = rangeYears.value.map((y,i) => {
    if (i===0 || co2kpiArr[i]==null || co2kpiArr[i-1]==null || co2kpiArr[i-1]===0) return null;
    return +((co2kpiArr[i]-co2kpiArr[i-1])/Math.abs(co2kpiArr[i-1])*100).toFixed(2);
  });
  mkChart("yoy", yoyChart, "bar", [{ label:"YoY Change %", data:yoyVals, backgroundColor:yoyVals.map(v=>v!=null?v<0?C.renew+"CC":C.red+"CC":"transparent"), borderWidth:0, borderRadius:3 }],
    { scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}, grid:{color:AXIS.y.grid.color}}} });
}

async function loadData() {
  try {
    const params = { year_from:2009, year_to:2023, company_id:auth.companyName };
    const data = await api.getAnalytics(params);
    sectorData.value = data;
    // Parse company series from analytics response
    const rawSeries = data?.series || {};
    const coSeriesMap = {};
    const sYears = data?.years || [];
    // analytics series are [{year,value}] format
    for (const yr of sYears) {
      coSeriesMap[yr] = {
        co2_kpi:    rawSeries.co2_kpi?.find?.(r=>r.year===yr)?.value ?? null,
        energy_kpi: rawSeries.energy_kpi?.find?.(r=>r.year===yr)?.value ?? null,
        water_kpi:  rawSeries.water_kpi?.find?.(r=>r.year===yr)?.value ?? null,
        renew_pct:  rawSeries.renewable_share_pct?.find?.(r=>r.year===yr)?.value ?? null,
        scope1:     rawSeries.scope1_co2_t?.find?.(r=>r.year===yr)?.value ?? null,
        scope2:     rawSeries.scope2_co2_t?.find?.(r=>r.year===yr)?.value ?? null,
        total_co2:  rawSeries.total_co2_t?.find?.(r=>r.year===yr)?.value ?? null,
      };
    }
    coSeries.value = coSeriesMap;
    await buildCharts();
  } catch(e) {
    console.error("Dashboard:", e);
    await buildCharts();
  }
}

onMounted(loadData);
onUnmounted(destroyAll);
watch([yearFrom, yearTo, highlightCompany], buildCharts);
</script>