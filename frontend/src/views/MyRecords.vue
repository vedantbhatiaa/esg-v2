<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-[20px] font-bold text-[#0F172A]">My Records</h2>
        <p class="text-[13px] text-[#64748B] mt-0.5">{{ auth.companyName }} · Historical KPI data</p>
      </div>
      <div class="flex gap-2 items-center">
        <select v-model="selYear" @change="loadData"
          class="h-9 border border-[#E2E8F0] rounded-lg px-3 text-sm bg-white text-[#0F172A] focus:outline-none">
          <option v-for="y in availYears" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="h-9 px-4 bg-[#0A2240] text-white rounded-lg text-sm font-semibold hover:bg-[#1a3560] transition-colors">
          💾 Submit &amp; Save
        </button>
      </div>
    </div>

    <!-- Tabs (5 tabs like Streamlit) -->
    <div class="flex border-b border-[#E2E8F0] mb-3 overflow-x-auto">
      <button v-for="tab in TABS" :key="tab.id" @click="activeTab=tab.id"
        class="px-4 py-2.5 text-[12.5px] font-medium border-b-2 whitespace-nowrap transition-colors"
        :class="activeTab===tab.id
          ? 'border-[#0A2240] text-[#0A2240] font-semibold'
          : 'border-transparent text-[#64748B] hover:text-[#0F172A]'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Main Data Input tab -->
    <div v-if="activeTab==='main'">
      <div v-if="loading" class="py-12 text-center text-[#64748B] text-sm">Loading records…</div>
      <div v-else-if="!apiRows.length" class="py-12 text-center text-[#64748B] text-sm">
        No data found. Submit your first report via Submit Data.<br>
        <span class="text-[11px] text-[#94A3B8]">Ensure the Python service is running and master CSV exists.</span>
      </div>
      <template v-else>
        <!-- Header card (matches Streamlit render_template_table header) -->
        <div class="flex items-center justify-between bg-white border border-[#E5E7EB] rounded-[10px] px-6 py-[18px] mb-4">
          <div>
            <div class="text-[17px] font-bold text-[#0A2240] tracking-[-0.2px]">
              Tire Industry Project — Key Performance Indicators
            </div>
            <div class="text-[26px] font-extrabold text-[#00916E] mt-1 tracking-[-0.4px]">
              {{ auth.companyName }}
            </div>
            <div class="text-[12px] text-[#9CA3AF] mt-1">Corporate units · ESG KPI Template — {{ selYear }}</div>
          </div>
          <div class="text-right">
            <div class="text-[11px] text-[#6B7280] uppercase tracking-[.5px]">Reporting year</div>
            <div class="text-[36px] font-extrabold text-[#0A2240] leading-none">{{ selYear }}</div>
            <div class="text-[11px] text-[#9CA3AF] mt-1">Data range: 2009–{{ selYear }}</div>
          </div>
        </div>

        <div class="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 text-[12px] text-blue-700 mb-3">
          ℹ Template generated from your inputs. Blue cells = company input, grey italic = auto-calculated formula.
        </div>

        <!-- Template table -->
        <div class="overflow-x-auto rounded-[10px] border border-[#E2E8F0]">
          <table class="w-full text-[11.5px] border-collapse">
            <thead>
              <tr class="bg-[#F8FAFC] sticky top-0 z-10">
                <th class="px-4 py-2.5 text-left text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] sticky left-0 bg-[#F8FAFC] min-w-[200px]">
                  Indicator
                </th>
                <th class="px-3 py-2.5 text-left text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap">Unit</th>
                <th v-for="y in allYears" :key="y"
                  class="px-3 py-2.5 text-right text-[9.5px] font-bold uppercase tracking-[.4px] border-b border-[#E2E8F0] min-w-[72px] whitespace-nowrap"
                  :class="y===selYear ? 'text-[#0A2240] bg-blue-50' : 'text-[#64748B]'">
                  {{ y }}
                </th>
                <th class="px-3 py-2.5 text-right text-[9.5px] font-bold text-[#64748B] uppercase tracking-[.4px] border-b border-[#E2E8F0] whitespace-nowrap">YoY %</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in apiRows" :key="row.label">
                <!-- Section header rows (green) -->
                <tr v-if="row.section" class="border-b border-[#D1FAE5]">
                  <td :colspan="allYears.length+3"
                    class="px-4 py-2 text-[10.5px] font-extrabold uppercase tracking-[.5px]"
                    style="background:#ECFDF5;color:#065F46;border-top:2px solid #6EE7B7">
                    ▸ {{ row.label }}
                  </td>
                </tr>
                <!-- Data rows -->
                <tr v-else
                  class="border-b border-[#F8FAFC] last:border-none"
                  :class="row.type==='calc' ? 'hover:bg-[#EEF2FF]' : 'hover:bg-[#F0FDF4]'">
                  <td class="px-4 py-1.5 sticky left-0 bg-white font-medium"
                    :class="row.type==='calc' ? 'italic text-[#6B7280]' : 'text-[#374151]'"
                    style="min-width:200px">
                    {{ row.label }}
                  </td>
                  <td class="px-3 py-1.5 text-[#9CA3AF] whitespace-nowrap">{{ row.unit }}</td>
                  <td v-for="y in allYears" :key="y"
                    class="px-3 py-1.5 text-right tabular-nums"
                    :class="{
                      'bg-[#EFF6FF] text-[#1D4ED8] font-semibold':   y===selYear && row.type==='input',
                      'bg-[#EEF2FF] text-[#4F46E5] italic':          y===selYear && row.type==='calc',
                      'text-[#6B7280] italic':                        y!==selYear && row.type==='calc',
                      'text-[#374151]':                              y!==selYear && row.type==='input',
                    }">
                    {{ row.values?.[String(y)] || '—' }}
                  </td>
                  <td class="px-3 py-1.5 text-right tabular-nums text-[11px] font-semibold"
                    :class="yoyClass(row.yoy)">
                    {{ row.yoy || '—' }}
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <!-- Legend -->
        <div class="flex gap-5 px-4 py-3 bg-[#F8FAFC] border-t border-[#E2E8F0] flex-wrap text-[10.5px] text-[#64748B] rounded-b-[10px] border border-t-0 border-[#E2E8F0]">
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-[#EFF6FF] border border-[#BFDBFE] inline-block"></span>
            Company input (selected year)
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-[#EEF2FF] border border-[#C7D2FE] inline-block"></span>
            Auto-calculated (selected year)
          </span>
          <span class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-white border border-[#E2E8F0] inline-block"></span>
            Historical
          </span>
        </div>
      </template>
    </div>

    <!-- Conversion Tables tab -->
    <div v-if="activeTab==='conversion'" class="grid grid-cols-2 gap-4">
      <div class="bg-white border border-[#E2E8F0] rounded-[10px] overflow-hidden">
        <div class="px-4 py-3 border-b border-[#F1F5F9] text-[13px] font-semibold">Emission Factors (T.CO₂/GJ LHV)</div>
        <table class="w-full text-[12px]">
          <thead><tr class="bg-[#F8FAFC]">
            <th class="px-4 py-2 text-left text-[10px] text-[#64748B] uppercase">Fuel</th>
            <th class="px-4 py-2 text-right text-[10px] text-[#64748B] uppercase">EF (T.CO₂/GJ)</th>
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
        <div class="px-4 py-3 border-b border-[#F1F5F9] text-[13px] font-semibold">Unit Conversions</div>
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
import { ref, watch, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";

const auth     = useAuthStore();
const selYear  = ref(2023);
const availYears = ref([2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009]);
const loading  = ref(false);
const activeTab = ref("main");
const apiRows  = ref([]);
const allYears = ref([]);

const TABS = [
  { id:"main",       label:"Main Data Input" },
  { id:"elec",       label:"Electricity by Country" },
  { id:"waste",      label:"Waste" },
  { id:"qual",       label:"Qualitative Data" },
  { id:"conversion", label:"Conversion Tables" },
];

function yoyClass(yoy) {
  if (!yoy || yoy==="—") return "text-[#94A3B8]";
  return parseFloat(yoy) < 0 ? "text-green-700" : "text-red-600";
}

async function loadData() {
  if (!auth.companyName) return;
  loading.value = true;
  try {
    const data = await api.getMyRecords(auth.companyName, selYear.value);
    if (data?.available_years?.length) {
      availYears.value = data.available_years.slice().sort((a,b)=>b-a);
      if (!availYears.value.includes(selYear.value))
        selYear.value = availYears.value[0];
    }
    allYears.value = (data?.all_years || []).sort((a,b)=>a-b);
    apiRows.value  = data?.rows || [];
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
  {from:"MWh",to:"GJ",factor:"3.6"},{from:"TJ",to:"GJ",factor:"1000"},
  {from:"Waste tires",to:"GJ",factor:"×36.23"},
];

onMounted(loadData);
watch(selYear, loadData);
</script>