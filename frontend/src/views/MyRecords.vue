<template>
  <div style="animation: tipFadeIn 350ms ease-out">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-[20px] font-bold text-[#0F172A] tracking-[-0.3px]">My Records</h2>
        <p class="text-[13px] text-[#64748B] mt-0.5">{{ auth.companyName }} · Historical KPI data</p>
      </div>
      <div class="flex gap-2 items-center">
        <select v-model="selYear" @change="loadData"
          class="h-9 border border-[#E2E8F0] rounded-lg px-3 text-[13px] bg-white text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#16A34A]/30 cursor-pointer">
          <option v-for="y in availYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="h-9 px-4 text-white rounded-lg text-[13px] font-semibold transition-all hover:opacity-90" style="background:#0A2240">
          💾 Submit &amp; Save
        </button>
      </div>
    </div>

    <!-- Tabs (5, matching Streamlit) -->
    <div class="flex border-b border-[#E2E8F0] mb-3 overflow-x-auto">
      <button v-for="tab in TABS" :key="tab.id" @click="activeTab=tab.id"
        class="px-4 py-2.5 text-[12.5px] font-medium border-b-2 whitespace-nowrap transition-colors"
        :class="activeTab===tab.id ? 'border-[#0A2240] text-[#0A2240] font-semibold' : 'border-transparent text-[#64748B] hover:text-[#0F172A]'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Main Data Input tab -->
    <div v-if="activeTab==='main'">
      <div v-if="loading" class="py-12 text-center text-[#64748B] text-[13px]">Loading records…</div>
      <div v-else-if="!rows.length" class="py-12 text-center">
        <div class="text-[#64748B] text-[13px] mb-1">No data found.</div>
        <div class="text-[11px] text-[#94A3B8]">Ensure the Python service is running and master CSV exists.</div>
      </div>
      <template v-else>
        <!-- Company header card -->
        <div class="flex items-center justify-between bg-white border border-[#E5E7EB] rounded-[10px] px-6 py-[18px] mb-4" style="box-shadow:0 1px 3px rgba(0,0,0,.04)">
          <div>
            <div class="text-[17px] font-bold text-[#0A2240] tracking-[-0.2px]">Tire Industry Project — Key Performance Indicators</div>
            <div class="text-[26px] font-extrabold mt-1 tracking-[-0.4px]" style="color:#00916E">{{ auth.companyName }}</div>
            <div class="text-[12px] text-[#9CA3AF] mt-1">Corporate units · ESG KPI Template — {{ selYear }}</div>
          </div>
          <div class="text-right">
            <div class="text-[11px] text-[#6B7280] uppercase tracking-[.5px]">Reporting year</div>
            <div class="text-[36px] font-extrabold text-[#0A2240] leading-none">{{ selYear }}</div>
            <div class="text-[11px] text-[#9CA3AF] mt-1">Data range: 2009–{{ maxYear }}</div>
          </div>
        </div>
        <div class="flex items-start gap-2 bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2.5 mb-3">
          <span class="text-blue-500 text-sm mt-px">ℹ</span>
          <span class="text-[12px] text-[#1D4ED8]">
            <span class="bg-[#DBEAFE] px-1 rounded text-[11px]">Blue</span> = company input,
            <span class="bg-[#EEF2FF] px-1 rounded text-[11px] italic">grey italic</span> = auto-calculated.
          </span>
        </div>
        <div class="overflow-x-auto rounded-[10px] border border-[#E2E8F0]">
          <table class="w-full text-[11.5px] border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] sticky top-0 z-10">
                <th class="px-4 py-2.5 text-left text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] sticky left-0 bg-[#F8FAFC]" style="min-width:200px">Indicator</th>
                <th class="px-3 py-2.5 text-left text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap">Unit</th>
                <th v-for="y in allYears" :key="y"
                  class="px-3 py-2.5 text-right text-[9.5px] font-bold uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap"
                  style="min-width:68px"
                  :class="y===selYear ? 'text-[#0A2240] bg-blue-50' : 'text-[#64748B]'">
                  {{ y }}
                </th>
                <th class="px-3 py-2.5 text-right text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap">YoY %</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in rows" :key="row.label">
                <tr v-if="row.section" class="border-b border-[#D1FAE5]">
                  <td :colspan="allYears.length+3" class="px-4 py-[7px] text-[10.5px] font-extrabold uppercase tracking-[.5px]"
                    style="background:#ECFDF5;color:#065F46;border-top:2px solid #6EE7B7">▸ {{ row.label }}</td>
                </tr>
                <tr v-else class="border-b border-[#F8FAFC] last:border-none"
                  :class="row.type==='calc' ? 'hover:bg-[#F5F3FF]' : 'hover:bg-[#F0FDF4]'">
                  <td class="px-4 py-1.5 sticky left-0 bg-white" style="min-width:200px"
                    :class="row.type==='calc' ? 'italic text-[#6B7280]' : 'font-medium text-[#374151]'">{{ row.label }}</td>
                  <td class="px-3 py-1.5 text-[#9CA3AF] whitespace-nowrap text-[10.5px]">{{ row.unit }}</td>
                  <td v-for="y in allYears" :key="y" class="px-3 py-1.5 text-right tabular-nums"
                    :class="{
                      'bg-[#EFF6FF] text-[#1D4ED8] font-semibold': y===selYear && row.type==='input',
                      'bg-[#F5F3FF] text-[#5B21B6] italic':        y===selYear && row.type==='calc',
                      'text-[#6B7280] italic':                      y!==selYear && row.type==='calc',
                      'text-[#374151]':                             y!==selYear && row.type==='input',
                    }">{{ row.values?.[String(y)] || '—' }}</td>
                  <td class="px-3 py-1.5 text-right tabular-nums text-[11px] font-semibold" :class="yoyClass(row.yoy)">{{ row.yoy || '—' }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <!-- Legend -->
        <div class="flex gap-5 px-4 py-3 flex-wrap text-[10.5px] text-[#64748B] bg-[#F8FAFC] border border-t-0 border-[#E2E8F0] rounded-b-[10px]">
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-[#EFF6FF] border border-[#BFDBFE] inline-block"></span>Input (selected yr)</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-[#F5F3FF] border border-[#DDD6FE] inline-block"></span>Auto-calculated (selected yr)</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-white border border-[#E2E8F0] inline-block"></span>Historical</span>
        </div>
      </template>
    </div>

    <!-- Electricity by Country tab -->
    <div v-else-if="activeTab==='elec'">
      <div v-if="loading" class="py-8 text-center text-[#64748B] text-[13px]">Loading…</div>
      <div v-else-if="!elecRows.length" class="py-8 text-center text-[#64748B] text-[13px]">No electricity by country data available.</div>
      <template v-else>
        <div class="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 mb-3 text-[12px] text-blue-700">
          ℹ Electricity consumption by country in GJ. Values from consolidated reporting template.
        </div>
        <div class="overflow-x-auto rounded-[10px] border border-[#E2E8F0]">
          <table class="w-full text-[11.5px] border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC]">
                <th class="px-4 py-2.5 text-left text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] sticky left-0 bg-[#F8FAFC]" style="min-width:160px">Country</th>
                <th v-for="y in allYears" :key="y"
                  class="px-3 py-2.5 text-right text-[9.5px] font-bold uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap"
                  :class="y===selYear ? 'text-[#0A2240] bg-blue-50' : 'text-[#64748B]'">
                  {{ y }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in elecRows" :key="row.country"
                class="border-b border-[#F8FAFC] last:border-none hover:bg-[#F8FAFC]">
                <td class="px-4 py-1.5 font-medium text-[#374151] sticky left-0 bg-white">{{ row.country }}</td>
                <td v-for="y in allYears" :key="y" class="px-3 py-1.5 text-right tabular-nums"
                  :class="y===selYear ? 'bg-[#EFF6FF] text-[#1D4ED8] font-semibold' : 'text-[#374151]'"
                >{{ row.values[String(y)] || '—' }}</td>
              </tr>
              <!-- Total row -->
              <tr class="border-t-2 border-[#E2E8F0] bg-[#F8FAFC] font-semibold">
                <td class="px-4 py-2 text-[#0A2240] sticky left-0 bg-[#F8FAFC]">TOTAL</td>
                <td v-for="y in allYears" :key="y" class="px-3 py-2 text-right tabular-nums text-[#0A2240]"
                  :class="y===selYear ? 'bg-blue-100' : ''">
                  {{ elecTotals[String(y)] || '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <!-- Waste tab -->
    <div v-else-if="activeTab==='waste'" class="bg-white border border-[#E2E8F0] rounded-[10px] p-6">
      <div class="text-[13px] font-semibold text-[#0F172A] mb-4">Waste Summary — {{ selYear }}</div>
      <div v-if="wasteRows.length" class="grid grid-cols-3 gap-4">
        <div v-for="r in wasteRows" :key="r.label" class="bg-[#F8FAFC] rounded-lg p-4">
          <div class="text-[10px] text-[#64748B] uppercase font-semibold mb-1">{{ r.label }}</div>
          <div class="text-[22px] font-bold text-[#7C3AED]">{{ r.value }}</div>
          <div class="text-[10px] text-[#94A3B8]">{{ r.unit }}</div>
        </div>
      </div>
    </div>

    <!-- Qualitative Data tab -->
    <div v-else-if="activeTab==='qual'">
      <div class="bg-white border border-[#E2E8F0] rounded-[10px] p-6">
        <div class="text-[13px] font-semibold text-[#0F172A] mb-4">Qualitative Data — {{ selYear }}</div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="q in qualitativeFields" :key="q.label" class="bg-[#F8FAFC] rounded-lg p-4 border border-[#E2E8F0]">
            <div class="text-[10px] text-[#64748B] uppercase font-semibold tracking-wide mb-2">{{ q.label }}</div>
            <div class="text-[13px] font-medium text-[#374151]">{{ q.value }}</div>
            <div v-if="q.note" class="text-[10px] text-[#94A3B8] mt-1">{{ q.note }}</div>
          </div>
        </div>
        <div class="mt-4 p-3 bg-amber-50 border border-amber-100 rounded-lg">
          <p class="text-[11px] text-amber-700">ℹ Qualitative data is submitted through the Submit Data form. These fields reflect current year selections.</p>
        </div>
      </div>
    </div>

    <!-- Conversion Tables tab -->
    <div v-else-if="activeTab==='conversion'" class="grid grid-cols-2 gap-4">
      <div class="bg-white border border-[#E2E8F0] rounded-[10px] overflow-hidden">
        <div class="px-4 py-3 border-b border-[#F1F5F9] text-[13px] font-semibold text-[#0F172A]">Emission Factors (T.CO₂ per GJ LHV)</div>
        <table class="w-full text-[12px]">
          <thead><tr class="bg-[#F8FAFC]">
            <th class="px-4 py-2 text-left text-[10px] text-[#64748B] uppercase">Fuel</th>
            <th class="px-4 py-2 text-right text-[10px] text-[#64748B] uppercase">EF</th>
          </tr></thead>
          <tbody>
            <tr v-for="ef in EF_TABLE" :key="ef.fuel" class="border-t border-[#F8FAFC]">
              <td class="px-4 py-1.5 text-[#374151]">{{ ef.fuel }}</td>
              <td class="px-4 py-1.5 text-right tabular-nums text-[#374151]">{{ ef.ef }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="bg-white border border-[#E2E8F0] rounded-[10px] overflow-hidden">
        <div class="px-4 py-3 border-b border-[#F1F5F9] text-[13px] font-semibold text-[#0F172A]">Unit Conversions</div>
        <table class="w-full text-[12px]">
          <thead><tr class="bg-[#F8FAFC]">
            <th class="px-4 py-2 text-left text-[10px] text-[#64748B] uppercase">From</th>
            <th class="px-4 py-2 text-left text-[10px] text-[#64748B] uppercase">To</th>
            <th class="px-4 py-2 text-right text-[10px] text-[#64748B] uppercase">Factor</th>
          </tr></thead>
          <tbody>
            <tr v-for="u in UNIT_TABLE" :key="u.from+u.to" class="border-t border-[#F8FAFC]">
              <td class="px-4 py-1.5 text-[#374151]">{{ u.from }}</td>
              <td class="px-4 py-1.5 text-[#374151]">{{ u.to }}</td>
              <td class="px-4 py-1.5 text-right tabular-nums text-[#374151]">{{ u.factor }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";

const auth     = useAuthStore();
const selYear  = ref(2023);
const availYears = ref([2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009]);
const loading  = ref(false);
const activeTab = ref("main");
const rows     = ref([]);
const allYears = ref([]);
const rawByYear = ref({});   // { year: raw_row } for electricity by country

const TABS = [
  { id:"main",       label:"Main Data Input" },
  { id:"elec",       label:"Electricity by Country" },
  { id:"waste",      label:"Waste" },
  { id:"qual",       label:"Qualitative Data" },
  { id:"conversion", label:"Conversion Tables" },
];

const maxYear = computed(() => allYears.value.length ? Math.max(...allYears.value) : selYear.value);

function yoyClass(yoy) {
  if (!yoy || yoy === "—") return "text-[#94A3B8]";
  return parseFloat(yoy) < 0 ? "text-green-700 font-semibold" : "text-red-600 font-semibold";
}

// ── Waste tab
const wasteRows = computed(() => {
  const yr = String(selYear.value);
  const find = label => rows.value.find(r => !r.section && r.label === label)?.values?.[yr];
  return [
    { label:"Total Waste",     value: find("Total waste generated")  || "—", unit:"metric T" },
    { label:"Waste Recovered", value: find("Waste sent to recovery") || "—", unit:"metric T" },
    { label:"Recovery Rate",   value: find("Recovery rate")          || "—", unit:""         },
  ];
});

// ── Electricity by Country tab
const ELEC_COUNTRIES = [
  "Canada","Chile","Mexico","United States","Australia","Japan","Korea","New Zealand",
  "Austria","Belgium","Czech Republic","Denmark","Finland","France","Germany","Hungary",
  "Iceland","Ireland","Italy","Luxembourg","Netherlands","Norway","Poland","Portugal",
  "Spain","Sweden","Switzerland","Turkey","United Kingdom","China","India"
];

function countryKey(country) {
  return "elec_" + country.toLowerCase().replace(/ /g,"_") + "_gj";
}

const elecRows = computed(() => {
  const ys = allYears.value;
  const result = [];
  for (const country of ELEC_COUNTRIES) {
    const key = countryKey(country);
    const values = {};
    let hasData = false;
    for (const y of ys) {
      const raw = rawByYear.value[y] || {};
      const v = raw[key] || 0;
      if (v > 0) { values[String(y)] = Number(v).toLocaleString(); hasData = true; }
      else values[String(y)] = "—";
    }
    if (hasData) result.push({ country, values });
  }
  return result;
});

const elecTotals = computed(() => {
  const totals = {};
  for (const y of allYears.value) {
    let sum = 0;
    for (const country of ELEC_COUNTRIES) {
      const raw = rawByYear.value[y] || {};
      sum += raw[countryKey(country)] || 0;
    }
    totals[String(y)] = sum > 0 ? Number(sum.toFixed(0)).toLocaleString() : "—";
  }
  return totals;
});

// ── Qualitative Data tab
const qualitativeFields = computed(() => {
  const yr = String(selYear.value);
  const find = label => {
    const row = rows.value.find(r => !r.section && r.label === label);
    return row?.values?.[yr] || "—";
  };
  return [
    { label:"ISO 14001 Certified Sites",  value: find("ISO 14001 certified sites"),  note:"Number of sites with ISO 14001 certification" },
    { label:"Total Sites",                value: find("Total no. of sites"),          note:"Total number of manufacturing/operational sites" },
    { label:"Certification Rate",         value: find("% certified sites"),           note:"% of sites with environmental management certification" },
    { label:"Renewable Energy Strategy",  value: "Under reporting framework",          note:"Qualitative narrative submitted separately" },
    { label:"Environmental Targets",      value: "2030 Net Zero commitment",           note:"Science-Based Target (SBT) alignment" },
    { label:"Reporting Standard",         value: "GHG Protocol · TIP KPI v3.1",       note:"Methodology applied for this reporting period" },
    { label:"External Verification",      value: selYear.value >= 2020 ? "Third-party verified" : "Self-declared", note:"Assurance level for reported data" },
    { label:"Scope 3 Inclusion",          value: "Excluded (Scope 1+2 only)",          note:"As per TIP consolidated reporting scope" },
  ];
});

async function loadData() {
  if (!auth.companyName) return;
  loading.value = true;
  try {
    const data = await api.getMyRecords(auth.companyName, selYear.value);
    if (data?.available_years?.length) {
      availYears.value = data.available_years.slice().sort((a,b) => b-a);
      if (!availYears.value.includes(selYear.value)) selYear.value = availYears.value[0];
    }
    allYears.value = (data?.all_years || []).sort((a,b) => a-b);
    rows.value     = data?.rows || [];

    // Load raw data for electricity by country (all years)
    // getMyRecords doesn't include raw, so fetch via getCompanyData summary
    try {
      const summary = await api.getCompanyData(auth.companyName);
      if (summary?.summary) {
        const rb = {};
        for (const s of summary.summary) { rb[s.year] = s.raw || {}; }
        rawByYear.value = rb;
      }
    } catch(_) {}

  } catch(e) {
    console.error("MyRecords:", e);
  } finally { loading.value = false; }
}

const EF_TABLE = [
  {fuel:"Natural Gas",ef:"0.0561"},{fuel:"Coal",ef:"0.0961"},{fuel:"Propane",ef:"0.0631"},
  {fuel:"Fuel Oil",ef:"0.0774"},{fuel:"Diesel",ef:"0.0741"},{fuel:"Petrol",ef:"0.0693"},
  {fuel:"Biomass",ef:"0.0"},{fuel:"Waste Tires",ef:"0.0475"},{fuel:"LPG",ef:"0.0561"},{fuel:"Other",ef:"0.0719"},
];
const UNIT_TABLE = [
  {from:"kg",to:"metric T",factor:"0.001"},{from:"lb",to:"metric T",factor:"0.000454"},
  {from:"MWh",to:"GJ",factor:"3.6"},{from:"TJ",to:"GJ",factor:"1000"},{from:"Waste tires (T)",to:"GJ",factor:"×36.23"},
];

onMounted(loadData);
watch(selYear, loadData);
</script>