<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 mb-1">Benchmarking</h2>
    <p class="text-sm text-gray-400 mb-4">Industry peer comparison · TIP sector quartiles</p>

    <!-- Selectors -->
    <div class="flex gap-3 mb-4 flex-wrap items-center">
      <select v-if="auth.isDss" v-model="company" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white min-w-48">
        <option v-for="c in companies" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="selYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
        <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
      </select>
      <span v-if="loading" class="text-xs text-gray-400">Loading…</span>
    </div>

    <!-- 5 KPI position chips -->
    <div class="grid grid-cols-5 gap-3 mb-4">
      <div v-for="(b, i) in bands" :key="b.key"
        class="bg-white border border-gray-100 rounded-xl p-3 hover:shadow-sm transition-shadow">
        <div class="text-[9.5px] font-semibold text-gray-400 uppercase tracking-wide mb-1">{{ b.name }}</div>
        <div class="text-2xl font-bold leading-tight" :style="{color:b.color}">{{ b.displayVal }}</div>
        <div class="text-[9px] text-gray-400 mb-2">{{ b.unit }}</div>
        <div class="bg-gray-100 rounded h-1.5 overflow-hidden mb-1">
          <div class="h-full rounded transition-all duration-1000" :style="{width:b.posPct+'%', background:b.rankColor}"></div>
        </div>
        <div class="flex justify-between text-[9px]">
          <span class="text-gray-400">{{ b.lowerBetter ? "Worst" : "Low" }}</span>
          <span class="font-semibold" :style="{color:b.rankColor}">{{ b.rankLabel }}</span>
          <span class="text-gray-400">{{ b.lowerBetter ? "Best" : "High" }}</span>
        </div>
      </div>
    </div>

    <!-- 6 KPI tabs -->
    <div class="flex border-b border-gray-200 overflow-x-auto mb-0">
      <button v-for="tab in tabs" :key="tab.id" @click="setTab(tab.id)"
        class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap"
        :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- General -->
    <div v-show="activeTab==='general'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">ESG Performance Radar</div>
        <div class="p-4" style="height:300px"><canvas ref="radarChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Sector Percentile Position (100=best)</div>
        <div class="p-4" style="height:220px"><canvas ref="posChart"></canvas></div>
        <div v-if="improvData.length" class="px-4 pb-4">
          <div class="text-xs font-semibold text-gray-500 mb-2">Improvement since base year</div>
          <table class="w-full text-xs">
            <tbody>
              <tr v-for="r in improvData" :key="r.kpi" class="border-t border-gray-50">
                <td class="py-1 text-gray-600">{{ r.kpi }}</td>
                <td class="py-1 text-right font-semibold" :class="r.good?'text-green-600':'text-red-500'">{{ r.val }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- CO2 -->
    <div v-show="activeTab==='co2'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">CO₂ Intensity Trend vs Sector (T.CO₂/T)</div>
        <div class="p-4" style="height:260px"><canvas ref="co2TrendChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Scope 1 vs Scope 2 (T.CO₂)</div>
        <div class="p-4" style="height:260px"><canvas ref="scopeChart"></canvas></div>
      </div>
    </div>

    <!-- Energy -->
    <div v-show="activeTab==='energy'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Energy Intensity Trend vs Sector (GJ/T)</div>
        <div class="p-4" style="height:260px"><canvas ref="energyTrendChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Energy Mix by Source (GJ)</div>
        <div class="p-4" style="height:260px"><canvas ref="fuelChart"></canvas></div>
      </div>
    </div>

    <!-- Electricity -->
    <div v-show="activeTab==='elec'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Electricity Mix (%)</div>
        <div class="p-4" style="height:260px"><canvas ref="elecMixChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Renewable Electricity Share vs Sector (%)</div>
        <div class="p-4" style="height:260px"><canvas ref="renewTrendChart"></canvas></div>
      </div>
    </div>

    <!-- Water -->
    <div v-show="activeTab==='water'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Water Intensity Trend vs Sector (m³/T)</div>
        <div class="p-4" style="height:260px"><canvas ref="waterTrendChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Water Withdrawals & Intensity</div>
        <div class="p-4" style="height:260px"><canvas ref="waterComboChart"></canvas></div>
      </div>
    </div>

    <!-- Waste -->
    <div v-show="activeTab==='waste'" class="mt-4 grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Waste Recovery Rate vs Sector (%)</div>
        <div class="p-4" style="height:260px"><canvas ref="wasteRecovChart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-50 text-sm font-semibold">Total Waste vs Recovered (T)</div>
        <div class="p-4" style="height:260px"><canvas ref="wasteVolChart"></canvas></div>
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
const company = ref(auth.isDss ? "" : auth.companyName);
const selYear = ref(2023);
const companies = ref([]);
const availableYears = ref([]);
const loading = ref(false);
const activeTab = ref("general");

// API data
const benchData   = ref(null);
const companyData = ref(null);  // { years:[], summary:[] } all years
const coTrend     = ref({});    // { year: kpis }
const sectorData  = ref(null);  // analytics

const tabs = [
  { id:"general", label:"General" },
  { id:"co2",     label:"CO₂" },
  { id:"energy",  label:"Energy" },
  { id:"elec",    label:"Electricity" },
  { id:"water",   label:"Water" },
  { id:"waste",   label:"Waste" },
];
function setTab(id) { activeTab.value = id; }

// ── Static quartile bands from benchData + company KPIs
const bands = computed(() => {
  const bd = benchData.value?.bands || {};
  const cd = companyData.value;
  // get year-specific kpis
  const yr = selYear.value;
  const kpis = coTrend.value[yr] || benchData.value?.my_kpis || null;

  const defs = [
    { key:"co2_kpi",    name:"CO₂ Intensity",  unit:"T.CO₂/T", lowerBetter:true,  color:C.co2,    val:kpis?.co2_kpi },
    { key:"energy_kpi", name:"Energy Intensity",unit:"GJ/T",    lowerBetter:true,  color:C.energy, val:kpis?.energy_kpi },
    { key:"water_kpi",  name:"Water Intensity", unit:"m³/T",    lowerBetter:true,  color:C.water,  val:kpis?.water_kpi },
    { key:"renew_pct",  name:"Renewable Elec.", unit:"%",       lowerBetter:false, color:C.renew,  val:kpis?.renewable_share_pct },
    { key:"waste_pct",  name:"Waste Recovery",  unit:"%",       lowerBetter:false, color:C.waste,  val:kpis?.waste_recovery_pct },
  ];

  return defs.map(d => {
    const b = bd[d.key] || { q10:0, q25:0, median:0, q75:0, q90:1 };
    const lo=b.q10, hi=b.q90, span=Math.max(hi-lo, 0.001);
    const v = d.val ?? 0;
    let posPct = ((v-lo)/span*100);
    if (d.lowerBetter) posPct = 100 - posPct;
    posPct = Math.max(0, Math.min(100, posPct));
    const rankColor = posPct>=70?"#16A34A":posPct>=40?"#F59E0B":"#DC2626";
    const rankLabel = posPct>=75?"Top quartile":posPct>=50?"Above median":posPct>=25?"Below median":"Bottom quartile";
    return { ...d, b, posPct, rankColor, rankLabel,
      displayVal: d.val!=null ? (d.lowerBetter ? d.val.toFixed(3) : d.val.toFixed(1)) : "—" };
  });
});

const improvData = computed(() => {
  const ys = Object.keys(coTrend.value).map(Number).sort((a,b)=>a-b);
  if (ys.length < 2) return [];
  const base = coTrend.value[ys[0]]; const end = coTrend.value[ys[ys.length-1]];
  if (!base || !end) return [];
  const pct = (cur, prev, down=true) => {
    if (!prev||prev===0) return null;
    const p = ((cur-prev)/Math.abs(prev)*100).toFixed(1);
    return { val:`${p>0?"+":""}${p}%`, good:(p<0)===down };
  };
  return [
    { kpi:"CO₂ Intensity",    ...pct(end.co2_kpi, base.co2_kpi)        },
    { kpi:"Energy Intensity", ...pct(end.energy_kpi, base.energy_kpi)  },
    { kpi:"Water Intensity",  ...pct(end.water_kpi, base.water_kpi)    },
    { kpi:"Renewable Elec.",  ...pct(end.renewable_share_pct, base.renewable_share_pct, false) },
    { kpi:"Waste Recovery",   ...pct(end.waste_pct??end.waste_recovery_pct, base.waste_pct??base.waste_recovery_pct, false) },
  ].filter(r=>r.val);
});

// ── Charts
const radarChart=ref(null), posChart=ref(null);
const co2TrendChart=ref(null), scopeChart=ref(null);
const energyTrendChart=ref(null), fuelChart=ref(null);
const elecMixChart=ref(null), renewTrendChart=ref(null);
const waterTrendChart=ref(null), waterComboChart=ref(null);
const wasteRecovChart=ref(null), wasteVolChart=ref(null);

const chartInstances = {};
function destroyAll() { Object.values(chartInstances).forEach(c=>{ try{c.destroy()}catch(_){} }); }

const OPT = (extra={}) => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:10}, padding:7 } }, tooltip:TOOLTIP },
  scales:AXIS, interaction:{ mode:"index", intersect:false }, ...extra
});

function mk(key, el, type, datasets, extra={}) {
  if (!el.value) return;
  if (chartInstances[key]) { try{chartInstances[key].destroy()}catch(_){} }
  chartInstances[key] = new Chart(el.value, { type, data:{ labels:YEAR_LABELS, datasets }, options:{ ...OPT(), ...extra } });
}

function secSeries(key, div=1) {
  const raw = sectorData.value?.series?.[key];
  if (!raw || !raw.length) return FALLBACK[key] || Array(YEARS.length).fill(null);
  // analytics returns [{year, value}] - map to YEARS array
  if (typeof raw[0] === "object" && "year" in raw[0]) {
    return YEARS.map(y => {
      const item = raw.find(r => r.year === y);
      return item?.value != null ? item.value / div : null;
    });
  }
  return raw.map(v => v != null ? v / div : null);
}

function coLine(key, div=1) {
  return YEARS.map(y => { const d=coTrend.value[y]; return d?.[key]!=null?d[key]/div:null; });
}

async function buildCharts() {
  await nextTick();
  const co = company.value || auth.companyName;
  const coName = co?.split(" ")[0] || "You";

  // sector series
  const secCo2KPI  = secSeries("co2_kpi");
  const secEnergyKPI = secSeries("energy_kpi");
  const secWaterKPI= secSeries("water_kpi");
  const secRenewPct= secSeries("renewable_share_pct");
  const secWasteR  = secSeries("waste_recovery_pct");
  const secScope1  = secSeries("scope1_co2_t", 1e6);
  const secScope2  = secSeries("scope2_co2_t", 1e6);
  const fm = FALLBACK.fuel_mix;

  // company trend series
  const coCo2KPI    = coLine("co2_kpi");
  const coEnergyKPI = coLine("energy_kpi");
  const coWaterKPI  = coLine("water_kpi");
  const coRenewPct  = coLine("renew_share_pct");
  const coWasteR    = YEARS.map(y=>{ const d=coTrend.value[y]; return d?.waste_pct!=null?d.waste_pct:(d?.waste_recovery_pct!=null?d.waste_recovery_pct:null); });
  const coScope1    = coLine("total_co2_scope1", 1);
  const coScope2    = coLine("total_co2_scope2", 1);
  const coWaterM3   = coLine("water_kpi");
  const coWasteTotal= YEARS.map(y=>coTrend.value[y]?.waste_total??null);
  const coWasteRec  = YEARS.map(y=>coTrend.value[y]?.waste_recovery??null);
  const coRenewGJ   = YEARS.map(y=>coTrend.value[y]?.renew_elec??null);
  const coNonRenewGJ= YEARS.map(y=>coTrend.value[y]?.nonrenew_elec??null);

  // IQR band helper
  const iqrDatasets = (q25arr, q75arr, color) => [
    { data:q75arr, fill:false, borderWidth:0, pointRadius:0, label:undefined, showInLegend:false },
    { data:q25arr, fill:"-1", backgroundColor:color+"15", borderWidth:0, pointRadius:0, label:"Sector IQR", borderColor:"transparent" },
  ];

  // Radar
  if (radarChart.value) {
    const scores = bands.value.map(b=>b.posPct);
    const secScores = bands.value.map(b=>{
      const bnd=benchData.value?.bands?.[b.key]; if(!bnd) return 50;
      const span=Math.max(bnd.q90-bnd.q10,0.001);
      const raw=(bnd.median-bnd.q10)/span*100;
      return b.lowerBetter ? 100-raw : raw;
    });
    const bLabels = bands.value.map(b=>b.name);
    const r = (arr) => [...arr, arr[0]];
    const ang = bLabels.map((_,i)=>2*Math.PI*i/bLabels.length - Math.PI/2);
    const toXY = (scores) => scores.map((s,i)=>({ x: Math.cos(ang[i])*s, y: Math.sin(ang[i])*s }));

    if (chartInstances.radar) { try{chartInstances.radar.destroy()}catch(_){} }
    chartInstances.radar = new Chart(radarChart.value, {
      type:"radar",
      data:{ labels:bLabels, datasets:[
        { label:coName, data:r(scores), borderColor:C.renew, backgroundColor:"rgba(22,163,74,.15)", pointRadius:5, borderWidth:2.5 },
        { label:"Sector Median", data:r(secScores), borderColor:"#94A3B8", backgroundColor:"rgba(148,163,184,.08)", pointRadius:3, borderWidth:1.5, borderDash:[4,3] },
      ]},
      options:{ responsive:true, maintainAspectRatio:false, animation:ANIMATION,
        plugins:{ legend:{ display:true, position:"bottom", labels:{ color:"#64748B", boxWidth:9, font:{size:10} } }, tooltip:TOOLTIP },
        scales:{ r:{ min:0, max:100, ticks:{ backdropColor:"transparent", color:"#9CA3AF", font:{size:9}, stepSize:25 }, grid:{ color:"rgba(0,0,0,.06)" }, pointLabels:{ color:"#374151", font:{size:11} } } } }
    });
  }

  // Position bar (horizontal)
  if (posChart.value) {
    if (chartInstances.pos) { try{chartInstances.pos.destroy()}catch(_){} }
    chartInstances.pos = new Chart(posChart.value, {
      type:"bar",
      data:{ labels:bands.value.map(b=>b.name), datasets:[{ data:bands.value.map(b=>b.posPct), backgroundColor:bands.value.map(b=>b.color), borderRadius:4, borderWidth:0 }] },
      options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false, animation:ANIMATION,
        plugins:{ legend:{display:false}, tooltip:TOOLTIP },
        scales:{ x:{ min:0, max:100, grid:{color:AXIS.y.grid.color}, ticks:{...AXIS.x.ticks,callback:v=>v+"%"} }, y:{...AXIS.y,grid:{display:false}} } }
    });
  }

  // CO2 trend vs sector
  mk("co2trend", co2TrendChart, "line", [
    ...iqrDatasets(secCo2KPI.map((_,i)=>secCo2KPI[i]*0.9), secCo2KPI.map(v=>v?v*1.1:null), C.co2),
    { label:"Sector Median", data:secCo2KPI, borderColor:"#94A3B8", borderDash:[4,3], tension:0.4, pointRadius:2, borderWidth:1.5, backgroundColor:"transparent" },
    { label:coName, data:coCo2KPI, borderColor:C.co2, tension:0.4, pointRadius:5, borderWidth:2.5, backgroundColor:"transparent" },
  ]);

  // Scope 1+2
  mk("scope", scopeChart, "line", [
    { label:"Scope 2", data:coScope2.some(v=>v!=null)?coScope2:secScope2, fill:true, backgroundColor:"rgba(71,85,105,.15)", borderColor:"#1D4ED8", tension:0.4, pointRadius:2, borderWidth:2 },
    { label:"Scope 1", data:coScope1.some(v=>v!=null)?coScope1:secScope1, fill:true, backgroundColor:"rgba(71,85,105,.4)", borderColor:C.co2, tension:0.4, pointRadius:2, borderWidth:2 },
  ]);

  // Energy trend
  mk("energytrend", energyTrendChart, "line", [
    ...iqrDatasets(secEnergyKPI.map(v=>v?v*0.9:null), secEnergyKPI.map(v=>v?v*1.1:null), C.energy),
    { label:"Sector Median", data:secEnergyKPI, borderColor:"#94A3B8", borderDash:[4,3], tension:0.4, pointRadius:2, borderWidth:1.5, backgroundColor:"transparent" },
    { label:coName, data:coEnergyKPI, borderColor:C.energy, tension:0.4, pointRadius:5, borderWidth:2.5, backgroundColor:"transparent" },
  ]);

  // Fuel mix
  const fuelColors={"Natural Gas":C.energy,"Electricity":"#3B82F6","Fuel Oil":"#EF4444","LPG":"#8B5CF6","Coal":"#6B7280","Other":"#D1D5DB"};
  mk("fuel", fuelChart, "bar",
    Object.entries(fm).map(([n,d])=>({ label:n, data:d, backgroundColor:fuelColors[n]||"#999", stack:"s", borderWidth:0 })),
    { scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true} } });

  // Electricity mix (renew vs non-renew)
  const renGJ=coRenewGJ.every(v=>v==null)?YEARS.map((_,i)=>FALLBACK.renew_pct[i]):coRenewGJ;
  const nonRenGJ=coNonRenewGJ.every(v=>v==null)?YEARS.map((_,i)=>100-FALLBACK.renew_pct[i]):coNonRenewGJ;
  const totE = renGJ.map((v,i)=>Math.max((v||0)+(nonRenGJ[i]||0),1));
  mk("elecmix", elecMixChart, "bar", [
    { label:"Renewable", data:renGJ.map((v,i)=>v!=null?v/totE[i]*100:null), backgroundColor:C.renew, stack:"s", borderWidth:0 },
    { label:"Non-Renewable", data:nonRenGJ.map((v,i)=>v!=null?v/totE[i]*100:null), backgroundColor:"#94A3B8", stack:"s", borderWidth:0 },
  ], { scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}} } });

  // Renew trend
  mk("renewtrend", renewTrendChart, "line", [
    ...iqrDatasets(secRenewPct.map(v=>v?v*0.7:null), secRenewPct.map(v=>v?v*1.3:null), C.renew),
    { label:"Sector Median", data:secRenewPct, borderColor:"#94A3B8", borderDash:[4,3], tension:0.4, pointRadius:2, borderWidth:1.5, backgroundColor:"transparent" },
    { label:coName, data:coRenewPct, borderColor:C.renew, tension:0.4, pointRadius:5, borderWidth:2.5, backgroundColor:"transparent" },
  ], { scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });

  // Water trend
  mk("watertrend", waterTrendChart, "line", [
    ...iqrDatasets(secWaterKPI.map(v=>v?v*0.85:null), secWaterKPI.map(v=>v?v*1.15:null), C.water),
    { label:"Sector Median", data:secWaterKPI, borderColor:"#94A3B8", borderDash:[4,3], tension:0.4, pointRadius:2, borderWidth:1.5, backgroundColor:"transparent" },
    { label:coName, data:coWaterKPI, borderColor:C.water, tension:0.4, pointRadius:5, borderWidth:2.5, backgroundColor:"transparent" },
  ]);

  // Water combo
  mk("watercombo", waterComboChart, "bar", [
    { label:"Withdrawals (M m³)", data:coWaterM3.every(v=>v==null)?FALLBACK.water:coWaterM3.map(v=>v?v/1e6:null), backgroundColor:C.water+"80", borderWidth:0, borderRadius:2 },
  ]);

  // Waste recovery trend
  mk("wasterecov", wasteRecovChart, "line", [
    ...iqrDatasets(secWasteR.map(v=>v?v*0.9:null), secWasteR.map(v=>v?v*1.05:null), C.waste),
    { label:"Sector Median", data:secWasteR, borderColor:"#94A3B8", borderDash:[4,3], tension:0.4, pointRadius:2, borderWidth:1.5, backgroundColor:"transparent" },
    { label:coName, data:coWasteR, borderColor:C.waste, tension:0.4, pointRadius:5, borderWidth:2.5, backgroundColor:"transparent" },
    { label:"Target 90%", data:YEARS.map(()=>90), borderColor:C.renew, borderDash:[6,3], pointRadius:0, borderWidth:1.5, backgroundColor:"transparent" },
  ], { scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });

  // Waste volumes
  mk("wasteVol", wasteVolChart, "bar", [
    { label:"Total Waste", data:coWasteTotal.every(v=>v==null)?YEARS.map(()=>335000):coWasteTotal, backgroundColor:"#E2E8F0", borderWidth:0, borderRadius:2 },
    { label:"Recovered",   data:coWasteRec.every(v=>v==null)?YEARS.map(()=>285000):coWasteRec, backgroundColor:C.waste, borderWidth:0, borderRadius:2 },
  ], { scales:{...AXIS, y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>(v/1000).toFixed(0)+"k"}}} });
}

async function loadData() {
  const co = company.value || auth.companyName;
  if (!co) return;
  loading.value = true;
  try {
    const [bench, analytics] = await Promise.all([
      api.getBenchmarks(selYear.value, co),
      api.getAnalytics({ year_from:2009, year_to:2023, company_id: auth.companyId || co.toLowerCase().replace(/ /g,'') }),
    ]);
    benchData.value  = bench;
    sectorData.value = analytics;

    // company_trend is pre-computed in get_benchmarks Python function
    if (bench?.company_trend) {
      availableYears.value = Object.keys(bench.company_trend).map(Number).sort((a,b)=>b-a);
      if (availableYears.value.length && !availableYears.value.includes(selYear.value))
        selYear.value = availableYears.value[0];
      coTrend.value = bench.company_trend;
    }
    await buildCharts();
  } catch(e) {
    console.error("Benchmarking:", e);
    await buildCharts();
  }
  loading.value = false;
}

async function loadCompanies() {
  try {
    const res = await api.getCompanies();
    companies.value = Array.isArray(res) ? res : (res?.companies || []);
    if (!company.value && companies.value.length) company.value = companies.value[0];
  } catch(_) {}
}

onMounted(async () => {
  if (auth.isDss) await loadCompanies();
  else company.value = auth.companyName;
  await loadData();
});
onUnmounted(destroyAll);
watch([company, selYear], loadData);
</script>