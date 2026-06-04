<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 mb-1">Analysis & Trends</h2>
    <p class="text-sm text-gray-400 mb-4">Sector aggregated · All TIP members · {{ dataSource }}</p>

    <!-- DSS+ company overlay -->
    <div v-if="auth.isDss" class="flex gap-3 mb-4 items-center flex-wrap">
      <select v-model="overlayCompany" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white min-w-52">
        <option value="">All Companies (sector avg)</option>
        <option v-for="co in companies" :key="co" :value="co">{{ co }}</option>
      </select>
    </div>
    <div v-else class="mb-4 bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 text-sm text-blue-700">
      📊 Showing TIP sector aggregates. Pathway-level analysis is available to dss+ analysts only.
    </div>

    <!-- Headline KPI strip -->
    <div class="grid grid-cols-5 gap-3 mb-4">
      <div v-for="kpi in headlineKPIs" :key="kpi.label" class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-[10.5px] text-gray-500 mb-1">{{ kpi.label }}</div>
        <div class="text-xl font-semibold text-navy leading-tight">{{ kpi.value }}</div>
        <div class="text-[10px] text-gray-400">{{ kpi.unit }}</div>
        <div v-html="kpi.delta" class="mt-1 text-[10px]"></div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-0 overflow-x-auto">
      <button v-for="tab in visibleTabs" :key="tab.id" @click="activeTab=tab.id"
        class="px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap"
        :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- General tab -->
    <div v-show="activeTab==='general'" class="mt-4 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Total energy consumption (M GJ)"><canvas ref="genEnergy" style="height:220px"></canvas></ChartBox>
        <ChartBox title="CO₂ Scope 1 vs Scope 2 (M T.CO₂)"><canvas ref="genScope" style="height:220px"></canvas></ChartBox>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Water withdrawals (M m³)"><canvas ref="genWater" style="height:220px"></canvas></ChartBox>
        <ChartBox title="Renewable electricity share (%)"><canvas ref="genRenew" style="height:220px"></canvas></ChartBox>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Waste recovery rate (%)"><canvas ref="genWaste" style="height:200px"></canvas></ChartBox>
        <ChartBox title="ISO 14001 certification (%)"><canvas ref="genISO" style="height:200px"></canvas></ChartBox>
      </div>
    </div>

    <!-- DSS-only pathway tabs -->
    <div v-show="activeTab==='p12'" class="mt-4 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="Sector total energy (M GJ)"><canvas ref="p12Energy" style="height:240px"></canvas></ChartBox>
        <ChartBox title="Energy intensity (GJ/metric ton)"><canvas ref="p12EKpi" style="height:240px"></canvas></ChartBox>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <ChartBox title="CO₂ Scope 1 & 2 stacked (M T.CO₂)"><canvas ref="p12CO2" style="height:240px"></canvas></ChartBox>
        <ChartBox title="CO₂ intensity (T.CO₂/metric ton)"><canvas ref="p12CKpi" style="height:240px"></canvas></ChartBox>
      </div>
    </div>
    <div v-show="activeTab==='p3'" class="mt-4 grid grid-cols-2 gap-3">
      <ChartBox title="Sector water withdrawals (M m³)"><canvas ref="p3Water" style="height:260px"></canvas></ChartBox>
      <ChartBox title="Water intensity (m³/metric ton)"><canvas ref="p3WKpi" style="height:260px"></canvas></ChartBox>
    </div>
    <div v-show="activeTab==='p4'" class="mt-4 grid grid-cols-2 gap-3">
      <ChartBox title="Waste recovery rate (%)"><canvas ref="p4Waste" style="height:260px"></canvas></ChartBox>
      <ChartBox title="ISO 14001 certification rate (%)"><canvas ref="p4ISO" style="height:260px"></canvas></ChartBox>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, h, defineComponent } from "vue";
import { Chart } from "chart.js";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";
import { C, TOOLTIP, ANIMATION, AXIS, YEARS, YEAR_LABELS, FALLBACK } from "@/composables/useCharts.js";

const auth = useAuthStore();
const activeTab = ref("general");
const overlayCompany = ref("");
const companies = ref([]);
const sectorData = ref(null);  // { years:[{year,value}], series:{ co2_kpi:[...], ... } }

const dataSource = computed(() => sectorData.value ? "live consolidated data" : "demo data");

const allTabs = [
  { id:"general", label:"General",                      dssOnly:false },
  { id:"p12",     label:"Pathway 1 & 2 — Energy & CO₂", dssOnly:true },
  { id:"p3",      label:"Pathway 3 — Water",             dssOnly:true },
  { id:"p4",      label:"Pathway 4 — Waste & ISO",       dssOnly:true },
];
const visibleTabs = computed(() => allTabs.filter(t => !t.dssOnly || auth.isDss));

// ── Parse analytics series
// API returns series values as [{year,value}] arrays
function parseS(key) {
  const raw = sectorData.value?.series?.[key];
  if (!raw) return null;
  // If array of objects {year,value}
  if (Array.isArray(raw) && raw.length && typeof raw[0] === "object" && "value" in raw[0]) {
    return YEARS.map(y => {
      const item = raw.find(r => r.year === y);
      return item ? item.value : null;
    });
  }
  // If plain array (already aligned to years)
  if (Array.isArray(raw)) return raw;
  return null;
}

function safe(key, fallbackKey, div=1) {
  const s = parseS(key);
  if (s) return s.map(v => v!=null ? v/div : null);
  return FALLBACK[fallbackKey] || Array(YEARS.length).fill(null);
}

const energy  = computed(() => safe("total_energy_gj","energy",1e6));
const scope1  = computed(() => safe("scope1_co2_t","scope1",1e6));
const scope2  = computed(() => safe("scope2_co2_t","scope2",1e6));
const water   = computed(() => safe("total_water_m3","water",1e6));
const ekpi    = computed(() => safe("energy_kpi","energy_kpi"));
const ckpi    = computed(() => safe("co2_kpi","co2_kpi"));
const wkpi    = computed(() => safe("water_kpi"));
const renew   = computed(() => safe("renewable_share_pct","renew_pct"));
const waste   = computed(() => safe("waste_recovery_pct","waste_recov"));
const iso     = computed(() => { const s=parseS("iso_certified_pct"); return s||Array(YEARS.length).fill(92); });

const headlineKPIs = computed(() => {
  const delta = (arr, down=true) => {
    if (!arr) return "";
    const a = arr.filter(v=>v!=null); if (a.length<2) return "";
    const pct = ((a[a.length-1]-a[a.length-2])/Math.abs(a[a.length-2])*100).toFixed(1);
    const good = (pct<0)===down;
    return `<span style="color:${good?'#16A34A':'#DC2626'}">${pct<0?"▼":"▲"} ${Math.abs(pct)}%</span>`;
  };
  const last = arr => arr?.filter(v=>v!=null).at(-1);
  const e=energy.value; const co2=scope1.value.map((v,i)=>(v||0)+(scope2.value[i]||0));
  return [
    { label:"Total Energy (latest)", value:last(e)?.toFixed(1)+"M"??"—",   unit:"GJ",      delta:delta(e)     },
    { label:"Total CO₂ (latest)",    value:last(co2)?.toFixed(2)+"M"??"—", unit:"T.CO₂",   delta:delta(co2)   },
    { label:"CO₂ Intensity",         value:last(ckpi.value)?.toFixed(3)??"—",unit:"T.CO₂/T",delta:delta(ckpi.value) },
    { label:"Renewable Electricity", value:last(renew.value)?.toFixed(1)+"%"??"—",unit:"of elec.",delta:delta(renew.value,false) },
    { label:"Waste Recovery",        value:last(waste.value)?.toFixed(1)+"%"??"—",unit:"of waste",delta:delta(waste.value,false) },
  ];
});

// ── Chart refs
const genEnergy=ref(null), genScope=ref(null), genWater=ref(null), genRenew=ref(null), genWaste=ref(null), genISO=ref(null);
const p12Energy=ref(null), p12EKpi=ref(null), p12CO2=ref(null), p12CKpi=ref(null);
const p3Water=ref(null), p3WKpi=ref(null);
const p4Waste=ref(null), p4ISO=ref(null);
const ch = {};
function destroyAll() { Object.values(ch).forEach(c=>{ try{c.destroy()}catch(_){} }); }

const OPT = (extra={}) => ({
  responsive:true, maintainAspectRatio:false, animation:ANIMATION,
  plugins:{ legend:{ display:true, position:"top", labels:{ color:"#64748B", boxWidth:9, font:{size:10}, padding:7 } }, tooltip:TOOLTIP },
  scales:AXIS, interaction:{ mode:"index", intersect:false }, ...extra
});
function line(label, data, color, fill=false) {
  return { label, data, borderColor:color, backgroundColor:fill?color+"15":"transparent", fill, tension:0.4, pointRadius:2, borderWidth:2 };
}
function mk(key, el, type, datasets, extra={}) {
  if (!el.value) return;
  if (ch[key]) { try{ch[key].destroy()}catch(_){} }
  ch[key] = new Chart(el.value, { type, data:{ labels:YEAR_LABELS, datasets }, options:{ ...OPT(), ...extra } });
}

async function buildCharts() {
  await nextTick();
  const e=energy.value, s1=scope1.value, s2=scope2.value, w=water.value;
  const ek=ekpi.value, ck=ckpi.value, wk=wkpi.value, rp=renew.value, wr=waste.value, is_=iso.value;

  mk("gE",  genEnergy, "line", [{ ...line("Energy (M GJ)",e,C.renew,true), pointRadius:2 }]);
  mk("gSc", genScope,  "line", [line("Scope 1",s1,C.co2,true), line("Scope 2",s2,"#1D4ED8",true)]);
  mk("gW",  genWater,  "bar",  [{ label:"Water (M m³)", data:w, backgroundColor:C.water+"80", borderRadius:2, borderWidth:0 }]);
  mk("gR",  genRenew,  "bar",  [{ label:"Renew. %", data:rp, backgroundColor:C.renew+"90", borderRadius:2, borderWidth:0 }],
    { scales:{...AXIS,y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
  mk("gWs", genWaste,  "line", [{ ...line("Recovery %",wr,C.waste,true), pointRadius:2 }],
    { scales:{...AXIS,y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
  mk("gI",  genISO,    "bar",  [{ label:"ISO 14001 %", data:is_, backgroundColor:"#0A224090", borderRadius:2, borderWidth:0 }],
    { scales:{...AXIS,y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });

  if (auth.isDss) {
    mk("p12E", p12Energy,"line",[{ ...line("Total energy (M GJ)",e,C.renew,true),pointRadius:2 }]);
    mk("p12EK",p12EKpi,  "line",[line("Energy KPI (GJ/T)",ek,"#7C3AED")]);
    mk("p12C", p12CO2,   "line",[line("Scope 1",s1,C.co2,true),line("Scope 2",s2.map((v,i)=>(v||0)+(s1[i]||0)),"#1D4ED8",true)]);
    mk("p12CK",p12CKpi,  "line",[line("CO₂ KPI",ck,C.co2)]);
    mk("p3W",  p3Water,  "line",[{ ...line("Water (M m³)",w,C.teal,true),pointRadius:2 }]);
    mk("p3WK", p3WKpi,   "line",[line("Water KPI (m³/T)",wk,C.teal)]);
    mk("p4W",  p4Waste,  "line",[{ ...line("Recovery %",wr,C.waste,true),pointRadius:2 }],
      { scales:{...AXIS,y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
    mk("p4I",  p4ISO,    "bar", [{ label:"ISO 14001 %", data:is_, backgroundColor:"#0A224090", borderRadius:2, borderWidth:0 }],
      { scales:{...AXIS,y:{...AXIS.y,ticks:{...AXIS.y.ticks,callback:v=>v+"%"}}} });
  }
}

async function loadData() {
  try {
    const params = { year_from:2009, year_to:2023 };
    if (overlayCompany.value) params.company_id = overlayCompany.value;
    sectorData.value = await api.getAnalytics(params);
    await buildCharts();
  } catch(e) { console.error("Analysis:", e); await buildCharts(); }
}

async function loadCompanies() {
  try { companies.value = await api.getCompanies(); } catch(_) {}
}

onMounted(async () => { if (auth.isDss) await loadCompanies(); await loadData(); });
onUnmounted(destroyAll);
watch(overlayCompany, loadData);

const ChartBox = defineComponent({
  props: { title:String },
  setup(props, { slots }) {
    return () => h("div", { class:"bg-white border border-gray-100 rounded-xl overflow-hidden" }, [
      h("div", { class:"px-4 pt-3 pb-1.5 border-b border-gray-50 text-[12.5px] font-semibold text-gray-700" }, props.title),
      h("div", { class:"p-3" }, slots.default?.()),
    ]);
  },
});
</script>