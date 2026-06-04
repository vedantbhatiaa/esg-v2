<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-bold text-gray-900">AI Assistant — Readiness Check</h2>
      <p class="text-sm text-gray-400 mt-0.5">Live data readiness scoring for any company & year</p>
    </div>

    <!-- Selectors -->
    <div class="flex gap-3 mb-5">
      <select v-model="selCompany" class="h-9 border border-gray-200 rounded-lg px-3 text-sm bg-white min-w-48">
        <option v-for="c in companies" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="selYear" class="h-9 border border-gray-200 rounded-lg px-3 text-sm bg-white">
        <option v-for="y in availYears" :key="y" :value="y">{{ y }}</option>
      </select>
      <div v-if="loading" class="text-sm text-gray-400 self-center">Loading…</div>
    </div>

    <div class="grid grid-cols-3 gap-4 mb-5">
      <!-- Score gauge -->
      <div class="bg-white border border-gray-100 rounded-xl p-5 flex flex-col items-center">
        <div class="relative w-32 h-32 mb-3">
          <svg viewBox="0 0 120 120" class="w-full h-full -rotate-90">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#F1F5F9" stroke-width="10"/>
            <circle cx="60" cy="60" r="50" fill="none"
              :stroke="scoreColor" stroke-width="10" stroke-linecap="round"
              :stroke-dasharray="`${score*3.14} 314`"
              style="transition:stroke-dasharray 1s ease"/>
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center rotate-90">
            <div class="text-3xl font-black" :style="{color:scoreColor}">{{ score }}</div>
            <div class="text-xs text-gray-400">/100</div>
          </div>
        </div>
        <div class="text-sm font-bold" :style="{color:scoreColor}">{{ scoreLabel }}</div>
        <div class="text-xs text-gray-400 text-center mt-1">{{ selCompany }} · {{ selYear }}</div>
      </div>

      <!-- KPI grid -->
      <div class="col-span-2 bg-white border border-gray-100 rounded-xl p-5">
        <div class="text-sm font-semibold text-gray-700 mb-3">Key Performance Indicators</div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="k in kpiCards" :key="k.label" class="flex justify-between items-center bg-gray-50 rounded-lg px-3 py-2">
            <span class="text-xs text-gray-500">{{ k.label }}</span>
            <span class="text-sm font-bold" :style="{color:k.color}">{{ k.value }}</span>
          </div>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2">
          <div v-for="f in flagSummary" :key="f.label" class="text-center py-2 rounded-lg"
            :class="f.cls">
            <div class="text-lg font-bold">{{ f.count }}</div>
            <div class="text-[10px]">{{ f.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Completeness bars -->
    <div class="bg-white border border-gray-100 rounded-xl p-5 mb-5">
      <div class="text-sm font-semibold text-gray-700 mb-3">Data Completeness by Section</div>
      <div class="grid grid-cols-3 gap-3">
        <div v-for="s in sectionCompleteness" :key="s.label">
          <div class="flex justify-between mb-1">
            <span class="text-xs text-gray-500">{{ s.label }}</span>
            <span class="text-xs font-semibold" :class="s.pct===100?'text-green-600':s.pct>=60?'text-amber-600':'text-red-500'">{{ s.pct }}%</span>
          </div>
          <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-700"
              :style="{width:s.pct+'%',background:s.pct===100?'#16A34A':s.pct>=60?'#F59E0B':'#EF4444'}"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Flags -->
    <div class="bg-white border border-gray-100 rounded-xl p-5 mb-5">
      <div class="text-sm font-semibold text-gray-700 mb-3">Validation Flags</div>
      <div class="space-y-2">
        <div v-for="(f, i) in flags" :key="i"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg border text-sm"
          :class="f.severity==='error'?'bg-red-50 border-red-200 text-red-700':f.severity==='warning'?'bg-yellow-50 border-yellow-200 text-yellow-700':'bg-green-50 border-green-200 text-green-700'">
          <span class="text-base">{{ f.severity==='error'?'✕':f.severity==='warning'?'!':'✓' }}</span>
          <span class="font-medium">{{ f.message }}</span>
          <span v-if="f.detail" class="text-xs opacity-70">· {{ f.detail }}</span>
        </div>
      </div>
    </div>

    <!-- AI Mock insight -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-100">
        <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        <span class="text-sm font-semibold">dss+ AI Analyst</span>
        <span class="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full border border-green-200">AI-Assisted</span>
      </div>
      <div class="p-4 text-sm text-gray-600 leading-relaxed">
        <span v-if="insight">{{ insight }}</span>
        <span v-else-if="loading" class="text-gray-400 italic">Generating insight…</span>
        <span v-else class="text-gray-400 italic">Select a company and year to generate an AI readiness insight.</span>
        <p class="mt-3 text-xs text-gray-400 italic">Note: All insights are AI-generated and require analyst review before use.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import api from "@/services/api.js";

const selCompany = ref("");
const selYear    = ref(2023);
const companies  = ref([]);
const availYears = ref([2023,2022,2021,2020,2019,2018,2017,2016,2015]);
const loading    = ref(false);
const kpis       = ref(null);
const flags      = ref([]);
const insight    = ref("");

const C = { navy:"#0A2240", co2:"#475569", energy:"#F59E0B", water:"#0891B2", renew:"#16A34A", waste:"#7C3AED" };

const score = computed(() => {
  if (!kpis.value) return 0;
  const k = kpis.value;
  const fields = [k.total_electricity, k.production, k.water_kpi, k.energy_kpi, k.co2_kpi, k.waste_recovery_pct];
  const filled = fields.filter(v=>v!=null&&v>0).length;
  const base = Math.round(filled/fields.length * 100);
  const errs = flags.value.filter(f=>f.severity==="error").length;
  const warns = flags.value.filter(f=>f.severity==="warning").length;
  return Math.max(0, Math.min(100, base - errs*10 - warns*3));
});

const scoreLabel = computed(() => score.value>=90?"Ready":score.value>=70?"Review Required":"Not Ready");
const scoreColor = computed(() => score.value>=80?"#16A34A":score.value>=60?"#F59E0B":"#DC2626");

const flagSummary = computed(() => {
  const errs  = flags.value.filter(f=>f.severity==="error").length;
  const warns = flags.value.filter(f=>f.severity==="warning").length;
  const ok    = flags.value.filter(f=>f.severity==="ok").length;
  return [
    { label:"Errors",   count:errs,  cls:"bg-red-50 text-red-600" },
    { label:"Warnings", count:warns, cls:"bg-yellow-50 text-yellow-700" },
    { label:"Passed",   count:ok,    cls:"bg-green-50 text-green-700" },
  ];
});

const kpiCards = computed(() => {
  if (!kpis.value) return [];
  const k = kpis.value;
  return [
    { label:"CO₂ KPI",    value:(k.co2_kpi||0).toFixed(3)+" T/T",    color:C.co2    },
    { label:"Energy KPI", value:(k.energy_kpi||0).toFixed(2)+" GJ/T", color:C.energy },
    { label:"Water KPI",  value:(k.water_kpi||0).toFixed(2)+" m³/T",  color:C.water  },
    { label:"Renewable",  value:(k.renew_share_pct||0).toFixed(1)+"%",color:C.renew  },
    { label:"Waste Rec.", value:k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1)+"%":"—", color:C.waste },
    { label:"ISO 14001",  value:k.pct_certified?(k.pct_certified*100).toFixed(0)+"%":"—", color:C.navy },
  ];
});

const sectionCompleteness = computed(() => {
  if (!kpis.value) return [];
  const k = kpis.value;
  return [
    { label:"ISO 14001",        pct: k.pct_certified>0?100:0 },
    { label:"Production",       pct: k.total_energy>0?100:0 },
    { label:"Water",            pct: k.water_kpi>0?100:0 },
    { label:"Energy (Elec.)",   pct: k.total_electricity>0?100:0 },
    { label:"CO₂ Scope 1",      pct: k.total_co2_scope1>0?100:0 },
    { label:"CO₂ Scope 2",      pct: k.total_co2_scope2>0?100:0 },
    { label:"Waste",            pct: k.waste_recovery_pct>0?100:0 },
    { label:"Renewable Elec.",  pct: k.renew_share_pct>0?100:0 },
    { label:"Pathway 3 (SBTi)", pct: 0 },
  ];
});

function buildInsight() {
  if (!kpis.value || !selCompany.value) return;
  const k = kpis.value;
  const co2 = (k.co2_kpi||0).toFixed(3);
  const e   = (k.energy_kpi||0).toFixed(2);
  const w   = (k.water_kpi||0).toFixed(2);
  const wr  = k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1):0;
  const re  = (k.renew_share_pct||0).toFixed(1);
  const s   = score.value;
  insight.value = `${selCompany.value} ${selYear.value} submission has a readiness score of ${s}/100 (${scoreLabel.value}). ` +
    `Key KPIs: CO₂ intensity ${co2} T.CO₂/T, Energy intensity ${e} GJ/T, Water intensity ${w} m³/T. ` +
    `Renewable electricity share is ${re}% and waste recovery rate is ${wr}%. ` +
    (s>=80 ? "Submission appears complete and ready for consolidation. Minor analyst review recommended." :
     s>=60 ? "Submission requires review. Address open flags before inclusion in the consolidated report." :
             "Significant data gaps detected. Return to client for completion before proceeding.");
}

async function loadCompanies() {
  try {
    const res = await api.getCompanies();
    companies.value = Array.isArray(res) ? res : (res?.companies || []);
    if (companies.value.length) { selCompany.value = companies.value[0]; await loadData(); }
  } catch(e) {}
}

async function loadData() {
  if (!selCompany.value) return;
  loading.value = true;
  kpis.value = null; flags.value = []; insight.value = "";
  try {
    const res = await api.getCompanyData(selCompany.value, selYear.value);
    if (res?.kpis)  kpis.value  = res.kpis;
    if (res?.flags) flags.value = res.flags;
    if (res?.years) availYears.value = res.years.slice().sort((a,b)=>b-a);
    buildInsight();
  } catch(e) {}
  finally { loading.value = false; }
}

onMounted(loadCompanies);
watch([selCompany, selYear], loadData);
</script>