<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 mb-1">Analysis & Trends</h2>
    <p class="text-sm text-gray-400 mb-4">Sector aggregated · All TIP members · {{ dataSource }}</p>

    <!-- DSS+: company overlay selector -->
    <div v-if="auth.isDSS" class="flex gap-3 mb-4 items-center flex-wrap">
      <select v-model="overlayCompany" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white min-w-52">
        <option value="">All Companies (sector avg)</option>
        <option v-for="co in companies" :key="co" :value="co">{{ co }}</option>
      </select>
      <select v-if="overlayCompany" v-model="overlayYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
        <option v-for="y in companyYears" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>
    <div v-else class="mb-4 bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 text-sm text-blue-700">
      📊 Showing TIP sector aggregates. Pathway-level analysis with company breakdowns is available to dss+ analysts only.
    </div>

    <!-- Headline 5 KPIs -->
    <div class="grid grid-cols-5 gap-3 mb-4">
      <div v-for="kpi in headlineKPIs" :key="kpi.label"
        class="bg-white border border-gray-100 rounded-xl p-3 hover:shadow-sm transition-shadow">
        <div class="text-[10.5px] text-gray-500 mb-1">{{ kpi.label }}</div>
        <div class="text-xl font-semibold text-navy leading-tight">{{ kpi.value }}</div>
        <div class="text-[10px] text-gray-400">{{ kpi.unit }}</div>
        <div v-html="kpi.delta" class="mt-1"></div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-0 overflow-x-auto">
      <button v-for="tab in visibleTabs" :key="tab.id" @click="setTab(tab.id)"
        class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap"
        :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- General tab -->
    <div v-show="activeTab==='general'" class="mt-4 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Total energy consumption (M GJ)"><canvas ref="genEnergy" style="height:220px"></canvas></ChartBox>
        <ChartBox title="CO₂ emissions — Scope 1 vs Scope 2 (M T.CO₂)"><canvas ref="genScope" style="height:220px"></canvas></ChartBox>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Fuel mix evolution (%)"><canvas ref="genFuel" style="height:220px"></canvas></ChartBox>
        <ChartBox title="Water withdrawals (M m³)"><canvas ref="genWater" style="height:220px"></canvas></ChartBox>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <ChartBox title="Renewable electricity share (%)"><canvas ref="genRenew" style="height:200px"></canvas></ChartBox>
        <ChartBox title="Waste recovery rate (%)"><canvas ref="genWaste" style="height:200px"></canvas></ChartBox>
        <ChartBox title="ISO 14001 certification (%)"><canvas ref="genISO" style="height:200px"></canvas></ChartBox>
      </div>
      <!-- Client vs sector comparison -->
      <template v-if="!auth.isDSS && clientCo2kpi.some(v=>v!=null)">
        <div class="my-2 border-t border-gray-100 pt-3 text-sm font-semibold text-gray-600">
          {{ auth.companyName }} — your performance vs TIP sector average
        </div>
        <div class="grid grid-cols-2 gap-3">
          <ChartBox title="Energy intensity — your company vs sector (GJ/T)"><canvas ref="clientEnergy" style="height:200px"></canvas></ChartBox>
          <ChartBox title="CO₂ intensity — your company vs sector (T.CO₂/T)"><canvas ref="clientCO2" style="height:200px"></canvas></ChartBox>
        </div>
      </template>
    </div>

    <!-- P1&2 tab -->
    <div v-show="activeTab==='p12'" class="mt-4 space-y-4">
      <div class="text-sm font-semibold text-gray-600 mb-2">Pathway 1 — Energy consumption & intensity</div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Sector total energy (M GJ)"><canvas ref="p12Energy" style="height:240px"></canvas></ChartBox>
        <ChartBox title="Energy intensity — GJ/metric ton"><canvas ref="p12EnergyKPI" style="height:240px"></canvas></ChartBox>
      </div>
      <div class="border-t border-gray-100 pt-4 text-sm font-semibold text-gray-600 mb-2">Pathway 2 — CO₂ emissions & intensity</div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="CO₂ Scope 1 & 2 stacked (M T.CO₂)"><canvas ref="p12CO2" style="height:240px"></canvas></ChartBox>
        <ChartBox title="CO₂ intensity — T.CO₂/metric ton"><canvas ref="p12CO2KPI" style="height:240px"></canvas></ChartBox>
      </div>
    </div>

    <!-- P3 tab -->
    <div v-show="activeTab==='p3'" class="mt-4 space-y-4">
      <div class="text-sm font-semibold text-gray-600 mb-2">Pathway 3 — Water withdrawals & intensity</div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Sector water withdrawals (M m³)"><canvas ref="p3Water" style="height:260px"></canvas></ChartBox>
        <ChartBox title="Water intensity — m³/metric ton"><canvas ref="p3WaterKPI" style="height:260px"></canvas></ChartBox>
      </div>
    </div>

    <!-- P4 tab -->
    <div v-show="activeTab==='p4'" class="mt-4 space-y-4">
      <div class="text-sm font-semibold text-gray-600 mb-2">Pathway 4 — Waste management & environmental certification</div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Waste — recovery vs elimination (metric T)"><canvas ref="p4Waste" style="height:260px"></canvas></ChartBox>
        <ChartBox title="Waste recovery rate — sector average (%)"><canvas ref="p4WasteRecov" style="height:260px"></canvas></ChartBox>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, h, defineComponent } from "vue";
import { Chart } from "chart.js";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, TOOLTIP, ANIMATION, AXIS, YEARS, YEAR_LABELS, FALLBACK, mergeSeries } from "@/composables/useCharts.js";

const auth = useAuthStore();
const activeTab = ref("general");
const overlayCompany = ref("");
const overlayYear = ref(2023);
const companies = ref([]);
const companyYears = ref([]);
const sectorData = ref(null);
const coSeries = ref({});   // { year: kpiObj }
const loading = ref(false);

const dataSource = computed(() => sectorData.value ? "live consolidated data" : "built-in demo data");

const allTabs = [
  { id:"general", label:"General", dssOnly:false },
  { id:"p12",     label:"Pathway 1 & 2 — Energy & CO₂", dssOnly:true },
  { id:"p3",      label:"Pathway 3 — Water", dssOnly:true },
  { id:"p4",      label:"Pathway 4 — Waste & Environment", dssOnly:true },
];
const visibleTabs = computed(() => allTabs.filter(t => !t.dssOnly || auth.isDSS));
function setTab(id) { activeTab.value = id; }

// ── sector series helpers
const ys = YEARS;
const labels = YEAR_LABELS;

function get(key, div=1) {
  const s = sectorData.value?.series;
  if (!s?.[key]) return FALLBACK[key] || Array(ys.length).fill(null);
  return s[key].map(v => v!=null ? v/div : null);
}

const energy     = computed(() => get("total_energy", 1e6));
const scope1     = computed(() => get("scope1", 1e6));
const scope2     = computed(() => get("scope2", 1e6));
const water      = computed(() => get("water", 1e6));
const energy_kpi = computed(() => get("energy_kpi"));
const co2_kpi    = computed(() => get("co2_kpi"));
const water_kpi  = computed(() => get("water_kpi"));
const renew_pct  = computed(() => get("renew_pct"));
const waste_recov= computed(() => get("waste_recov"));
const iso_cert   = computed(() => get("iso_cert"));
const fuelMix    = computed(() => sectorData.value?.fuel_mix || FALLBACK.fuel_mix);
const production = computed(() => get("production", 1e6));

// client-specific series
const clientCo2kpi    = computed(() => ys.map(y => coSeries.value[y]?.co2_kpi    ?? null));
const clientEnergyKpi = computed(() => ys.map(y => coSeries.value[y]?.energy_kpi ?? null));

// headline KPI strip
const headlineKPIs = computed(() => {
  const delta = (cur, prev, down=true) => {
    if (!cur||!prev||prev===0) return "";
    const pct = ((cur-prev)/Math.abs(prev)*100).toFixed(1);
    const good = (pct<0)===down;
    const col = good ? "#16A34A" : "#DC2626";
    const arr = pct<0?"▼":"▲";
    return `<span style="color:${col};font-size:10px">${arr} ${Math.abs(pct)}%</span>`;
  };
  const e=energy.value; const c=scope1.value.map((v,i)=>(v||0)+(scope2.value[i]||0));
  const r=renew_pct.value; const wr=waste_recov.value; const ck=co2_kpi.value;
  return [
    { label:"Total Energy (latest)", value:e[e.length-1]!=null?e[e.length-1].toFixed(1)+"M":"—", unit:"GJ", delta:delta(e[e.length-1],e[e.length-2]) },
    { label:"Total CO₂ (latest)",    value:c[c.length-1]!=null?c[c.length-1].toFixed(2)+"M":"—", unit:"T.CO₂", delta:delta(c[c.length-1],c[c.length-2]) },
    { label:"CO₂ Intensity",         value:ck[ck.length-1]!=null?ck[ck.length-1].toFixed(3):"—", unit:"T.CO₂/T", delta:delta(ck[ck.length-1],ck[ck.length-2]) },
    { label:"Renewable Electricity", value:r[r.length-1]!=null?r[r.length-1].toFixed(1)+"%":"—",  unit:"of elec.", delta:delta(r[r.length-1],r[r.length-2],false) },
    { label:"Waste Recovery",        value:wr[wr.length-1]!=null?wr[wr.length-1].toFixed(1)+"%":"—", unit:"of waste", delta:delta(wr[wr.length-1],wr[wr.length-2],false) },
  ];
});

// ── Chart refs
const genEnergy=ref(null), genScope=ref(null), genFuel=ref(null), genWater=ref(null);
const genRenew=ref(null),  genWaste=ref(null), genISO=ref(null);
const clientEnergy=ref(null), clientCO2=ref(null);
const p12Energy=ref(null), p12EnergyKPI=ref(null), p12CO2=ref(null), p12CO2KPI=ref(null);
const p3Water=ref(null), p3WaterKPI=ref(null);
const p4Waste=ref(null), p4WasteRecov=ref(null);

const chartInstances = {};
function destroyAll() { Object.values(chartInstances).forEach(c=>{ try{c.destroy()}catch(_){} }); }

function make(key, ref, type, datasets, extraOpts={}) {
  if (!ref.value) return;
  if (chartInstances[key]) { try{chartInstances[key].destroy()}catch(_){} }
  chartInstances[key] = new Chart(ref.value, {
    type, data:{ labels, datasets },
    options:{ responsive:true, maintainAspectRatio:false, animation:ANIMATION,
      plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:10}, padding:7 } }, tooltip:TOOLTIP },
      scales:AXIS, interaction:{ mode:"index", intersect:false }, ...extraOpts }
  });
}

function line(label, data, color, fill=false, dash=[]) {
  return { label, data, borderColor:color, backgroundColor:fill?color+"15":"transparent",
    fill, tension:0.4, pointRadius:3, borderWidth:2, borderDash:dash,
    borderDashOffset:0, segment:dash.length?{borderDash:()=>dash}:{} };
}
function bar(label, data, color) {
  return { label, data, backgroundColor:color, borderWidth:0, borderRadius:2 };
}
function stackedBar(label, data, color) {
  return { ...bar(label,data,color), stack:"s" };
}

async function buildAllCharts() {
  await nextTick();
  const e=energy.value, s1=scope1.value, s2=scope2.value, w=water.value;
  const ek=energy_kpi.value, ck=co2_kpi.value, wk=water_kpi.value;
  const rp=renew_pct.value, wr=waste_recov.value, iso=iso_cert.value;
  const fm=fuelMix.value;
  const fuelColors={"Natural Gas":C.energy,"Electricity":"#3B82F6","Fuel Oil":"#EF4444","LPG":"#8B5CF6","Coal":"#6B7280","Other":"#D1D5DB"};

  // General
  make("genEnergy", genEnergy, "line", [{ ...line("Energy (M GJ)",e,C.renew,true), pointRadius:2 }]);
  make("genScope",  genScope,  "line", [line("Scope 1",s1,C.co2,true), line("Scope 2",s2,"#1D4ED8",true)]);
  make("genFuel",   genFuel,   "bar",
    Object.entries(fm).map(([n,d])=>stackedBar(n,d,fuelColors[n]||"#999")),
    { scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}} } });
  make("genWater",  genWater,  "bar", [bar("Water (M m³)",w,C.water+"90")]);
  make("genRenew",  genRenew,  "bar", [bar("Renew. %",rp,C.renew)],
    { scales:{...AXIS, y:{...AXIS.y, ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
  make("genWaste",  genWaste,  "bar",
    [stackedBar("Recovery",wr.map(v=>v),C.renew), stackedBar("Elimination",wr.map(v=>v!=null?100-v:null),"#EF444440")],
    { scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}} } });
  make("genISO",    genISO,    "bar", [bar("ISO 14001 %",iso,"#0A224090")],
    { scales:{...AXIS, y:{...AXIS.y, ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });

  // Client vs sector (only when data exists)
  const hasClient = clientEnergyKpi.value.some(v=>v!=null);
  if (!auth.isDSS && hasClient) {
    make("clientEnergy", clientEnergy, "line", [
      line("Sector avg", ek, "#94A3B8", false, [4,3]),
      { ...line(auth.companyName?.split(" ")[0]||"You", clientEnergyKpi.value, C.navy), pointRadius:4 }
    ]);
    make("clientCO2", clientCO2, "line", [
      line("Sector avg", ck, "#94A3B8", false, [4,3]),
      { ...line(auth.companyName?.split(" ")[0]||"You", clientCo2kpi.value, C.red), pointRadius:4 }
    ]);
  }

  // P1+2
  make("p12Energy",    p12Energy,    "line", [{ ...line("Total energy (M GJ)",e,C.renew,true), pointRadius:2 }]);
  make("p12EnergyKPI", p12EnergyKPI, "line", [line("Energy KPI (GJ/T)",ek,C.purple)]);
  make("p12CO2",       p12CO2,       "line", [
    { label:"Scope 1", data:s1, borderColor:C.red, backgroundColor:"rgba(200,16,46,.15)", fill:true, tension:0.4, pointRadius:2, borderWidth:2 },
    { label:"Scope 2", data:s2.map((v,i)=>(v||0)+(s1[i]||0)), borderColor:"#1D4ED8", backgroundColor:"rgba(29,78,216,.12)", fill:true, tension:0.4, pointRadius:2, borderWidth:2 },
  ]);
  make("p12CO2KPI",    p12CO2KPI,    "line", [line("CO₂ KPI (T/T)",ck,C.red)]);

  // P3
  make("p3Water",    p3Water,    "line", [{ ...line("Water (M m³)",w,C.teal,true), pointRadius:2 }]);
  make("p3WaterKPI", p3WaterKPI, "line", [line("Water KPI (m³/T)",wk,C.teal)]);

  // P4
  const totalWaste = production.value.map(v=>v?v*85000:null);
  const recovered  = production.value.map((v,i)=>v&&wr[i]?v*85000*wr[i]/100:null);
  make("p4Waste", p4Waste, "bar", [
    stackedBar("Recovered",recovered,C.renew), stackedBar("Eliminated",totalWaste.map((v,i)=>v&&recovered[i]?v-recovered[i]:null),"#EF444440")
  ], { scales:{ x:{...AXIS.x,stacked:true}, y:{...AXIS.y,stacked:true} } });
  make("p4WasteRecov", p4WasteRecov, "line", [{ ...line("Recovery %",wr,C.waste,true), pointRadius:2 }],
    { scales:{...AXIS, y:{...AXIS.y, ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
}

async function loadData() {
  loading.value = true;
  try {
    const params = overlayCompany.value
      ? { year_from:2009, year_to:2023, company_id:overlayCompany.value }
      : { year_from:2009, year_to:2023 };
    const data = await api.getAnalytics(params);
    sectorData.value = data;

    // Company series for client view
    if (!auth.isDSS) {
      const cd = await api.getAnalytics({ year_from:2009, year_to:2023, company_id:auth.companyName });
      coSeries.value = cd?.company_series || {};
    }

    await buildAllCharts();
  } catch(e) {
    console.error("Analysis load:", e);
    await buildAllCharts();
  }
  loading.value = false;
}

async function loadCompanies() {
  try {
    const res = await api.getCompanies();
    companies.value = Array.isArray(res) ? res : (res?.companies || []);
  } catch(_) {}
}

watch(overlayCompany, async (co) => {
  if (co) {
    try {
      const cd = await api.getCompanyData(co);
      companyYears.value = (cd?.years || []).slice().sort((a,b)=>b-a);
      overlayYear.value = companyYears.value[0] || 2023;
    } catch(_) {}
  }
  await loadData();
});

onMounted(async () => { if (auth.isDSS) await loadCompanies(); await loadData(); });
onUnmounted(destroyAll);

// ChartBox sub-component
const ChartBox = defineComponent({
  props: { title:String, subtitle:String },
  setup(props, { slots }) {
    return () => h("div", { class:"bg-white border border-gray-100 rounded-xl overflow-hidden" }, [
      h("div", { class:"px-4 pt-3 pb-1.5 border-b border-gray-50" }, [
        h("div", { class:"text-[12.5px] font-semibold text-gray-700" }, props.title),
        props.subtitle ? h("div", { class:"text-[10px] text-gray-400" }, props.subtitle) : null,
      ]),
      h("div", { class:"p-3" }, slots.default?.()),
    ]);
  },
});
</script>