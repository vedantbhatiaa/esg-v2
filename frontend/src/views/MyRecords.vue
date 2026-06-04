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
          class="h-8 px-4 bg-navy text-white rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50">
          {{ saving ? "Saving…" : "💾 Submit & Save" }}
        </button>
      </div>
    </div>

    <div v-if="saveMsg" class="mb-3 px-4 py-2.5 rounded-lg text-sm border"
      :class="saveOk ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-100 text-red-600'">
      {{ saveMsg }}
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 overflow-x-auto mb-3">
      <button v-for="tab in TABS" :key="tab.id" @click="activeTab=tab.id"
        class="px-4 py-2.5 text-xs font-medium border-b-2 whitespace-nowrap transition-colors"
        :class="activeTab===tab.id ? 'border-navy text-navy font-semibold' : 'border-transparent text-gray-400 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Main Data tab -->
    <div v-if="activeTab==='main'">
      <div v-if="loading" class="py-8 text-center text-sm text-gray-400">Loading records…</div>
      <div v-else-if="!apiRows.length" class="py-8 text-center text-sm text-gray-400">
        No data found. Submit your first report via Submit Data.
      </div>
      <template v-else>
        <div class="text-xs text-gray-400 mb-2">
          ℹ Blue = company input · grey italic = auto-calculated
        </div>
        <div class="overflow-x-auto rounded-xl border border-gray-100">
          <table class="w-full text-xs border-collapse">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100 sticky left-0 bg-gray-50 min-w-44">Indicator</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Unit</th>
                <th v-for="y in allYears" :key="y"
                  class="px-3 py-2.5 text-right text-[9px] font-bold uppercase tracking-wider border-b border-gray-100 min-w-16"
                  :class="y===selYear ? 'text-navy bg-blue-50' : 'text-gray-400'">{{ y }}</th>
                <th class="px-3 py-2.5 text-right text-[9px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-100">YoY %</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="row in apiRows" :key="row.label">
                <tr v-if="row.section" class="border-b border-green-100">
                  <td :colspan="allYears.length + 3"
                    class="px-4 py-2 text-[10px] font-extrabold uppercase tracking-wider"
                    style="background:#E8F5F0;color:#065F46;border-top:2px solid #6EE7B7">
                    ▸ {{ row.section_label || row.label }}
                  </td>
                </tr>
                <tr v-else class="border-b border-gray-50 hover:bg-gray-50">
                  <td class="px-4 py-1.5 font-medium text-gray-700 sticky left-0 bg-white">{{ row.label }}</td>
                  <td class="px-3 py-1.5 text-gray-400 whitespace-nowrap">{{ row.unit }}</td>
                  <td v-for="y in allYears" :key="y"
                    class="px-3 py-1.5 text-right tabular-nums"
                    :class="{
                      'bg-blue-50 text-blue-700 font-semibold': y===selYear && row.type==='input',
                      'bg-indigo-50 text-indigo-600 italic':    y===selYear && row.type==='formula',
                      'text-gray-400 italic':                   y!==selYear && row.type==='formula',
                      'text-gray-600':                          y!==selYear && row.type==='input',
                    }">
                    {{ row.values?.[String(y)] || '—' }}
                  </td>
                  <td class="px-3 py-1.5 text-right text-xs font-semibold"
                    :class="yoyClass(row.yoy)">{{ row.yoy || '—' }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <!-- Legend -->
        <div class="flex gap-4 px-4 py-3 bg-gray-50 border-t border-gray-100 flex-wrap text-[10px] text-gray-500 rounded-b-xl">
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-blue-50 border border-blue-200 inline-block"></span>Company input (selected year)</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-indigo-50 border border-indigo-200 inline-block"></span>Auto-calculated (selected year)</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-white border border-gray-200 inline-block"></span>Historical</span>
        </div>
      </template>
    </div>

    <!-- Conversion Tables tab -->
    <div v-if="activeTab==='conversion'" class="grid grid-cols-2 gap-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 text-sm font-semibold">Emission Factors</div>
        <table class="w-full text-xs">
          <thead><tr class="bg-gray-50">
            <th class="px-4 py-2 text-left text-[9px] text-gray-400 uppercase">Fuel</th>
            <th class="px-4 py-2 text-right text-[9px] text-gray-400 uppercase">T.CO₂/GJ</th>
          </tr></thead>
          <tbody>
            <tr v-for="ef in EF_TABLE" :key="ef.fuel" class="border-t border-gray-50">
              <td class="px-4 py-2 text-gray-700">{{ ef.fuel }}</td>
              <td class="px-4 py-2 text-right tabular-nums text-gray-700">{{ ef.ef }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 text-sm font-semibold">Unit Conversions</div>
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
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";

const auth = useAuthStore();
const TABS = [
  { id:"main",       label:"Main Data Input" },
  { id:"conversion", label:"Conversion Tables" },
];
const activeTab    = ref("main");
const selYear      = ref(2023);
const availableYears = ref([2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009]);
const loading      = ref(false);
const saving       = ref(false);
const saveMsg      = ref(""); const saveOk = ref(false);

// Data from get_my_records
const apiRows      = ref([]);    // [{section?, label, unit, type, values:{yr:val}, yoy}]
const allYears     = ref([]);
const rawDataCache = ref({});    // { year: { ...raw fields } } for the save operation

function yoyClass(yoy) {
  if (!yoy || yoy === "—") return "text-gray-400";
  const n = parseFloat(yoy);
  return n < 0 ? "text-green-600 font-medium" : "text-red-500 font-medium";
}

async function loadData() {
  loading.value = true;
  try {
    const data = await api.getMyRecords(auth.companyName, selYear.value);
    if (data?.available_years?.length) {
      availableYears.value = data.available_years.slice().sort((a,b)=>b-a);
      if (!availableYears.value.includes(selYear.value))
        selYear.value = availableYears.value[0];
    }
    allYears.value = (data?.all_years || [selYear.value]).sort((a,b)=>a-b);

    // Build rows with section headers injected
    if (data?.rows) {
      let lastSection = "";
      const built = [];
      for (const row of data.rows) {
        if (row.section && row.section !== lastSection) {
          built.push({ section: true, section_label: row.section, label: row.section });
          lastSection = row.section;
        }
        built.push(row);
      }
      apiRows.value = built;
    }
  } catch(e) {
    console.error("MyRecords load:", e);
  } finally {
    loading.value = false;
  }
}

async function saveData() {
  // Re-submit data for selected year using what's cached from the form
  saving.value = true;
  saveMsg.value = "";
  try {
    // We don't have an editable form here — this is view-only with save button
    // In production this would submit edits; for now notify user to use Submit Data
    saveOk.value = true;
    saveMsg.value = "✅ Records are read-only here. Use Submit Data to update your figures.";
  } catch(e) {
    saveOk.value = false;
    saveMsg.value = `Save failed: ${e.message}`;
  } finally {
    saving.value = false;
    setTimeout(() => saveMsg.value = "", 5000);
  }
}

const EF_TABLE = [
  { fuel:"Natural Gas", ef:"0.0561" }, { fuel:"Coal", ef:"0.0961" }, { fuel:"Propane", ef:"0.0631" },
  { fuel:"Fuel Oil", ef:"0.0774" }, { fuel:"Diesel", ef:"0.0741" }, { fuel:"Petrol", ef:"0.0693" },
  { fuel:"Biomass", ef:"0.0" }, { fuel:"Waste Tires", ef:"0.0475 (×36.23 GJ/T)" }, { fuel:"LPG", ef:"0.0561" }, { fuel:"Other", ef:"0.0719" },
];
const UNIT_TABLE = [
  { from:"kg", to:"metric T", factor:"0.001" }, { from:"lb", to:"metric T", factor:"0.000454" },
  { from:"MWh", to:"GJ", factor:"3.6" }, { from:"TJ", to:"GJ", factor:"1000" }, { from:"m³", to:"m³", factor:"1.0" },
];

onMounted(loadData);
watch(selYear, loadData);
</script>