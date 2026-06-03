<template>
  <div class="tip-fade-in">

    <!-- ── Page header ────────────────────────────────────────────────────── -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <h1 class="text-[22px] font-extrabold text-[#0F172A] tracking-tight leading-none">
          Welcome, {{ firstName }} 👋
        </h1>
        <p class="text-[12px] text-[#64748B] mt-1">
          {{ auth.companyName }} · Your Performance Dashboard
        </p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model.number="selYear" @change="onYearChange"
          class="h-9 px-3 border border-[#E2E8F0] rounded-lg text-[13px] font-semibold
                 bg-white cursor-pointer focus:outline-none">
          <option v-for="yr in availYears" :key="yr" :value="yr">{{ yr }}</option>
        </select>
        <button @click="$router.push('/entry')"
          class="h-9 px-4 bg-[#0A2240] text-white rounded-lg text-[12px] font-semibold
                 hover:bg-[#1a3560] transition-colors">
          📋 Submit Data
        </button>
      </div>
    </div>

    <!-- ── Submission status bar ─────────────────────────────────────────── -->
    <div class="bg-white border border-[#E2E8F0] rounded-xl px-5 py-3 mb-4 flex items-center gap-4">
      <div class="flex-1">
        <div class="text-[11px] text-[#64748B] mb-1.5">{{ selYear }} Submission Status</div>
        <div class="h-1.5 bg-[#F1F5F9] rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-700"
            :class="statusBarColor"
            :style="{ width: statusPct + '%' }"></div>
        </div>
      </div>
      <div class="text-[18px] font-bold" :class="statusNumColor">
        {{ sectionsDone }}/6
      </div>
      <div class="text-[11px] text-[#64748B]">sections complete</div>
      <div class="border-l border-[#E2E8F0] pl-4 text-[12px] font-semibold whitespace-nowrap"
        :class="verifTextColor">
        {{ verifIcon }} {{ verifLabel }}
      </div>
    </div>

    <!-- ── 8 KPI Cards ───────────────────────────────────────────────────── -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <KpiCard v-for="k in kpiCards" :key="k.label" v-bind="k" />
    </div>

    <!-- ── Chart tabs ────────────────────────────────────────────────────── -->
    <div class="bg-white border border-[#E2E8F0] rounded-xl overflow-hidden">
      <div class="flex border-b border-[#E2E8F0]">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-5 py-3 text-[12px] font-semibold transition-colors flex items-center gap-1.5"
          :class="tabClass(tab.id)">
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <div class="p-4">
        <!-- CO₂ Trend -->
        <div v-if="activeTab === 'co2'">
          <div class="text-[13px] font-semibold mb-3">
            Total CO₂ Emissions (Scope 1 + 2) with Intensity
          </div>
          <PlotlyChart
            :traces="co2Traces"
            :layout="co2Layout"
            :height="320"
            :chartKey="'co2-' + selYear + '-' + dfVersion" />
        </div>

        <!-- Energy Mix -->
        <div v-if="activeTab === 'energy'">
          <div class="text-[13px] font-semibold mb-3">Energy Mix by Source (GJ)</div>
          <PlotlyChart
            :traces="energyTraces"
            :layout="energyLayout"
            :height="320"
            :chartKey="'energy-' + selYear + '-' + dfVersion" />
        </div>

        <!-- Water -->
        <div v-if="activeTab === 'water'">
          <div class="text-[13px] font-semibold mb-3">Water Withdrawals &amp; Intensity</div>
          <PlotlyChart
            :traces="waterTraces"
            :layout="waterLayout"
            :height="320"
            :chartKey="'water-' + selYear + '-' + dfVersion" />
        </div>

        <!-- Waste & Fuel -->
        <div v-if="activeTab === 'waste'">
          <div class="text-[13px] font-semibold mb-3">
            Waste Recovery Rate &amp; Renewable Electricity
          </div>
          <PlotlyChart
            :traces="wasteTraces"
            :layout="wasteLayout"
            :height="320"
            :chartKey="'waste-' + selYear + '-' + dfVersion" />
        </div>
      </div>
    </div>

    <!-- ── Historical KPI Summary Table ─────────────────────────────────── -->
    <div class="bg-white border border-[#E2E8F0] rounded-xl mt-4 overflow-hidden">
      <div class="px-5 py-3 border-b border-[#E2E8F0]">
        <div class="text-[13px] font-semibold">
          Historical KPI Summary — {{ auth.companyName }}
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-[12px]">
          <thead>
            <tr class="bg-[#F8FAFC] border-b border-[#E2E8F0]">
              <th class="px-4 py-2.5 text-left text-[10px] font-bold text-[#64748B] uppercase tracking-wider w-16">Year</th>
              <th v-for="h in TABLE_HEADERS" :key="h"
                class="px-3 py-2.5 text-right text-[10px] font-bold text-[#64748B] uppercase tracking-wider">
                {{ h }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in tableRows" :key="row.year"
              class="border-t border-[#F1F5F9]"
              :class="rowClass(row.year, i)">
              <td class="px-4 py-2 font-semibold">{{ row.year }}</td>
              <td class="px-3 py-2 text-right">{{ row.production }}</td>
              <td class="px-3 py-2 text-right">{{ row.total_co2 }}</td>
              <td class="px-3 py-2 text-right">{{ row.co2_kpi }}</td>
              <td class="px-3 py-2 text-right">{{ row.energy_kpi }}</td>
              <td class="px-3 py-2 text-right">{{ row.renew_pct }}</td>
              <td class="px-3 py-2 text-right">{{ row.water_kpi }}</td>
              <td class="px-3 py-2 text-right">{{ row.waste_pct }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useEsgStore }  from '@/stores/esg.js'
import KpiCard     from '@/components/KPICard.vue'
import PlotlyChart from '@/components/PlotlyChart.vue'

const auth = useAuthStore()
const esg  = useEsgStore()

const firstName = computed(() => (auth.companyName || 'User').split(' ')[0])
const selYear   = ref(new Date().getFullYear() - 1)
const activeTab = ref('co2')
const dfVersion = computed(() => esg.dfVersion)

const TABS = [
  { id: 'co2',    icon: '📈', label: 'CO₂ Trend' },
  { id: 'energy', icon: '⚡', label: 'Energy Mix' },
  { id: 'water',  icon: '💧', label: 'Water' },
  { id: 'waste',  icon: '♻️', label: 'Waste & Fuel' },
]

const TABLE_HEADERS = [
  'Production (MT)', 'CO₂ Total (T)', 'CO₂ Intensity',
  'Energy KPI (GJ/T)', 'Renew. Elec. %', 'Water KPI (m³/T)', 'Waste Recovery %',
]

// ── tab helper (avoids ternary inside :class attribute) ──────────────────────
function tabClass(id) {
  if (id === activeTab.value) {
    return 'border-b-2 border-[#0A2240] text-[#0A2240]'
  }
  return 'text-[#64748B] hover:text-[#0F172A]'
}

function rowClass(year, i) {
  if (year === selYear.value) return 'font-bold text-[#0A2240] bg-blue-50'
  return i % 2 === 0 ? 'bg-white' : 'bg-[#FAFBFC]'
}

// ── Store-derived data ────────────────────────────────────────────────────────
const charts      = computed(() => esg.homeCharts)
const availYears  = computed(() => {
  const yrs = esg.availableYears
  return yrs.length ? [...yrs].reverse() : [selYear.value]
})
const kpis        = computed(() => esg.homeKpis)
const yoy         = computed(() => esg.homeYoy)
const status      = computed(() => esg.submissionStatus)
const sectionsDone= computed(() => status.value.sections_done || 0)
const statusPct   = computed(() => (sectionsDone.value / 6) * 100)

const statusBarColor = computed(() => {
  if (sectionsDone.value === 6) return 'bg-[#16A34A]'
  if (sectionsDone.value >= 3)  return 'bg-amber-400'
  return 'bg-red-400'
})
const statusNumColor = computed(() => {
  if (sectionsDone.value === 6) return 'text-[#16A34A]'
  if (sectionsDone.value >= 3)  return 'text-amber-500'
  return 'text-red-500'
})

const verifStatus  = computed(() => status.value.verification || 'Pending')
const verifIcon    = computed(() => {
  const map = { Verified: '✓', Pending: '◉', Flagged: '⚑' }
  return map[verifStatus.value] || '○'
})
const verifLabel   = computed(() => {
  const map = { Verified: 'Verified by dss+', Pending: 'Pending Review', Flagged: 'Flagged' }
  return map[verifStatus.value] || 'Not Submitted'
})
const verifTextColor = computed(() => {
  const map = { Verified: 'text-[#16A34A]', Pending: 'text-amber-500', Flagged: 'text-red-500' }
  return map[verifStatus.value] || 'text-[#94A3B8]'
})

// ── KPI formatting ────────────────────────────────────────────────────────────
function fmtBig(v) {
  if (!v) return '—'
  if (v >= 1e6) return (v / 1e6).toFixed(2) + 'M'
  if (v >= 1e3) return (v / 1e3).toFixed(1) + 'k'
  return String(v)
}

const CAT_CO2   = '#475569'
const CAT_ENERGY= '#F59E0B'
const CAT_WATER = '#0891B2'
const CAT_RENEW = '#16A34A'
const CAT_WASTE = '#7C3AED'
const CAT_NAVY  = '#0A2240'
const CAT_ISO   = '#E31E24'

const kpiCards = computed(() => {
  const k = kpis.value
  const y = yoy.value
  const co2AbsVal  = k.total_co2_t   ? fmtBig(k.total_co2_t) + ' T' : '—'
  const co2KpiVal  = k.co2_kpi       ? k.co2_kpi.toFixed(3)          : '—'
  const engVal     = k.energy_kpi    ? k.energy_kpi.toFixed(2)        : '—'
  const renewVal   = k.renewable_share_pct ? k.renewable_share_pct.toFixed(1) + ' %' : '—'
  const watKpiVal  = k.water_kpi     ? k.water_kpi.toFixed(2)         : '—'
  const watAbsVal  = k.total_water_m3 ? fmtBig(k.total_water_m3) + ' m³' : '—'
  const wasteVal   = k.waste_recovery_pct ? k.waste_recovery_pct.toFixed(1) + ' %' : '—'
  const isoVal     = k.iso_certified_pct  ? k.iso_certified_pct.toFixed(0)  + ' %' : '—'

  return [
    { label: 'CO₂ Absolute',     value: co2AbsVal, delta: y.total_co2_t,        lowerBetter: true,  color: CAT_NAVY,   unit: 'T.CO₂' },
    { label: 'CO₂ Intensity',    value: co2KpiVal, delta: y.co2_kpi,            lowerBetter: true,  color: CAT_CO2,    unit: 'T/T' },
    { label: 'Energy Intensity', value: engVal,    delta: y.energy_kpi,         lowerBetter: true,  color: CAT_ENERGY, unit: 'GJ/T' },
    { label: 'Renewable Share',  value: renewVal,  delta: y.renewable_share_pct,lowerBetter: false, color: CAT_RENEW,  unit: '%' },
    { label: 'Water Intensity',  value: watKpiVal, delta: y.water_kpi,          lowerBetter: true,  color: CAT_WATER,  unit: 'm³/T' },
    { label: 'Water Withdrawal', value: watAbsVal, delta: y.total_water_m3,     lowerBetter: true,  color: CAT_WATER,  unit: 'm³' },
    { label: 'Waste Recovery',   value: wasteVal,  delta: y.waste_recovery_pct, lowerBetter: false, color: CAT_WASTE,  unit: '%' },
    { label: 'ISO 14001',        value: isoVal,    delta: y.iso_certified_pct,  lowerBetter: false, color: CAT_ISO,    unit: '%' },
  ]
})

// ── Chart traces ──────────────────────────────────────────────────────────────
const ys = computed(() => charts.value.years || [])

const co2Traces = computed(() => [
  { type: 'scatter', name: 'Scope 2', x: ys.value, y: charts.value.scope2_mt || [],
    stackgroup: 'sc', fillcolor: 'rgba(148,163,184,0.35)', mode: 'none',
    hovertemplate: '<b>%{x}</b><br>Scope 2: %{y:.2f} M T.CO₂<extra></extra>' },
  { type: 'scatter', name: 'Scope 1', x: ys.value, y: charts.value.scope1_mt || [],
    stackgroup: 'sc', fillcolor: 'rgba(71,85,105,0.5)', mode: 'none',
    hovertemplate: '<b>%{x}</b><br>Scope 1: %{y:.2f} M T.CO₂<extra></extra>' },
  { type: 'scatter', name: 'CO₂ Intensity', x: ys.value, y: charts.value.co2_kpi || [],
    yaxis: 'y2', mode: 'lines+markers', connectgaps: false,
    line: { color: '#C8102E', width: 2.5, dash: 'dot' },
    marker: { size: 5, color: '#C8102E' },
    hovertemplate: '<b>%{x}</b><br>Intensity: %{y:.3f}<extra></extra>' },
])
const co2Layout = computed(() => ({
  yaxis:  { title: { text: 'M T.CO₂' } },
  yaxis2: { title: { text: 'T.CO₂/T' }, overlaying: 'y', side: 'right' },
  hovermode: 'x unified',
}))

const energyTraces = computed(() => [
  { type: 'bar', name: 'Renew. Elec.',     x: ys.value, y: charts.value.renew_elec_gj    || [], marker: { color: CAT_RENEW } },
  { type: 'bar', name: 'Non-renew. Elec.', x: ys.value, y: charts.value.nonrenew_elec_gj || [], marker: { color: '#94A3B8' } },
  { type: 'bar', name: 'Natural Gas',      x: ys.value, y: charts.value.nat_gas_gj       || [], marker: { color: CAT_ENERGY } },
])
const energyLayout = computed(() => ({
  barmode: 'stack',
  yaxis: { title: { text: 'GJ' }, tickformat: ',.0f' },
  hovermode: 'x unified',
}))

const waterTraces = computed(() => [
  { type: 'bar', name: 'Total Withdrawals', x: ys.value, y: charts.value.water_m3 || [],
    marker: { color: CAT_WATER },
    hovertemplate: '<b>%{x}</b><br>%{y:,.0f} m³<extra></extra>' },
  { type: 'scatter', name: 'Intensity (m³/T)', x: ys.value, y: charts.value.water_kpi || [],
    yaxis: 'y2', mode: 'lines+markers', connectgaps: false,
    line: { color: '#164E63', width: 2 }, marker: { size: 4, color: '#164E63' },
    hovertemplate: '<b>%{x}</b><br>%{y:.2f} m³/T<extra></extra>' },
])
const waterLayout = computed(() => ({
  yaxis:  { title: { text: 'm³' }, tickformat: ',.0f' },
  yaxis2: { title: { text: 'm³/T' }, overlaying: 'y', side: 'right' },
  hovermode: 'x unified',
}))

const wasteTraces = computed(() => [
  { type: 'bar', name: 'Waste Recovery %', x: ys.value, y: charts.value.waste_recovery_pct || [],
    marker: { color: CAT_WASTE },
    hovertemplate: '<b>%{x}</b><br>%{y:.1f}%<extra></extra>' },
  { type: 'scatter', name: 'Renewable Elec. %', x: ys.value, y: charts.value.renewable_pct || [],
    yaxis: 'y2', mode: 'lines+markers', connectgaps: false,
    line: { color: CAT_RENEW, width: 2, dash: 'dot' }, marker: { size: 4, color: CAT_RENEW },
    hovertemplate: '<b>%{x}</b><br>%{y:.1f}%<extra></extra>' },
])
const wasteLayout = computed(() => ({
  yaxis:  { title: { text: 'Waste Recovery (%)' }, range: [0, 100] },
  yaxis2: { title: { text: 'Renewable Elec. (%)' }, overlaying: 'y', side: 'right' },
  hovermode: 'x unified',
}))

// ── Historical table ──────────────────────────────────────────────────────────
const tableRows = computed(() => {
  const series = charts.value.years || []
  const last10 = series.slice(-10).reverse()
  return last10.map(yr => {
    const idx = series.indexOf(yr)
    return {
      year:       yr,
      production: fmtBig(charts.value.production_t?.[idx]),
      total_co2:  fmtBig(charts.value.total_co2_t?.[idx]),
      co2_kpi:    (charts.value.co2_kpi?.[idx] ?? null)?.toFixed(3) ?? '—',
      energy_kpi: (charts.value.energy_kpi?.[idx] ?? null)?.toFixed(2) ?? '—',
      renew_pct:  charts.value.renewable_pct?.[idx] != null
        ? charts.value.renewable_pct[idx].toFixed(1) + '%' : '—',
      water_kpi:  (charts.value.water_kpi?.[idx] ?? null)?.toFixed(2) ?? '—',
      waste_pct:  charts.value.waste_recovery_pct?.[idx] != null
        ? charts.value.waste_recovery_pct[idx].toFixed(1) + '%' : '—',
    }
  })
})

// ── Lifecycle ─────────────────────────────────────────────────────────────────
async function load() {
  await esg.fetchHomeData(auth.companyName, selYear.value)
  if (esg.availableYears.length)
    selYear.value = Math.max(...esg.availableYears)
}

function onYearChange() {
  esg.fetchHomeData(auth.companyName, selYear.value)
}

onMounted(load)
watch(() => auth.companyName, load)
</script>