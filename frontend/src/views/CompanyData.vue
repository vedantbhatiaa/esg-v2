<template>
  <div>
    <div class="flex items-center gap-3 mb-5">
      <button @click="$router.push('/portfolio')" class="text-xs text-gray-400 hover:text-navy flex items-center gap-1">
        ← Portfolio
      </button>
      <div class="w-px h-4 bg-gray-200"></div>
      <div>
        <h2 class="text-xl font-bold text-gray-900">Company Data</h2>
        <p class="text-sm text-gray-400 mt-0.5">Full KPI template — all historical years</p>
      </div>
    </div>

    <!-- Selectors -->
    <div class="flex gap-3 mb-5">
      <select v-model="selCompany" class="h-9 border border-gray-200 rounded-lg px-3 text-sm bg-white min-w-48"
        @change="loadData">
        <option v-for="c in companies" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="selYear" class="h-9 border border-gray-200 rounded-lg px-3 text-sm bg-white"
        @change="loadData">
        <option v-for="y in availYears" :key="y" :value="y">{{ y }}</option>
      </select>
      <div v-if="loading" class="text-sm text-gray-400 self-center">Loading…</div>
    </div>

    <!-- KPI quick cards -->
    <div v-if="kpis" class="grid grid-cols-6 gap-3 mb-5">
      <div v-for="k in kpiCards" :key="k.label" class="bg-white border border-gray-100 rounded-xl p-3 text-center">
        <div class="text-[9px] text-gray-400 uppercase tracking-wide font-semibold mb-1">{{ k.label }}</div>
        <div class="text-lg font-bold" :style="{color:k.color}">{{ k.value }}</div>
        <div class="text-[9px] text-gray-400">{{ k.unit }}</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-4 gap-1">
      <button v-for="t in tabs" :key="t" @click="activeTab=t"
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="activeTab===t ? 'border-navy text-navy' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ t }}
      </button>
    </div>

    <!-- Main Data tab -->
    <div v-if="activeTab==='Main Data'" class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs border-collapse" v-if="tableRows.length">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100 sticky left-0 bg-gray-50">Indicator</th>
              <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Unit</th>
              <th v-for="y in histYears" :key="y" class="px-4 py-2.5 text-right text-[9px] font-bold border-b border-gray-100"
                :class="y===selYear ? 'text-blue-600 bg-blue-50' : 'text-gray-400'">{{ y }}</th>
              <th class="px-4 py-2.5 text-right text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">YoY %</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in tableRows" :key="row.label">
              <tr v-if="row.type==='section'" class="bg-emerald-50">
                <td :colspan="histYears.length+3" class="px-4 py-2 text-[11px] font-bold text-emerald-800 border-b border-emerald-100 uppercase tracking-wide">
                  ▸ {{ row.label }}
                </td>
              </tr>
              <tr v-else class="border-b border-gray-50 hover:bg-gray-50/50">
                <td class="px-4 py-2 font-medium text-gray-700 sticky left-0 bg-white">{{ row.label }}</td>
                <td class="px-4 py-2 text-gray-400">{{ row.unit }}</td>
                <td v-for="y in histYears" :key="y" class="px-4 py-2 text-right tabular-nums"
                  :class="[y===selYear ? (row.type==='input' ? 'bg-blue-50 text-blue-800 font-semibold' : 'bg-indigo-50 text-indigo-700 italic') : (row.type==='calc' ? 'text-gray-400 italic' : 'text-gray-700')]">
                  {{ row.values[y] ?? '—' }}
                </td>
                <td class="px-4 py-2 text-right tabular-nums" :class="yoyClass(row.yoy)">{{ row.yoy }}</td>
              </tr>
            </template>
          </tbody>
        </table>
        <div v-else class="px-5 py-10 text-center text-sm text-gray-400">
          No data found. Ensure the Python service is running and master CSV exists.
        </div>
      </div>
      <!-- Legend -->
      <div class="flex gap-4 px-4 py-3 bg-gray-50 border-t border-gray-100 flex-wrap text-[10px] text-gray-500">
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-blue-100 border border-blue-200 inline-block"></span>Input (selected yr)</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-indigo-50 border border-indigo-200 inline-block"></span>Calculated (selected yr)</span>
        <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-white border border-gray-200 inline-block"></span>Input (historical)</span>
      </div>
    </div>

    <!-- Waste tab -->
    <div v-if="activeTab==='Waste'" class="bg-white border border-gray-100 rounded-xl p-5">
      <div class="grid grid-cols-3 gap-4 mb-4">
        <div class="bg-gray-50 rounded-lg p-3">
          <div class="text-xs text-gray-400 mb-1">Total Waste</div>
          <div class="text-2xl font-bold text-purple-700">{{ fmt(raw?.waste_total) }}</div>
          <div class="text-xs text-gray-400">metric T</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-3">
          <div class="text-xs text-gray-400 mb-1">Waste Recovered</div>
          <div class="text-2xl font-bold text-green-700">{{ fmt(raw?.waste_recovery) }}</div>
          <div class="text-xs text-gray-400">metric T</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-3">
          <div class="text-xs text-gray-400 mb-1">Recovery Rate</div>
          <div class="text-2xl font-bold text-navy">{{ kpis?.waste_recovery_pct ? (kpis.waste_recovery_pct*100).toFixed(1)+'%' : '—' }}</div>
          <div class="text-xs text-gray-400">of total waste</div>
        </div>
      </div>
      <div class="text-sm text-gray-500">Consistency check:
        <span :class="kpis?.check_waste ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'">
          {{ kpis?.check_waste ? '✓ OK' : '✕ FAIL — recovery exceeds total' }}
        </span>
      </div>
    </div>

    <!-- Conversion tab -->
    <div v-if="activeTab==='Conversion Tables'" class="grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 text-sm font-semibold">Energy conversion factors</div>
        <table class="w-full text-xs">
          <thead><tr class="bg-gray-50"><th class="px-4 py-2 text-left text-[9px] text-gray-400 uppercase">Fuel</th><th class="px-4 py-2 text-right text-[9px] text-gray-400 uppercase">CO₂ EF (T/GJ)</th></tr></thead>
          <tbody>
            <tr v-for="ef in EF_TABLE" :key="ef.fuel" class="border-t border-gray-50">
              <td class="px-4 py-2 text-gray-700">{{ ef.fuel }}</td>
              <td class="px-4 py-2 text-right tabular-nums text-gray-700">{{ ef.ef }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 text-sm font-semibold">Unit conversion factors</div>
        <table class="w-full text-xs">
          <thead><tr class="bg-gray-50">
            <th class="px-4 py-2 text-left text-[9px] text-gray-400 uppercase">From</th>
            <th class="px-4 py-2 text-left text-[9px] text-gray-400 uppercase">To</th>
            <th class="px-4 py-2 text-right text-[9px] text-gray-400 uppercase">Factor</th>
          </tr></thead>
          <tbody>
            <tr v-for="u in UNIT_TABLE" :key="u.from+u.to" class="border-t border-gray-50">
              <td class="px-4 py-2 text-gray-700">{{ u.from }}</td>
              <td class="px-4 py-2 text-gray-700">{{ u.to }}</td>
              <td class="px-4 py-2 text-right tabular-nums text-gray-700">{{ u.factor }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api.js";

const route  = useRoute();
const selCompany = ref("");
const selYear    = ref(2023);
const companies  = ref([]);
const availYears = ref([]);
const loading    = ref(false);
const raw        = ref(null);
const kpis       = ref(null);
const allData    = ref({});  // { year: { raw, kpis } }
const activeTab  = ref("Main Data");
const tabs = ["Main Data","Waste","Conversion Tables"];

const histYears = computed(() => Object.keys(allData.value).map(Number).sort((a,b)=>a-b));

const C = { navy:"#0A2240", co2:"#475569", energy:"#F59E0B", water:"#0891B2", renew:"#16A34A", waste:"#7C3AED" };

const kpiCards = computed(() => {
  if (!kpis.value) return [];
  const k = kpis.value;
  const r = raw.value || {};
  const re = ((r.renew_elec_purchased||0)+(r.self_gen_elec||0)) / Math.max(k.total_electricity||1,1)*100;
  return [
    { label:"CO₂ KPI",     value:(k.co2_kpi||0).toFixed(3),               unit:"T.CO₂/T", color:C.co2    },
    { label:"Energy KPI",  value:(k.energy_kpi||0).toFixed(2),             unit:"GJ/T",    color:C.energy },
    { label:"Water KPI",   value:(k.water_kpi||0).toFixed(2),              unit:"m³/T",    color:C.water  },
    { label:"Renewable",   value:re.toFixed(1),                            unit:"%",       color:C.renew  },
    { label:"Waste Rec.",  value:k.waste_recovery_pct?(k.waste_recovery_pct).toFixed(1):"—", unit:"%", color:C.waste },
    { label:"ISO 14001",   value:k.iso_certified_pct?k.iso_certified_pct.toFixed(0):"—",    unit:"%",       color:C.navy  },
  ];
});

const TABLE_DEF = [
  { type:"section", label:"ISO 14001" },
  { type:"input",   label:"Total no. of sites",       unit:"no.",     key:"total_sites" },
  { type:"input",   label:"ISO 14001 certified sites",unit:"no.",     key:"iso_sites" },
  { type:"calc",    label:"% certified sites",         unit:"%",       fn:(r,k)=>k?.iso_certified_pct?k.iso_certified_pct.toFixed(1)+"%":"—" },
  { type:"section", label:"Production" },
  { type:"input",   label:"Production",               unit:"metric T",key:"production", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"section", label:"Water" },
  { type:"input",   label:"Water withdrawals",        unit:"m³",      key:"water_withdrawals", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"calc",    label:"Water KPI",                unit:"m³/T",    fn:(_,k)=>k?.water_kpi?k.water_kpi.toFixed(2):"—" },
  { type:"section", label:"Energy" },
  { type:"calc",    label:"Total Electricity",        unit:"GJ",      fn:(_,k)=>k?.total_electricity?Number(k.total_electricity).toLocaleString():"—" },
  { type:"input",   label:"Renewable Electricity",    unit:"GJ",      key:"renew_elec_purchased", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"Non-Renewable Electricity",unit:"GJ",      key:"nonrenew_elec_purchased", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"Natural Gas",              unit:"GJ LHV",  key:"nat_gas", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"Coal",                     unit:"GJ LHV",  key:"coal_sub", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"Diesel",                   unit:"GJ LHV",  key:"diesel", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"LPG",                      unit:"GJ LHV",  key:"lpg", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"calc",    label:"TOTAL ENERGY",             unit:"GJ",      fn:(_,k)=>k?.total_energy_gj?Number(k.total_energy_gj).toLocaleString():"—" },
  { type:"calc",    label:"Energy KPI",               unit:"GJ/T",    fn:(_,k)=>k?.energy_kpi?k.energy_kpi.toFixed(2):"—" },
  { type:"section", label:"CO₂ Emissions" },
  { type:"input",   label:"Scope 2 Steam",            unit:"T.CO₂",   key:"co2_scope2_steam", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"calc",    label:"Total CO₂ Scope 1",        unit:"T.CO₂",   fn:(_,k)=>k?.total_co2_scope1?Number(k.total_co2_scope1).toLocaleString():"—" },
  { type:"calc",    label:"Total CO₂ Scope 2",        unit:"T.CO₂",   fn:(_,k)=>k?.total_co2_scope2?Number(k.total_co2_scope2).toLocaleString():"—" },
  { type:"calc",    label:"TOTAL CO₂",                unit:"T.CO₂",   fn:(_,k)=>k?.total_co2_t?Number(k.total_co2_t).toLocaleString():"—" },
  { type:"calc",    label:"CO₂ KPI",                  unit:"T.CO₂/T", fn:(_,k)=>k?.co2_kpi?k.co2_kpi.toFixed(3):"—" },
  { type:"section", label:"Waste" },
  { type:"input",   label:"Total waste",              unit:"metric T", key:"waste_total", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"input",   label:"Waste recovered",          unit:"metric T", key:"waste_recovery", fmt:(v)=>v?Number(v).toLocaleString():"—" },
  { type:"calc",    label:"Recovery rate",            unit:"%",        fn:(_,k)=>k?.waste_recovery_pct?(k.waste_recovery_pct).toFixed(1)+"%":"—" },
];

const tableRows = computed(() => {
  const ys = histYears.value;
  if (!ys.length) return [];
  return TABLE_DEF.map(def => {
    if (def.type === "section") return def;
    const vals = {};
    ys.forEach(y => {
      const d = allData.value[y];
      if (!d) { vals[y] = "—"; return; }
      if (def.fn) vals[y] = def.fn(d.raw||{}, d.kpis||{});
      else {
        const v = (d.raw||{})[def.key];
        vals[y] = v != null ? (def.fmt ? def.fmt(v) : Number(v).toLocaleString()) : "—";
      }
    });
    // YoY for last two years
    let yoy = "—";
    if (ys.length >= 2) {
      const lv = parseFloat(String(vals[ys[ys.length-1]]).replace(/,/g,"").replace("%","")) || 0;
      const pv = parseFloat(String(vals[ys[ys.length-2]]).replace(/,/g,"").replace("%","")) || 0;
      if (pv && pv !== 0) yoy = ((lv-pv)/Math.abs(pv)*100).toFixed(1) + "%";
    }
    return { ...def, values: vals, yoy };
  });
});

function yoyClass(yoy) {
  if (!yoy || yoy === "—") return "text-gray-400";
  return parseFloat(yoy) < 0 ? "text-green-600 font-medium" : "text-red-500 font-medium";
}

function fmt(v) { return v != null ? Number(v).toLocaleString() : "—"; }

const EF_TABLE = [
  { fuel:"Natural Gas", ef:"0.0561" }, { fuel:"Coal", ef:"0.0961" }, { fuel:"Propane", ef:"0.0631" },
  { fuel:"Fuel Oil", ef:"0.0774" }, { fuel:"Diesel", ef:"0.0741" }, { fuel:"Petrol", ef:"0.0693" },
  { fuel:"Biomass", ef:"0.0" }, { fuel:"Waste Tires", ef:"0.0475" }, { fuel:"LPG", ef:"0.0561" }, { fuel:"Other", ef:"0.0719" },
];
const UNIT_TABLE = [
  { from:"kg", to:"metric T", factor:"0.001" }, { from:"lb", to:"metric T", factor:"0.000454" },
  { from:"MWh", to:"GJ", factor:"3.6" }, { from:"TJ", to:"GJ", factor:"1000.0" },
  { from:"m³", to:"m³", factor:"1.0" },
];

async function loadCompanies() {
  try {
    const res = await api.getCompanies();
    companies.value = Array.isArray(res) ? res : (res?.companies || []);
    // Pre-select from query param
    const qco = route.query?.company;
    if (qco && companies.value.includes(qco)) selCompany.value = qco;
    else if (companies.value.length) selCompany.value = companies.value[0];
    await loadData();
  } catch(e) { console.error("CompanyData companies:", e); }
}

async function loadData() {
  if (!selCompany.value) return;
  loading.value = true;
  allData.value = {};
  try {
    // Use getCompanyData which returns all years with raw+kpis
    const summary = await api.getCompanyData(selCompany.value);
    if (summary?.years?.length) {
      availYears.value = summary.years.slice().sort((a,b)=>b-a);
      if (!availYears.value.includes(selYear.value) && availYears.value.length)
        selYear.value = availYears.value[0];
    }
    // Populate allData from summary
    if (summary?.summary) {
      for (const s of summary.summary) {
        allData.value[s.year] = { raw: s.raw || {}, kpis: s.kpis || {} };
      }
    }
    // Set current year raw+kpis
    const cur = allData.value[selYear.value];
    if (cur) { raw.value = cur.raw; kpis.value = cur.kpis; }
  } catch(e) { console.error("CompanyData load:", e); }
  finally { loading.value = false; }
}

onMounted(loadCompanies);
watch([selCompany, selYear], ([co, yr], [oldCo]) => {
  if (co !== oldCo) loadData();
  else loadData();
});
</script>