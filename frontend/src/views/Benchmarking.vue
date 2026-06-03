<template>
  <div class="tip-fade-in">
    <div class="flex items-start justify-between mb-4">
      <div>
        <h1 class="text-[20px] font-extrabold text-[#0F172A] tracking-tight">Benchmarking</h1>
        <p class="text-[11px] text-[#64748B] mt-0.5">Industry peer comparison · TIP sector quartiles</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-if="isDss" v-model="selCompany" @change="load"
          class="h-9 px-3 border border-[#E2E8F0] rounded-lg text-[12px] bg-white appearance-none cursor-pointer">
          <option v-for="c in companies" :key="c.name" :value="c.name">{{ c.name }}</option>
        </select>
        <select v-model.number="selYear" @change="load"
          class="h-9 px-3 border border-[#E2E8F0] rounded-lg text-[12px] bg-white appearance-none cursor-pointer">
          <option v-for="yr in years" :key="yr" :value="yr">{{ yr }}</option>
        </select>
      </div>
    </div>

    <!-- ── 5 KPI Chips ──────────────────────────────────────────────────────── -->
    <div class="grid grid-cols-5 gap-3 mb-4">
      <div v-for="chip in kpiChips" :key="chip.label"
        class="bg-white border border-[#E2E8F0] rounded-xl p-4">
        <div class="text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider mb-1">{{ chip.label }}</div>
        <div class="text-[22px] font-extrabold leading-none mb-2" :style="{ color: chip.color }">
          {{ chip.value }}
        </div>
        <div class="text-[9px] text-[#64748B] mb-2">{{ chip.unit }}</div>
        <!-- Percentile bar -->
        <div class="h-1.5 bg-[#F1F5F9] rounded-full relative overflow-visible">
          <div class="absolute inset-0 h-full rounded-full"
            :style="{ background: `linear-gradient(to right, #DCFCE7 0%, #FEF9C3 40%, #FEE2E2 100%)` }"></div>
          <div class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-2 h-4 rounded-sm shadow-sm"
            :style="{ left: chip.pct + '%', background: chip.color }"></div>
        </div>
        <div class="flex justify-between text-[9px] text-[#94A3B8] mt-1">
          <span>{{ chip.lowerBetter ? 'Best' : 'Low' }}</span>
          <span>{{ chip.label === 'CO₂ INTENSITY' || chip.lowerBetter ? 'Worst' : 'High' }}</span>
        </div>
      </div>
    </div>

    <!-- ── Download PDF ─────────────────────────────────────────────────────── -->
    <button @click="downloadPdf"
      class="w-full h-10 mb-4 bg-red-500 hover:bg-red-600 text-white rounded-lg
             font-semibold text-[13px] flex items-center justify-center gap-2 transition-colors">
      ⬇ Download Full Benchmarking Report (PDF)
    </button>

    <!-- ── 7 tabs ───────────────────────────────────────────────────────────── -->
    <div class="bg-white border border-[#E2E8F0] rounded-xl overflow-hidden">
      <div class="flex border-b border-[#E2E8F0] overflow-x-auto">
        <button v-for="t in TABS" :key="t.id" @click="activeTab = t.id"
          class="px-4 py-3 text-[12px] font-semibold whitespace-nowrap transition-colors flex-shrink-0"
          :class="activeTab === t.id
            ? 'border-b-2 border-[#0A2240] text-[#0A2240]'
            : 'text-[#64748B] hover:text-[#0F172A]'">
          {{ t.label }}
        </button>
      </div>

      <div class="p-5">
        <!-- General -->
        <template v-if="activeTab === 'general'">
          <p class="text-[11px] text-[#64748B] mb-4">Overall ESG performance profile vs sector</p>
          <div class="grid grid-cols-2 gap-5">
            <div>
              <div class="text-[12px] font-semibold mb-2">ESG Radar Profile</div>
              <PlotlyChart :traces="radarTraces" :layout="radarLayout" :height="300"
                :chartKey="`radar-${selYear}-${selCompany}`" />
            </div>
            <div>
              <div class="text-[12px] font-semibold mb-2">Performance vs Sector (◆=You · ─=Median · ▬=IQR)</div>
              <PlotlyChart :traces="whiskerTraces" :layout="whiskerLayout" :height="300"
                :chartKey="`whisker-${selYear}-${selCompany}`" />
            </div>
          </div>
          <!-- Improvement table -->
          <div class="mt-5 border-t border-[#E2E8F0] pt-4">
            <div class="text-[12px] font-semibold mb-3">Improvement since {{ firstYear }}</div>
            <table class="w-full text-[12px]">
              <thead>
                <tr class="bg-[#F8FAFC]">
                  <th class="px-3 py-2 text-left text-[10px] font-bold text-[#64748B] uppercase">KPI</th>
                  <th class="px-3 py-2 text-right text-[10px] font-bold text-[#64748B] uppercase">{{ firstYear }}→{{ selYear }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="imp in improvements" :key="imp.kpi" class="border-t border-[#F1F5F9]">
                  <td class="px-3 py-2">{{ imp.kpi }}</td>
                  <td class="px-3 py-2 text-right font-semibold"
                    :class="imp.good ? 'text-[#16A34A]' : 'text-red-500'">{{ imp.value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- CO₂ -->
        <template v-if="activeTab === 'co2'">
          <p class="text-[11px] text-[#64748B] mb-3">CO₂ intensity vs sector peers — Q1/Median/Q3 reference lines</p>
          <PlotlyChart :traces="co2BenchTraces" :layout="sectorLayout('CO₂ Intensity (T.CO₂/T)')"
            :height="280" :chartKey="`co2b-${selYear}-${selCompany}`" />
          <div class="mt-4">
            <PlotlyChart :traces="scopeAreaTraces" :layout="sectorLayout('Scope 1 vs Scope 2 (T.CO₂)')"
              :height="220" :chartKey="`scope-${selYear}-${selCompany}`" />
          </div>
        </template>

        <!-- Energy -->
        <template v-if="activeTab === 'energy'">
          <div class="grid grid-cols-2 gap-5">
            <PlotlyChart :traces="energyBenchTraces" :layout="sectorLayout('Energy Intensity (GJ/T)')"
              :height="260" :chartKey="`eb-${selYear}-${selCompany}`" />
            <PlotlyChart :traces="fuelMixTraces" :layout="{ barmode: 'stack', yaxis: { title: { text: 'GJ' } } }"
              :height="260" :chartKey="`fm-${selYear}-${selCompany}`" />
          </div>
        </template>

        <!-- Electricity -->
        <template v-if="activeTab === 'electricity'">
          <div class="grid grid-cols-2 gap-5">
            <PlotlyChart :traces="elecMixTraces" :layout="{ barmode: 'stack', yaxis: { title: { text: '%' }, range: [0,100] } }"
              :height="260" :chartKey="`emix-${selYear}-${selCompany}`" />
            <PlotlyChart :traces="renewBenchTraces" :layout="sectorLayout('Renewable Electricity Share (%)')"
              :height="260" :chartKey="`rew-${selYear}-${selCompany}`" />
          </div>
        </template>

        <!-- Water -->
        <template v-if="activeTab === 'water'">
          <div class="grid grid-cols-2 gap-5">
            <PlotlyChart :traces="waterBenchTraces" :layout="sectorLayout('Water Intensity (m³/T)')"
              :height="260" :chartKey="`wb-${selYear}-${selCompany}`" />
            <PlotlyChart :traces="waterBarTraces" :layout="{ yaxis: { title: { text: 'M m³' }, tickformat: '.1f' } }"
              :height="260" :chartKey="`wbar-${selYear}-${selCompany}`" />
          </div>
        </template>

        <!-- Waste -->
        <template v-if="activeTab === 'waste'">
          <div class="grid grid-cols-2 gap-5">
            <PlotlyChart :traces="wasteBenchTraces" :layout="sectorLayout('Waste Recovery Rate (%)')"
              :height="260" :chartKey="`wasteb-${selYear}-${selCompany}`" />
            <PlotlyChart :traces="wasteTotalTraces" :layout="{ barmode: 'group', yaxis: { title: { text: 'metric T' } } }"
              :height="260" :chartKey="`wastet-${selYear}-${selCompany}`" />
          </div>
        </template>

        <!-- Advanced -->
        <template v-if="activeTab === 'advanced'">
          <p class="text-[11px] text-[#64748B] mb-4">Paris-aligned trajectory · Decoupling analysis · KPI scorecard</p>
          <div class="grid grid-cols-2 gap-5 mb-5">
            <div>
              <div class="text-[12px] font-semibold mb-2">CO₂ Intensity vs Paris-Aligned Target (T.CO₂/T)</div>
              <PlotlyChart :traces="parisTraces" :layout="parisLayout" :height="280"
                :chartKey="`paris-${selYear}-${selCompany}`" />
            </div>
            <div>
              <div class="text-[12px] font-semibold mb-2">Decoupling: Renewable % vs CO₂ Intensity</div>
              <PlotlyChart :traces="decouplingTraces" :layout="decouplingLayout" :height="280"
                :chartKey="`dcpl-${selYear}-${selCompany}`" />
            </div>
          </div>
          <!-- KPI Scorecard table -->
          <div class="border border-[#E2E8F0] rounded-xl overflow-hidden">
            <div class="px-4 py-3 bg-[#F8FAFC] border-b border-[#E2E8F0] text-[12px] font-semibold">
              KPI Scorecard — {{ selYear }} vs Sector Quartiles
            </div>
            <table class="w-full text-[12px]">
              <thead>
                <tr class="border-b border-[#E2E8F0]">
                  <th class="px-4 py-2.5 text-left text-[10px] font-bold text-[#64748B] uppercase">KPI</th>
                  <th class="px-3 py-2.5 text-right text-[10px] font-bold text-[#64748B] uppercase">Your Value</th>
                  <th class="px-3 py-2.5 text-right text-[10px] font-bold text-[#64748B] uppercase">Q1 (25th)</th>
                  <th class="px-3 py-2.5 text-right text-[10px] font-bold text-[#64748B] uppercase">Median</th>
                  <th class="px-3 py-2.5 text-right text-[10px] font-bold text-[#64748B] uppercase">Q3 (75th)</th>
                  <th class="px-3 py-2.5 text-left text-[10px] font-bold text-[#64748B] uppercase">vs Median</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in scorecardRows" :key="row.kpi" class="border-t border-[#F1F5F9]">
                  <td class="px-4 py-2">{{ row.kpi }}</td>
                  <td class="px-3 py-2 text-right font-semibold">{{ row.myVal }}</td>
                  <td class="px-3 py-2 text-right text-[#64748B]">{{ row.q1 }}</td>
                  <td class="px-3 py-2 text-right text-[#64748B]">{{ row.median }}</td>
                  <td class="px-3 py-2 text-right text-[#64748B]">{{ row.q3 }}</td>
                  <td class="px-3 py-2 font-semibold"
                    :class="row.good ? 'text-[#16A34A]' : 'text-red-500'">
                    {{ row.good ? '↓ Improving' : '↑ Needs work' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useEsgStore }  from '@/stores/esg.js'
import PlotlyChart from '@/components/PlotlyChart.vue'
import api from '@/services/api.js'

const auth = useAuthStore()
const esg  = useEsgStore()
const isDss = computed(() => auth.role === 'dss')

const TABS = [
  { id: 'general',     label: 'General' },
  { id: 'co2',         label: 'CO₂' },
  { id: 'energy',      label: 'Energy' },
  { id: 'electricity', label: 'Electricity' },
  { id: 'water',       label: 'Water' },
  { id: 'waste',       label: 'Waste' },
  { id: 'advanced',    label: 'Advanced' },
]

const activeTab  = ref('general')
const selCompany = ref(auth.companyName)
const selYear    = ref(2023)
const years      = ref([2023, 2022, 2021, 2020])
const companies  = ref([])
const bench      = ref(null)

const CAT_CO2   = '#475569'; const CAT_ENERGY = '#F59E0B'; const CAT_WATER  = '#0891B2'
const CAT_RENEW = '#16A34A'; const CAT_WASTE  = '#7C3AED'; const GREEN = '#16A34A'

async function load() {
  try {
    bench.value = await api.getBenchmarks({ company_id: selCompany.value, year: selYear.value })
    if (bench.value?.available_years) years.value = [...bench.value.available_years].reverse()
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  if (isDss.value) {
    const data = await api.getCompanies()
    companies.value = data
  }
  await load()
})

// ── Data helpers ──────────────────────────────────────────────────────────────
const b = computed(() => bench.value || {})
const ys = computed(() => b.value.series_years || [])
const co = computed(() => b.value.company_series || {})
const sec= computed(() => b.value.sector_series || {})
const q  = computed(() => b.value.quartiles || {})
const myKpis = computed(() => b.value.company_kpis || {})
const firstYear = computed(() => ys.value[0] || 2009)

const sectorLayout = (title) => ({
  yaxis: { title: { text: '' } },
  hovermode: 'x unified',
  title: { text: title, font: { size: 13 } }
})

// ── KPI chips ─────────────────────────────────────────────────────────────────
const KPI_DEFS = [
  { key: 'co2_kpi',             label: 'CO₂ INTENSITY',    unit: 'T.CO₂/T',  color: CAT_CO2,   dp: 3, lowerBetter: true },
  { key: 'energy_kpi',          label: 'ENERGY INTENSITY', unit: 'GJ/T',      color: CAT_ENERGY,dp: 2, lowerBetter: true },
  { key: 'water_kpi',           label: 'WATER INTENSITY',  unit: 'm³/T',      color: CAT_WATER, dp: 2, lowerBetter: true },
  { key: 'renewable_share_pct', label: 'RENEWABLE ELEC.',  unit: '%',          color: CAT_RENEW, dp: 1, lowerBetter: false },
  { key: 'waste_recovery_pct',  label: 'WASTE RECOVERY',   unit: '%',          color: CAT_WASTE, dp: 1, lowerBetter: false },
]
const kpiChips = computed(() => KPI_DEFS.map(d => {
  const val  = myKpis.value[d.key] || 0
  const qd   = q.value[d.key] || {}
  const lo   = qd.q10 || 0; const hi = qd.q90 || val * 1.5 || 1
  const span = Math.abs(hi - lo) || 1
  let pct = ((val - lo) / span) * 100
  if (d.lowerBetter) pct = 100 - pct
  return { ...d, value: val.toFixed(d.dp), pct: Math.max(0, Math.min(100, pct)) }
}))

// ── Radar chart ────────────────────────────────────────────────────────────────
const radarTraces = computed(() => {
  const dims = ['CO₂ Intensity','Energy Intensity','Water Intensity','Renewable Elec.','Waste Recovery']
  const coScores = KPI_DEFS.map(d => {
    const val = myKpis.value[d.key] || 0
    const qd  = q.value[d.key] || {}
    const lo  = qd.q10 || 0; const hi = qd.q90 || val * 1.5 || 1
    const span= Math.abs(hi - lo) || 1
    const s   = d.lowerBetter ? (hi - val) / span * 100 : (val - lo) / span * 100
    return Math.max(0, Math.min(100, s))
  })
  const secScores = KPI_DEFS.map(() => 50)
  return [
    { type: 'scatterpolar', r: coScores, theta: dims, fill: 'toself',
      name: selCompany.value?.split(' ')[0],
      line: { color: GREEN, width: 2 }, fillcolor: 'rgba(22,163,74,0.15)', mode: 'lines+markers',
      marker: { size: 5, color: GREEN } },
    { type: 'scatterpolar', r: secScores, theta: dims, fill: 'none',
      name: 'Sector Median',
      line: { color: '#94A3B8', width: 1.5, dash: 'dot' }, mode: 'lines+markers',
      marker: { size: 4, color: '#94A3B8', symbol: 'diamond' } },
  ]
})
const radarLayout = computed(() => ({
  polar: { radialaxis: { range: [0, 100], tickfont: { size: 9 } },
           angularaxis: { tickfont: { size: 10 } } },
  showlegend: true,
}))

// ── Dot-and-whisker chart ─────────────────────────────────────────────────────
const whiskerTraces = computed(() => {
  const traces = []
  KPI_DEFS.forEach((d, idx) => {
    const qd  = q.value[d.key] || {}
    const val = myKpis.value[d.key] || 0
    const label = d.label
    const good  = (val <= (qd.median || 0) && d.lowerBetter) || (val >= (qd.median || 0) && !d.lowerBetter)
    // Range band
    traces.push({ type: 'scatter', x: [qd.q10, qd.q90], y: [label, label],
      mode: 'lines', line: { color: '#E2E8F0', width: 8 }, showlegend: false, hoverinfo: 'skip' })
    // IQR
    traces.push({ type: 'scatter', x: [qd.q25, qd.q75], y: [label, label],
      mode: 'lines', line: { color: d.color, width: 12, opacity: 0.25 }, showlegend: false, hoverinfo: 'skip' })
    // Median
    traces.push({ type: 'scatter', x: [qd.median], y: [label],
      mode: 'markers', marker: { size: 10, color: '#64748B', symbol: 'line-ns' }, showlegend: false,
      hovertemplate: `Median: ${(qd.median||0).toFixed(3)}<extra></extra>` })
    // Company diamond
    traces.push({ type: 'scatter', x: [val], y: [label],
      mode: 'markers+text', text: [val.toFixed(2)],
      textposition: 'top center', textfont: { size: 9, color: good ? GREEN : '#EF4444' },
      marker: { size: 14, color: good ? GREEN : '#EF4444', symbol: 'diamond',
                line: { color: 'white', width: 2 } },
      showlegend: false,
      hovertemplate: `${label}: ${val.toFixed(3)}<extra></extra>` })
  })
  return traces
})
const whiskerLayout = computed(() => ({
  xaxis: { gridcolor: '#F1F5F9' }, yaxis: { gridcolor: '#F1F5F9' }, showlegend: false,
}))

// ── Sector trend with IQR band ───────────────────────────────────────────────
function sectorBandTraces(field, color, name) {
  return [
    { type: 'scatter', name: 'Q3', x: ys.value, y: sec.value[field + '_q75'],
      mode: 'lines', line: { color: 'rgba(0,0,0,0)' }, showlegend: false, hoverinfo: 'skip' },
    { type: 'scatter', name: 'Sector IQR', x: ys.value, y: sec.value[field + '_q25'],
      fill: 'tonexty', fillcolor: color + '22', mode: 'lines', line: { color: 'rgba(0,0,0,0)' },
      hoverinfo: 'skip' },
    { type: 'scatter', name: 'Sector Median', x: ys.value, y: sec.value[field + '_median'],
      mode: 'lines', line: { color: '#94A3B8', width: 1.5, dash: 'dot' },
      hovertemplate: '<b>%{x}</b><br>Median: %{y:.3f}<extra></extra>' },
    { type: 'scatter', name: name, x: ys.value, y: co.value[field],
      mode: 'lines+markers', connectgaps: false,
      line: { color, width: 2.5 }, marker: { size: 5, color },
      hovertemplate: `<b>%{x}</b><br>${name}: %{y:.3f}<extra></extra>` },
  ]
}

const co2BenchTraces    = computed(() => sectorBandTraces('co2_kpi',             CAT_CO2,   'CO₂ Intensity'))
const energyBenchTraces = computed(() => sectorBandTraces('energy_kpi',          CAT_ENERGY,'Energy Intensity'))
const waterBenchTraces  = computed(() => sectorBandTraces('water_kpi',           CAT_WATER, 'Water Intensity'))
const renewBenchTraces  = computed(() => sectorBandTraces('renewable_share_pct', CAT_RENEW, 'Renewable %'))
const wasteBenchTraces  = computed(() => sectorBandTraces('waste_recovery_pct',  CAT_WASTE, 'Waste Recovery %'))

const scopeAreaTraces = computed(() => [
  { type: 'scatter', name: 'Scope 2', x: ys.value, y: co.value.scope2_co2_t,
    stackgroup: 'sc', fillcolor: 'rgba(148,163,184,0.3)', mode: 'none' },
  { type: 'scatter', name: 'Scope 1', x: ys.value, y: co.value.scope1_co2_t,
    stackgroup: 'sc', fillcolor: 'rgba(71,85,105,0.5)',   mode: 'none' },
])

const fuelMixTraces = computed(() => [
  { type: 'bar', name: 'Nat. Gas',      x: ys.value, y: co.value.nat_gas_gj,   marker: { color: CAT_ENERGY } },
  { type: 'bar', name: 'Renew. Elec.',  x: ys.value, y: co.value.renew_elec_gj,marker: { color: GREEN } },
  { type: 'bar', name: 'Diesel',        x: ys.value, y: co.value.diesel_gj,    marker: { color: '#78716C' } },
  { type: 'bar', name: 'Coal',          x: ys.value, y: co.value.coal_gj,      marker: { color: '#475569' } },
])

const elecMixTraces = computed(() => [
  { type: 'bar', name: 'Renewable',     x: ys.value,
    y: (co.value.renewable_share_pct || []), marker: { color: GREEN } },
  { type: 'bar', name: 'Non-Renewable', x: ys.value,
    y: (co.value.renewable_share_pct || []).map(v => 100 - (v||0)), marker: { color: '#94A3B8' } },
])

const waterBarTraces = computed(() => [
  { type: 'bar', name: 'Withdrawals (M m³)', x: ys.value,
    y: (co.value.total_water_m3 || []).map(v => (v||0)/1e6), marker: { color: CAT_WATER } },
])

const wasteTotalTraces = computed(() => [
  { type: 'bar', name: 'Total Waste',  x: ys.value, y: co.value.total_waste_t,    marker: { color: '#E2E8F0' } },
  { type: 'bar', name: 'Recovered',   x: ys.value, y: co.value.waste_recovered_t, marker: { color: CAT_WASTE } },
])

// ── Advanced tab ──────────────────────────────────────────────────────────────
const parisTraces = computed(() => {
  const baseYr  = ys.value[0] || 2009
  const baseVal = (co.value.co2_kpi || [])[0] || 0.7
  const paris   = ys.value.map(y => +(baseVal * Math.pow(0.958, y - baseYr)).toFixed(4))
  return [
    { type: 'scatter', name: 'Actual intensity', x: ys.value, y: co.value.co2_kpi,
      mode: 'lines+markers', line: { color: CAT_CO2, width: 2.5 }, marker: { size: 5 }, connectgaps: false },
    { type: 'scatter', name: `Paris 4.2%/yr (from ${baseYr})`, x: ys.value, y: paris,
      mode: 'lines', line: { color: GREEN, width: 1.5, dash: 'dot' } },
  ]
})
const parisLayout = { yaxis: { title: { text: 'T.CO₂/T' } }, hovermode: 'x unified' }

const decouplingTraces = computed(() => {
  const co2arr = co.value.co2_kpi || []
  const renarr = co.value.renewable_share_pct || []
  const valid  = ys.value.filter((_, i) => co2arr[i] > 0 && renarr[i] > 0)
  const n = valid.length
  return [{
    type: 'scatter', mode: 'lines+markers',
    x: valid.map((y, i) => renarr[ys.value.indexOf(y)]),
    y: valid.map((y) => co2arr[ys.value.indexOf(y)]),
    marker: { size: 10, color: valid.map((_, i) => `rgba(22,163,74,${0.25 + 0.75*i/Math.max(n-1,1)})`),
              line: { color: 'white', width: 1.5 }, symbol: 'circle' },
    line: { color: '#E2E8F0', width: 1, dash: 'dot' },
    text: valid.map(String), textposition: 'top center',
    hovertemplate: '<b>%{text}</b><br>Renew: %{x:.1f}%<br>CO₂: %{y:.3f}<extra></extra>',
    showlegend: false,
  }]
})
const decouplingLayout = {
  xaxis: { title: { text: 'Renewable Electricity (%)' } },
  yaxis: { title: { text: 'CO₂ Intensity (T.CO₂/T)' } },
}

// ── KPI Scorecard ─────────────────────────────────────────────────────────────
const scorecardRows = computed(() => KPI_DEFS.map(d => {
  const val = myKpis.value[d.key] || 0
  const qd  = q.value[d.key] || {}
  const med = qd.median || 0
  const good= d.lowerBetter ? val <= med : val >= med
  return {
    kpi: d.label.replace('_', ' '),
    myVal:  val.toFixed(d.dp) + ' ' + d.unit,
    q1:     qd.q25?.toFixed(d.dp) || '—',
    median: qd.median?.toFixed(d.dp) || '—',
    q3:     qd.q75?.toFixed(d.dp) || '—',
    good,
  }
}))

// ── Improvements ──────────────────────────────────────────────────────────────
const improvements = computed(() => {
  if (!co.value.co2_kpi?.length || co.value.co2_kpi.length < 2) return []
  return KPI_DEFS.map(d => {
    const arr   = co.value[d.key] || []
    const first = arr[0] || 0; const last = arr[arr.length-1] || 0
    const pct   = first !== 0 ? ((last-first)/Math.abs(first)*100) : 0
    const good  = d.lowerBetter ? pct <= 0 : pct >= 0
    return { kpi: d.label, value: `${pct.toFixed(1)}%`, good }
  })
})

function downloadPdf() { alert('PDF generation — hook up to backend /api/reports/pdf') }
</script>
