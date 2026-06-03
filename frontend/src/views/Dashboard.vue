<template>
  <div>
    <!-- KPI Cards grid -->
    <div class="grid grid-cols-4 gap-3 mb-4">
      <KPICard
        label="CO₂ Intensity"
        :value="kpis.co2_kpi"
        unit="T.CO₂ / metric tonne"
        :delta="yoy.co2_kpi"
        :lowerBetter="true"
        color="#0E1117"
      />
      <KPICard
        label="Energy Intensity"
        :value="kpis.energy_kpi"
        unit="GJ / metric tonne"
        :delta="yoy.energy_kpi"
        :lowerBetter="true"
        color="#F59E0B"
      />
      <KPICard
        label="Water Intensity"
        :value="kpis.water_kpi"
        unit="m³ / metric tonne"
        :delta="yoy.water_kpi"
        :lowerBetter="true"
        color="#0891B2"
      />
      <KPICard
        label="Renewable Electricity"
        :value="kpis.renewable_share_pct ? kpis.renewable_share_pct + '%' : null"
        unit="of total electricity"
        :delta="yoy.renewable_share_pct"
        :lowerBetter="false"
        color="#16A34A"
      />
      <KPICard
        label="Total CO₂"
        :value="kpis.total_co2_t ? (kpis.total_co2_t / 1_000_000).toFixed(2) + 'M' : null"
        unit="T.CO₂ absolute"
        :delta="yoy.total_co2_t"
        :lowerBetter="true"
        color="#7C3AED"
      />
      <KPICard
        label="Total Energy"
        :value="kpis.total_energy_gj ? (kpis.total_energy_gj / 1_000_000).toFixed(1) + 'M' : null"
        unit="GJ total"
        :delta="yoy.total_energy_gj"
        :lowerBetter="true"
        color="#0E1117"
      />
      <KPICard
        label="Waste Recovery"
        :value="kpis.waste_recovery_pct ? kpis.waste_recovery_pct + '%' : null"
        unit="of total waste"
        :delta="yoy.waste_recovery_pct"
        :lowerBetter="false"
        color="#0D9488"
      />
      <KPICard
        label="ISO 14001 Coverage"
        :value="kpis.iso_certified_pct ? kpis.iso_certified_pct + '%' : null"
        unit="of all sites"
        :delta="yoy.iso_certified_pct"
        :lowerBetter="false"
        color="#E31E24"
      />
    </div>

    <!-- Charts row -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50">
          <div class="text-[13px] font-semibold">CO₂ Intensity Trend</div>
          <div class="text-[11px] text-gray-400 mt-0.5">T.CO₂/T · 2009–2023</div>
        </div>
        <div class="p-4 h-48">
          <canvas ref="co2Chart"></canvas>
        </div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50">
          <div class="text-[13px] font-semibold">Renewable Electricity Share</div>
          <div class="text-[11px] text-gray-400 mt-0.5">% · 2009–2023</div>
        </div>
        <div class="p-4 h-48">
          <canvas ref="renewChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Submission status banner -->
    <div v-if="auth.role === 'client'" class="bg-white border border-gray-100 rounded-xl p-4 flex items-center justify-between">
      <div>
        <div class="text-[13px] font-semibold">2023 Data Submission</div>
        <div class="text-[11px] text-gray-400 mt-0.5">Complete all 6 steps to submit your annual ESG data</div>
      </div>
      <router-link to="/entry" class="px-4 h-9 bg-navy text-white rounded-lg text-[12px] font-semibold flex items-center hover:bg-[#1a1a5a] transition-colors">
        Go to data entry →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart, registerables } from "chart.js";
import KPICard from "@/components/KPICard.vue";
import { useAuthStore } from "@/stores/auth.js";
import { getAnalytics } from "@/services/api.js";

Chart.register(...registerables);

const auth = useAuthStore();

// Demo KPIs — will be replaced by real API data
const kpis = ref({
  co2_kpi: 0.551, energy_kpi: 8.7, water_kpi: 5.78,
  renewable_share_pct: 38.8, total_co2_t: 2050000,
  total_energy_gj: 32380000, waste_recovery_pct: 85.8,
  iso_certified_pct: 100,
});
const yoy = ref({
  co2_kpi: -4.3, energy_kpi: -4.4, water_kpi: 0.9,
  renewable_share_pct: 7.7, total_co2_t: -0.5,
  total_energy_gj: 0.3, waste_recovery_pct: 0.8,
  iso_certified_pct: 0,
});

const co2Chart  = ref(null);
const renewChart = ref(null);
let charts = [];

// Historical baseline data for charts
const YEARS    = ["'09","'10","'11","'12","'13","'14","'15","'16","'17","'18","'19","'20","'21","'22","'23"];
const CO2_DATA = [0.82,0.79,0.76,0.74,0.72,0.71,0.69,0.67,0.66,0.64,0.63,0.60,0.58,0.576,0.551];
const REN_DATA = [2,2,3,3,4,5,6,7,9,12,16,22,20,31,38.8];

const CHART_OPTS = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 900, easing: "easeOutQuart" },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: "#0E1117",
      titleColor: "#fff",
      bodyColor: "rgba(255,255,255,.65)",
      borderColor: "rgba(255,255,255,.1)",
      borderWidth: 1,
      padding: 8,
      cornerRadius: 6,
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } },
    y: { grid: { color: "rgba(0,0,0,.04)" }, ticks: { color: "#94A3B8", font: { size: 10 } } },
  },
};

function buildCharts() {
  // Destroy previous if re-rendered
  charts.forEach((c) => c.destroy());
  charts = [];

  if (co2Chart.value) {
    charts.push(new Chart(co2Chart.value, {
      type: "line",
      data: {
        labels: YEARS,
        datasets: [{
          data: CO2_DATA,
          borderColor: "#0E1117",
          backgroundColor: "rgba(14,17,23,.06)",
          fill: true, tension: 0.4, pointRadius: 2, borderWidth: 2,
        }],
      },
      options: CHART_OPTS,
    }));
  }

  if (renewChart.value) {
    charts.push(new Chart(renewChart.value, {
      type: "line",
      data: {
        labels: YEARS,
        datasets: [{
          data: REN_DATA,
          borderColor: "#16A34A",
          backgroundColor: "rgba(22,163,74,.07)",
          fill: true, tension: 0.4, pointRadius: 2, borderWidth: 2,
        }],
      },
      options: CHART_OPTS,
    }));
  }
}

onMounted(() => {
  buildCharts();
  // TODO: fetch real KPIs from API
  // getAnalytics({ company_id: auth.companyId, year_from: 2023, year_to: 2023 })
  //   .then(data => { /* populate kpis */ })
});
</script>
