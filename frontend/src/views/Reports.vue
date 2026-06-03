<template>
  <div>
    <!-- Cover card -->
    <div class="bg-navy rounded-xl px-7 py-6 mb-4 relative overflow-hidden">
      <div class="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-dss/[0.07]"></div>
      <div class="font-head text-[20px] font-black text-white mb-1">
        {{ auth.companyName || 'VerdaTyres Corp' }} — ESG Performance Report 2023
      </div>
      <div class="text-[11.5px] text-white/40 mb-5">TIP Sustainability Reporting · Verified by dss+ · Confidential</div>
      <div class="flex gap-8">
        <div v-for="h in HEADLINES" :key="h.label">
          <div class="text-[9.5px] text-white/35 uppercase tracking-wider">{{ h.label }}</div>
          <div class="font-head text-[21px] font-bold text-white mt-0.5 leading-none">
            {{ h.value }}<span class="text-[12px] text-white/30 ml-1">{{ h.unit }}</span>
          </div>
          <div class="text-[10px] font-semibold mt-1" :class="h.good ? 'text-green-400' : 'text-red-400'">
            {{ h.delta }}
          </div>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-[13px] font-semibold">CO₂ Trend 2019–2023</div>
        <div class="p-4 h-44"><canvas ref="co2Chart"></canvas></div>
      </div>
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-4 pt-3 pb-2 border-b border-gray-50 text-[13px] font-semibold">Fuel Mix 2023</div>
        <div class="p-4 h-44"><canvas ref="fuelChart"></canvas></div>
      </div>
    </div>

    <!-- KPI summary table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden mb-4">
      <div class="px-5 py-3 border-b border-gray-50 flex items-center justify-between">
        <div class="text-[13px] font-semibold">Annual KPI Summary</div>
        <button class="px-3 h-7 bg-dss text-white rounded-lg text-[12px] font-semibold hover:bg-red-700 transition-colors">
          ⬇ Download PDF
        </button>
      </div>
      <table class="w-full text-[12.5px] border-collapse">
        <thead>
          <tr class="bg-gray-50">
            <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">KPI</th>
            <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">2021</th>
            <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">2022</th>
            <th class="px-3 py-2.5 text-left text-[9px] font-bold text-navy uppercase tracking-wider border-b border-gray-100">2023</th>
            <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Unit</th>
            <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Trend</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in TABLE_ROWS" :key="row.kpi"
            class="border-b border-gray-50 last:border-none hover:bg-gray-50">
            <td class="px-4 py-2.5 font-medium">{{ row.kpi }}</td>
            <td class="px-3 py-2.5 tabular-nums text-gray-500">{{ row.y2021 }}</td>
            <td class="px-3 py-2.5 tabular-nums text-gray-500">{{ row.y2022 }}</td>
            <td class="px-3 py-2.5 tabular-nums font-bold text-navy">{{ row.y2023 }}</td>
            <td class="px-3 py-2.5 text-gray-400">{{ row.unit }}</td>
            <td class="px-3 py-2.5 text-[11px] font-semibold" :class="row.trendClass">{{ row.trend }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart, registerables } from "chart.js";
import { useAuthStore } from "@/stores/auth.js";
Chart.register(...registerables);

const auth = useAuthStore();
const co2Chart  = ref(null);
const fuelChart = ref(null);

const HEADLINES = [
  { label: "CO₂ Intensity", value: "0.551", unit: "T/T",  delta: "▼ −4.3%", good: true  },
  { label: "Energy KPI",    value: "8.7",   unit: "GJ/T", delta: "▼ −4.4%", good: true  },
  { label: "Renew. Share",  value: "38.8",  unit: "%",    delta: "▲ +7.7pp", good: true  },
  { label: "Waste Recovery",value: "85.8",  unit: "%",    delta: "▲ +0.8pp", good: true  },
];

const TABLE_ROWS = [
  { kpi: "CO₂ intensity",       y2021: "0.684", y2022: "0.576", y2023: "0.551", unit: "T.CO₂/T",  trend: "▼ improving", trendClass: "text-green-600" },
  { kpi: "Energy intensity",    y2021: "9.7",   y2022: "9.1",   y2023: "8.7",   unit: "GJ/T",      trend: "▼ improving", trendClass: "text-green-600" },
  { kpi: "Renewable electricity",y2021:"20.1%",  y2022: "31.1%", y2023: "38.8%", unit: "%",         trend: "▲ improving", trendClass: "text-green-600" },
  { kpi: "Water intensity",     y2021: "5.71",  y2022: "5.73",  y2023: "5.78",  unit: "m³/T",      trend: "▲ watch",     trendClass: "text-red-500"   },
  { kpi: "Waste recovery",      y2021: "83.2%", y2022: "85.0%", y2023: "85.8%", unit: "%",         trend: "▲ improving", trendClass: "text-green-600" },
  { kpi: "ISO 14001 coverage",  y2021: "100%",  y2022: "100%",  y2023: "100%",  unit: "%",         trend: "→ maintained",trendClass: "text-gray-400"  },
];

const OPT = {
  responsive: true, maintainAspectRatio: false,
  animation: { duration: 900, easing: "easeOutQuart" },
  plugins: { legend: { display: false }, tooltip: { backgroundColor: "#0E1117", titleColor: "#fff", bodyColor: "rgba(255,255,255,.65)", borderColor: "rgba(255,255,255,.1)", borderWidth: 1, padding: 8, cornerRadius: 6 } },
  scales: { x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } }, y: { grid: { color: "rgba(0,0,0,.04)" }, ticks: { color: "#94A3B8", font: { size: 10 } } } },
};

onMounted(() => {
  if (co2Chart.value) {
    new Chart(co2Chart.value, {
      type: "line",
      data: { labels: ["2019","2020","2021","2022","2023"], datasets: [{ data: [2.5,2.42,2.27,2.06,2.05], borderColor: "#0E1117", backgroundColor: "rgba(14,17,23,.07)", fill: true, tension: 0.4, pointRadius: 4, borderWidth: 2 }] },
      options: OPT,
    });
  }
  if (fuelChart.value) {
    new Chart(fuelChart.value, {
      type: "doughnut",
      data: {
        labels: ["Natural Gas","Electricity","LPG","Coal","Other"],
        datasets: [{ data: [50,41,4.2,1.2,3.6], backgroundColor: ["#0E1117","#0891B2","#F59E0B","#78716C","#94A3B8"], borderWidth: 0, hoverOffset: 5 }],
      },
      options: { ...OPT, scales: undefined, cutout: "55%", plugins: { legend: { display: true, position: "right", labels: { color: "#64748B", boxWidth: 9, font: { size: 11 } } }, tooltip: OPT.plugins.tooltip } },
    });
  }
});
</script>
