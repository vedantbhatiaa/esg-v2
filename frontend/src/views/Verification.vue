<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-bold text-gray-900">Verification Queue</h2>
      <p class="text-sm text-gray-400 mt-0.5">Review and verify company submissions</p>
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

    <!-- Summary metrics -->
    <div class="grid grid-cols-5 gap-3 mb-5">
      <div class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-xs text-gray-400 mb-0.5">Company</div>
        <div class="text-sm font-bold text-navy truncate">{{ selCompany || '—' }}</div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-xs text-gray-400 mb-0.5">Year</div>
        <div class="text-sm font-bold text-navy">{{ selYear }}</div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-xs text-gray-400 mb-0.5">Completeness</div>
        <div class="text-sm font-bold" :class="avgComplete>=80?'text-green-600':'text-amber-600'">{{ avgComplete }}%</div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-xs text-gray-400 mb-0.5">Flags</div>
        <div class="text-sm font-bold" :class="nErrors?'text-red-600':'text-amber-600'">
          {{ nErrors }} err · {{ nWarnings }} warn
        </div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl p-3">
        <div class="text-xs text-gray-400 mb-0.5">Status</div>
        <div class="text-sm font-bold" :class="statusColor">{{ currentStatus }}</div>
      </div>
    </div>

    <!-- KPI values -->
    <div v-if="kpis" class="grid grid-cols-6 gap-2 mb-5">
      <div v-for="k in kpiCards" :key="k.label" class="bg-white border border-gray-100 rounded-lg p-2.5 text-center">
        <div class="text-[9px] text-gray-400 uppercase tracking-wide mb-1">{{ k.label }}</div>
        <div class="text-base font-bold" :style="{color:k.color}">{{ k.value }}</div>
        <div class="text-[9px] text-gray-400">{{ k.unit }}</div>
      </div>
    </div>

    <!-- Flags -->
    <div class="mb-5 space-y-2">
      <div v-for="(flag, i) in allFlags" :key="i"
        class="flex items-start gap-3 px-4 py-3 rounded-xl border"
        :class="{
          'bg-red-50 border-red-200': flag.severity==='error' && !flag.resolved,
          'bg-yellow-50 border-yellow-200': flag.severity==='warning' && !flag.resolved,
          'bg-green-50 border-green-200': flag.severity==='ok' || flag.resolved,
        }">
        <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold text-white mt-0.5"
          :class="{'bg-red-500':flag.severity==='error'&&!flag.resolved,'bg-yellow-500':flag.severity==='warning'&&!flag.resolved,'bg-green-500':flag.severity==='ok'||flag.resolved}">
          {{ flag.severity==='error' ? '✕' : flag.severity==='warning' ? '!' : '✓' }}
        </div>
        <div class="flex-1">
          <div class="text-sm font-semibold text-gray-800">{{ flag.message }}{{ flag.resolved ? ' — Approved' : '' }}</div>
          <div v-if="flag.detail" class="text-xs text-gray-500 mt-0.5">{{ flag.detail }}</div>
        </div>
        <div v-if="!flag.resolved && flag.severity !== 'ok'" class="flex gap-2">
          <button v-if="flag.severity==='warning'" @click="resolveFlag(i)"
            class="px-3 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700">Accept</button>
          <button @click="queryFlag(i)"
            class="px-3 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium hover:bg-gray-200">Query</button>
        </div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="flex gap-3">
      <button @click="approve" class="px-5 h-9 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700">
        ✓ Verify & Approve
      </button>
      <button @click="markPending" class="px-5 h-9 bg-amber-500 text-white rounded-lg text-sm font-semibold hover:bg-amber-600">
        ◉ Mark as Pending
      </button>
      <button @click="flagSubmission" class="px-5 h-9 bg-red-500 text-white rounded-lg text-sm font-semibold hover:bg-red-600">
        ⚑ Flag Issues
      </button>
      <div v-if="actionMsg" class="self-center text-sm font-medium" :class="actionOk?'text-green-600':'text-red-600'">
        {{ actionMsg }}
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
const availYears = ref([2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009]);
const loading    = ref(false);
const kpis       = ref(null);
const flags      = ref([]);
const resolvedSet= ref(new Set());
const currentStatus = ref("Not Submitted");
const actionMsg  = ref(""); const actionOk = ref(true);

const C = { navy:"#0A2240", co2:"#475569", energy:"#F59E0B", water:"#0891B2", renew:"#16A34A", waste:"#7C3AED" };

const kpiCards = computed(() => {
  if (!kpis.value) return [];
  const k = kpis.value;
  return [
    { label:"CO₂ KPI",    value:(k.co2_kpi||0).toFixed(3),             unit:"T.CO₂/T", color:C.co2    },
    { label:"Energy KPI", value:(k.energy_kpi||0).toFixed(2),           unit:"GJ/T",    color:C.energy },
    { label:"Water KPI",  value:(k.water_kpi||0).toFixed(2),            unit:"m³/T",    color:C.water  },
    { label:"Renewable",  value:(k.renew_share_pct||0).toFixed(1),      unit:"%",       color:C.renew  },
    { label:"Waste Rec.", value:k.waste_recovery_pct?(k.waste_recovery_pct*100).toFixed(1):"—", unit:"%", color:C.waste },
    { label:"ISO 14001",  value:k.pct_certified?(k.pct_certified*100).toFixed(0):"—",  unit:"%",       color:C.navy  },
  ];
});

const allFlags = computed(() => flags.value.map((f, i) => ({ ...f, resolved: resolvedSet.value.has(i) })));
const nErrors   = computed(() => flags.value.filter(f=>f.severity==="error").length);
const nWarnings = computed(() => flags.value.filter(f=>f.severity==="warning").length);
const avgComplete = computed(() => {
  if (!kpis.value) return 0;
  const k = kpis.value;
  const checks = [k.total_electricity>0, k.production>0, k.water_kpi>0, k.energy_kpi>0, k.co2_kpi>0, k.waste_recovery_pct>0];
  return Math.round(checks.filter(Boolean).length / checks.length * 100);
});
const statusColor = computed(() => {
  if (currentStatus.value==="Verified") return "text-green-600";
  if (currentStatus.value==="Flagged")  return "text-red-600";
  return "text-amber-600";
});

function resolveFlag(i) { resolvedSet.value = new Set([...resolvedSet.value, i]); }
function queryFlag(i) { actionMsg.value = `Query logged for: ${flags.value[i]?.message}`; actionOk.value=true; }

async function setStatus(status) {
  try {
    await api.setVerification({ company: selCompany.value, year: selYear.value, status });
    currentStatus.value = status;
    actionMsg.value = `✅ ${selCompany.value} ${selYear.value} marked as ${status}`;
    actionOk.value = true;
    if (status==="Verified") resolvedSet.value = new Set(flags.value.map((_,i)=>i));
  } catch(e) {
    actionMsg.value = `❌ ${e.message}`;
    actionOk.value = false;
  }
  setTimeout(()=>actionMsg.value="", 4000);
}

const approve         = () => setStatus("Verified");
const markPending     = () => setStatus("Pending");
const flagSubmission  = () => setStatus("Flagged");

async function loadCompanies() {
  try {
    const res = await api.getCompanies();
    companies.value = Array.isArray(res) ? res : (res?.companies || []);
    if (companies.value.length) { selCompany.value = companies.value[0]; await loadData(); }
  } catch(e) { console.error("Verif companies:", e); }
}

async function loadData() {
  if (!selCompany.value) return;
  loading.value = true;
  kpis.value = null; flags.value = [];
  try {
    const res = await api.getCompanyData(selCompany.value, selYear.value);
    if (res?.kpis) kpis.value = res.kpis;
    if (res?.flags) flags.value = res.flags;
    if (res?.years) availYears.value = res.years.slice().sort((a,b)=>b-a);
    if (res?.verification_status) currentStatus.value = res.verification_status;
    resolvedSet.value = new Set();
  } catch(e) { console.error("Verif load:", e); }
  finally { loading.value = false; }
}

onMounted(loadCompanies);
watch([selCompany, selYear], loadData);
</script>