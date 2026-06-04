<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div>
        <div class="text-xl font-bold">My Records</div>
        <div class="text-sm text-gray-400 mt-0.5">{{ auth.companyName }} · Historical KPI data</div>
      </div>
      <div class="flex gap-2 items-center">
        <select v-model="selYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <button @click="saveData" :disabled="saving"
          class="h-8 px-4 bg-navy text-white rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity">
          {{ saving ? "Saving…" : "💾 Submit & Save" }}
        </button>
      </div>
    </div>

    <div v-if="saveMsg" class="mb-3 px-4 py-2.5 rounded-lg text-sm border"
      :class="saveOk ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-100 text-red-600'">
      ✅ {{ saveMsg }}
    </div>

    <!-- 5 template tabs -->
    <div class="flex border-b border-gray-200 overflow-x-auto">
      <button v-for="tab in TABS" :key="tab.id" @click="activeTab=tab.id"
        class="px-4 py-2.5 text-xs font-medium border-b-2 whitespace-nowrap transition-colors"
        :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Main KPI Data tab -->
    <div v-show="activeTab==='main'" class="mt-3">
      <div class="text-xs text-gray-400 mb-2">
        ℹ Blue cells = company input · grey italic = auto-calculated formula
      </div>
      <div class="overflow-x-auto rounded-xl border border-gray-100">
        <table class="w-full text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100 min-w-40">Indicator</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Unit</th>
              <th v-for="y in histYears" :key="y"
                class="px-3 py-2.5 text-right text-[9px] font-bold uppercase tracking-wider border-b border-gray-100"
                :class="y === selYear ? 'text-navy bg-blue-50' : 'text-gray-400'">{{ y }}</th>
              <th class="px-3 py-2.5 text-right text-[9px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-100">YoY %</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in tableRows" :key="row.label">
              <!-- Section header -->
              <tr v-if="row.type==='section'" class="border-b border-green-100">
                <td :colspan="histYears.length + 3"
                  class="px-4 py-2 text-[10px] font-extrabold uppercase tracking-wider"
                  style="background:#E8F5F0;color:#065F46;border-top:2px solid #6EE7B7">
                  ▸ {{ row.label }}
                </td>
              </tr>
              <!-- Data row -->
              <tr v-else class="border-b border-gray-50 hover:bg-gray-50">
                <td class="px-4 py-1.5 font-medium text-gray-700">{{ row.label }}</td>
                <td class="px-3 py-1.5 text-gray-400 whitespace-nowrap">{{ row.unit }}</td>
                <td v-for="y in histYears" :key="y"
                  class="px-3 py-1.5 text-right tabular-nums"
                  :class="{
                    'bg-blue-50 text-blue-700 font-semibold': y===selYear && row.type==='input',
                    'bg-indigo-50 text-indigo-600 italic': y===selYear && row.type==='calc',
                    'text-gray-400 italic': y!==selYear && row.type==='calc',
                    'text-gray-600': y!==selYear && row.type==='input',
                  }">{{ row.values[y] || '—' }}</td>
                <td class="px-3 py-1.5 text-right font-semibold text-xs"
                  :class="row.yoy?.startsWith('+') && !row.yoyGoodUp ? 'text-red-500' : row.yoy?.startsWith('+') ? 'text-green-600' : row.yoy?.startsWith('-') && row.yoyGoodUp ? 'text-red-500' : 'text-green-600'">
                  {{ row.yoy || '—' }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Electricity by Country tab -->
    <div v-show="activeTab==='electricity'" class="mt-3">
      <div class="text-sm font-semibold mb-2">Non-Renewable Electricity Purchased by Country</div>
      <div class="text-xs text-gray-400 mb-3">Values in MWh · 1 MWh = 3.6 GJ (conversion applied automatically)</div>
      <div class="overflow-x-auto rounded-xl border border-gray-100">
        <table class="w-full text-xs border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100 sticky left-0 bg-gray-50 min-w-36">Country</th>
              <th class="px-2 py-2 text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Unit</th>
              <th v-for="y in elecYears" :key="y" class="px-2 py-2 text-right text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">{{ y }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="country in COUNTRIES" :key="country" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-1.5 font-medium text-gray-700 sticky left-0 bg-white">{{ country }}</td>
              <td class="px-2 py-1.5 text-gray-400">MWh</td>
              <td v-for="y in elecYears" :key="y" class="px-2 py-1.5">
                <input type="number" min="0" step="1000"
                  :value="elecData[country]?.[y] || 0"
                  @change="(e) => setElecVal(country, y, e.target.value)"
                  class="w-24 h-7 border border-gray-200 rounded px-2 text-xs text-right tabular-nums focus:outline-none focus:border-blue-400">
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Waste tab -->
    <div v-show="activeTab==='waste'" class="mt-3">
      <div class="text-sm font-semibold mb-3">Waste KPIs — Corporate Units</div>
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-xs text-gray-400">Total Waste</div>
          <div class="text-xl font-bold mt-1">{{ fmtNum(currentKPIs?.waste_total || 0) }} T</div>
        </div>
        <div class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-xs text-gray-400">Recovery Rate</div>
          <div class="text-xl font-bold mt-1">{{ (((currentKPIs?.waste_recovery_pct||0)*100).toFixed(1)) }}%</div>
        </div>
        <div class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-xs text-gray-400">Consistency</div>
          <div class="text-xl font-bold mt-1" :class="currentKPIs?.check_waste ? 'text-green-600' : 'text-red-600'">
            {{ currentKPIs?.check_waste ? 'OK' : 'Error' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Qualitative tab -->
    <div v-show="activeTab==='qualitative'" class="mt-3 space-y-4">
      <div class="text-xs text-gray-500 mb-3">Qualitative data to help interpret quantitative KPIs. Non-public information kept confidential.</div>
      <QualSection v-for="sec in qualSections" :key="sec.title" :title="sec.title" :questions="sec.questions" />
    </div>

    <!-- Conversion tables tab -->
    <div v-show="activeTab==='conversion'" class="mt-3 grid grid-cols-2 gap-4">
      <div>
        <div class="text-sm font-semibold mb-2">Energy conversion factors</div>
        <table class="w-full text-xs border-collapse">
          <thead><tr class="bg-gray-50"><th class="px-3 py-2 text-left border-b">Fuel</th><th class="px-3 py-2 border-b">Unit</th><th class="px-3 py-2 border-b">CO₂ EF (T/GJ)</th></tr></thead>
          <tbody>
            <tr v-for="f in convFactors" :key="f.name" class="border-b border-gray-50">
              <td class="px-3 py-1.5">{{ f.name }}</td>
              <td class="px-3 py-1.5 text-gray-400">GJ LHV</td>
              <td class="px-3 py-1.5 tabular-nums">{{ f.ef }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div>
        <div class="text-sm font-semibold mb-2">Unit conversion factors</div>
        <table class="w-full text-xs border-collapse">
          <thead><tr class="bg-gray-50"><th class="px-3 py-2 text-left border-b">Indicator</th><th class="px-3 py-2 border-b">From</th><th class="px-3 py-2 border-b">To</th><th class="px-3 py-2 border-b">Factor</th></tr></thead>
          <tbody>
            <tr v-for="f in unitConv" :key="f.ind+f.from" class="border-b border-gray-50">
              <td class="px-3 py-1.5">{{ f.ind }}</td>
              <td class="px-3 py-1.5 text-gray-400">{{ f.from }}</td>
              <td class="px-3 py-1.5 text-gray-400">{{ f.to }}</td>
              <td class="px-3 py-1.5 tabular-nums">{{ f.factor }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineComponent, h } from "vue";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";

const auth = useAuthStore();

const TABS = [
  { id:"main",         label:"Main Data Input" },
  { id:"electricity",  label:"Electricity by Country" },
  { id:"waste",        label:"Waste" },
  { id:"qualitative",  label:"Qualitative Data" },
  { id:"conversion",   label:"Conversion Tables" },
];

const activeTab     = ref("main");
const selYear       = ref(2023);
const availableYears= ref([2023,2022,2021,2020]);
const saving        = ref(false);
const saveMsg       = ref("");
const saveOk        = ref(false);
const histData      = ref({});   // { year: { kpis, raw } }
const currentKPIs   = ref(null);
const elecData      = ref({});   // { country: { year: mwhVal } }

const histYears = computed(() => Object.keys(histData.value).map(Number).sort().slice(-10));
const elecYears = computed(() => [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]);

function fmtNum(n) { return n ? Math.round(n).toLocaleString() : "—"; }
function fmtVal(v, dec=0) {
  if (v == null || v === "" || v === 0) return "—";
  return dec > 0 ? Number(v).toFixed(dec) : Math.round(v).toLocaleString();
}

const COUNTRIES = [
  "Canada","Chile","Mexico","United States","Australia","Japan","Korea","New Zealand",
  "Austria","Belgium","Czech Republic","Denmark","Finland","France","Germany","Hungary",
  "Iceland","Ireland","Italy","Luxembourg","Netherlands","Norway","Poland","Portugal",
  "Spain","Sweden","Switzerland","Turkey","United Kingdom","China","India",
];

// Template rows definition
const ROWS = [
  { type:"section", label:"ISO 14001" },
  { type:"input",  label:"Total no. of sites",                    unit:"no.",    key:"total_sites",             fmt:0 },
  { type:"input",  label:"ISO 14001 certified sites",             unit:"no.",    key:"iso_sites",               fmt:0 },
  { type:"calc",   label:"% certified sites",                     unit:"%",      calc:(i,o)=>o.pct_certified!=null?(o.pct_certified*100).toFixed(1)+"%":"—" },
  { type:"section", label:"Production" },
  { type:"input",  label:"Production",                            unit:"metric T",key:"production",             fmt:0 },
  { type:"section", label:"Water" },
  { type:"input",  label:"Water withdrawals",                     unit:"m³",     key:"water_withdrawals",       fmt:0 },
  { type:"calc",   label:"Water intensity KPI",                   unit:"m³/T",   calc:(i,o)=>o.water_kpi?.toFixed(2) },
  { type:"section", label:"Energy" },
  { type:"calc",   label:"Total Electricity",                     unit:"GJ",     calc:(i,o)=>fmtNum(o.total_electricity) },
  { type:"input",  label:"— Renewable electricity purchased",     unit:"GJ",     key:"renew_elec_purchased",    fmt:0 },
  { type:"input",  label:"— Non-renewable electricity",           unit:"GJ",     key:"nonrenew_elec_purchased", fmt:0 },
  { type:"input",  label:"— Self-generated renewable",            unit:"GJ",     key:"self_gen_elec",           fmt:0 },
  { type:"input",  label:"Purchased Steam",                       unit:"GJ",     key:"purchased_steam",         fmt:0 },
  { type:"input",  label:"Sold Electricity",                      unit:"GJ",     key:"sold_electricity",        fmt:0 },
  { type:"input",  label:"Sold Steam",                            unit:"GJ",     key:"sold_steam",              fmt:0 },
  { type:"input",  label:"Natural Gas",                           unit:"GJ LHV", key:"nat_gas",                 fmt:0 },
  { type:"input",  label:"Coal (all types)",                      unit:"GJ LHV", key:"coal_sub",                fmt:0 },
  { type:"input",  label:"Propane",                               unit:"GJ LHV", key:"propane",                 fmt:0 },
  { type:"input",  label:"Fuel Oil",                              unit:"GJ LHV", key:"fuel_oil_heavy_a",        fmt:0 },
  { type:"input",  label:"Diesel",                                unit:"GJ LHV", key:"diesel",                  fmt:0 },
  { type:"input",  label:"Petrol",                                unit:"GJ LHV", key:"petrol",                  fmt:0 },
  { type:"input",  label:"Biomass",                               unit:"GJ LHV", key:"biomass",                 fmt:0 },
  { type:"input",  label:"Waste tires",                           unit:"metric T",key:"waste_tires_mt",         fmt:0 },
  { type:"input",  label:"LPG",                                   unit:"GJ LHV", key:"lpg",                     fmt:0 },
  { type:"input",  label:"Other fuels",                           unit:"GJ LHV", key:"other_fuels",             fmt:0 },
  { type:"calc",   label:"TOTAL ENERGY",                          unit:"GJ",     calc:(i,o)=>fmtNum(o.total_energy), bold:true },
  { type:"calc",   label:"Energy intensity KPI",                  unit:"GJ/T",   calc:(i,o)=>o.energy_kpi?.toFixed(2) },
  { type:"section", label:"CO2 Emissions" },
  { type:"input",  label:"Scope 2 — Steam",                       unit:"T.CO₂",  key:"co2_scope2_steam",        fmt:0 },
  { type:"calc",   label:"CO₂ — Natural Gas",                     unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.co2_nat_gas) },
  { type:"calc",   label:"CO₂ — Coal",                            unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.co2_coal) },
  { type:"calc",   label:"CO₂ — Diesel",                          unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.co2_diesel) },
  { type:"calc",   label:"TOTAL CO₂ Scope 1",                     unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.total_co2_scope1), bold:true },
  { type:"calc",   label:"TOTAL CO₂ Scope 2",                     unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.total_co2_scope2), bold:true },
  { type:"calc",   label:"TOTAL CO₂ (S1+S2)",                     unit:"T.CO₂",  calc:(i,o)=>fmtNum(o.total_co2), bold:true },
  { type:"calc",   label:"CO₂ intensity KPI",                     unit:"T.CO₂/T",calc:(i,o)=>o.co2_kpi?.toFixed(3) },
  { type:"section", label:"Waste" },
  { type:"input",  label:"Total waste generated",                 unit:"metric T",key:"waste_total",            fmt:0 },
  { type:"input",  label:"Waste sent to recovery",                unit:"metric T",key:"waste_recovery",         fmt:0 },
  { type:"calc",   label:"Waste sent to elimination",             unit:"metric T",calc:(i,o)=>fmtNum(o.waste_elimination) },
  { type:"calc",   label:"Recovery rate",                         unit:"%",       calc:(i,o)=>o.waste_recovery_pct?(o.waste_recovery_pct*100).toFixed(1)+"%":"—" },
];

const tableRows = computed(() => {
  const years = histYears.value;
  return ROWS.map(r => {
    if (r.type === "section") return { type:"section", label: r.label };

    const values = {};
    for (const y of years) {
      const d = histData.value[y];
      if (!d) { values[y] = "—"; continue; }
      if (r.type === "input") {
        const v = d.raw?.[r.key];
        values[y] = v != null && v !== 0 ? (r.fmt === 0 ? fmtNum(v) : Number(v).toFixed(r.fmt)) : "—";
      } else {
        values[y] = r.calc ? r.calc(d.raw||{}, d.kpis||{}) : "—";
      }
    }

    // YoY
    const sortedYrs = [...years].sort((a,b)=>b-a);
    const curY = sortedYrs[0], prevY = sortedYrs[1];
    let yoy = "—";
    if (curY && prevY && histData.value[curY] && histData.value[prevY]) {
      let cv, pv;
      if (r.type === "input") {
        cv = histData.value[curY]?.raw?.[r.key];
        pv = histData.value[prevY]?.raw?.[r.key];
      } else if (r.calc) {
        try { cv = parseFloat(r.calc(histData.value[curY].raw||{}, histData.value[curY].kpis||{})?.replace(/,/g,"").replace("%","")) } catch(_) {}
        try { pv = parseFloat(r.calc(histData.value[prevY].raw||{}, histData.value[prevY].kpis||{})?.replace(/,/g,"").replace("%","")) } catch(_) {}
      }
      if (cv && pv && pv !== 0) yoy = ((cv-pv)/Math.abs(pv)*100).toFixed(1)+"%";
    }

    return { type:r.type, label:r.label, unit:r.unit||"", values, yoy: yoy !== "—" ? (parseFloat(yoy)>=0?"+":"")+yoy : "—", yoyGoodUp: false };
  });
});

function setElecVal(country, year, val) {
  if (!elecData.value[country]) elecData.value[country] = {};
  elecData.value[country][year] = parseFloat(val) || 0;
}

async function loadData() {
  try {
    const data = await api.getCompanyData(auth.companyName);
    if (data?.summary && data.years) {
      availableYears.value = data.years.slice().sort((a,b)=>b-a);
      if (data.years.length) {
        selYear.value = data.years[data.years.length - 1]; // most recent
      }
      // Load raw data for each year (needed for template table)
      for (const s of data.summary) {
        histData.value[s.year] = { raw: {}, kpis: s.kpis || {} };
      }
      // Load raw for all years in parallel
      await Promise.all(data.years.map(async (y) => {
        try {
          const d = await api.getCompanyData(auth.companyName, y);
          if (d?.raw) histData.value[y] = { raw: d.raw, kpis: d.kpis || histData.value[y]?.kpis || {} };
        } catch(_) {}
      }));
      currentKPIs.value = histData.value[selYear.value]?.kpis || null;
    }
  } catch(e) {
    console.error("MyRecords load error:", e);
  }
}

async function saveData() {
  const d = histData.value[selYear.value];
  if (!d?.raw) return;
  saving.value = true;
  try {
    const result = await api.submitData({ company: auth.companyName, year: selYear.value, data: d.raw });
    saveOk.value  = true;
    saveMsg.value = result.message;
    setTimeout(() => saveMsg.value = "", 5000);
  } catch(e) {
    saveOk.value  = false;
    saveMsg.value = `Save failed: ${e.response?.data?.error || e.message}`;
  } finally {
    saving.value = false;
  }
}

onMounted(loadData);
watch(selYear, () => { currentKPIs.value = histData.value[selYear.value]?.kpis || null; });

// Qualitative section component
const qualSections = [
  { title:"⚡ Energy", questions:[
    { label:"Program — Management approach", hint:"Policies, commitments, ISO 50001, goals", key:"energy_prog" },
    { label:"Impacts", hint:"Expected impact on the Energy KPI", key:"energy_imp" },
    { label:"Specific projects completed / underway", hint:"Current or planned energy projects", key:"energy_proj" },
  ]},
  { title:"CO₂ Emissions", questions:[
    { label:"Program — Management approach", hint:"Policies, commitments, goals & targets", key:"co2_prog" },
    { label:"Specific projects completed / underway", hint:"CO₂ reduction projects", key:"co2_proj" },
  ]},
  { title:"💧 Water", questions:[
    { label:"Program — Management approach", hint:"Policies, commitments, goals & targets", key:"water_prog" },
    { label:"Specific projects completed / underway", hint:"Water management projects", key:"water_proj" },
  ]},
  { title:"♻ Waste", questions:[
    { label:"Program — Management approach", hint:"Policies, commitments, goals & targets", key:"waste_prog" },
    { label:"Specific projects completed / underway", hint:"Waste reduction projects", key:"waste_proj" },
  ]},
];

const QualSection = defineComponent({
  props: { title: String, questions: Array },
  setup(props) {
    return () => h("div", { class:"bg-white border border-gray-100 rounded-xl overflow-hidden" }, [
      h("div", { class:"px-4 py-3 font-semibold text-sm text-white", style:"background:#0A2240;border-radius:10px 10px 0 0" }, props.title),
      h("div", { class:"p-4 space-y-4" },
        props.questions.map(q => h("div", { key:q.key }, [
          h("div", { class:"text-sm font-semibold text-gray-800 mb-1" }, q.label),
          q.hint ? h("div", { class:"text-xs text-gray-400 mb-2" }, q.hint) : null,
          h("div", { class:"grid grid-cols-3 gap-2" }, [
            h("div", { class:"flex flex-col gap-1" }, [
              h("label", { class:"text-[10px] text-gray-400 font-medium" }, "Public information"),
              h("textarea", { class:"border border-gray-200 rounded-lg p-2 text-xs resize-none", rows:3, placeholder:"For the Global KPIs Report…" }),
            ]),
            h("div", { class:"flex flex-col gap-1" }, [
              h("label", { class:"text-[10px] text-gray-400 font-medium" }, "Non-public (confidential)"),
              h("textarea", { class:"border border-gray-200 rounded-lg p-2 text-xs resize-none", rows:3, placeholder:"Used only at aggregated level…" }),
            ]),
            h("div", { class:"flex flex-col gap-1" }, [
              h("label", { class:"text-[10px] text-gray-400 font-medium" }, "Other comments"),
              h("textarea", { class:"border border-gray-200 rounded-lg p-2 text-xs resize-none", rows:3, placeholder:"Additional remarks…" }),
            ]),
          ]),
        ]))
      ),
    ]);
  },
});

const convFactors = [
  { name:"Natural Gas",   ef:"0.0561" },
  { name:"Coal",          ef:"0.0961" },
  { name:"Propane",       ef:"0.0631" },
  { name:"LPG",           ef:"0.0561" },
  { name:"Diesel",        ef:"0.0741" },
  { name:"Petrol",        ef:"0.0693" },
  { name:"Fuel Oil",      ef:"0.0774" },
  { name:"Biomass",       ef:"0.0000" },
  { name:"Waste Tires",   ef:"0.0475" },
];
const unitConv = [
  { ind:"Production",       from:"kg",  to:"metric T", factor:"0.001" },
  { ind:"Production",       from:"lb",  to:"metric T", factor:"0.000454" },
  { ind:"Energy (electric)",from:"MWh", to:"GJ",       factor:"3.6" },
  { ind:"Energy (electric)",from:"TJ",  to:"GJ",       factor:"1000" },
  { ind:"Waste",            from:"kg",  to:"metric T", factor:"0.001" },
];
</script>