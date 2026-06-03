<template>
  <div>
    <!-- Filter bar -->
    <div class="flex gap-2 items-center mb-4 flex-wrap">
      <div class="flex gap-1.5">
        <button v-for="f in FILTERS" :key="f.value"
          @click="activeFilter = f.value"
          class="px-3 py-1.5 rounded-xl text-[11px] font-medium border transition-all"
          :class="activeFilter === f.value
            ? 'bg-navy text-white border-navy'
            : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'">
          {{ f.label }}
        </button>
      </div>
      <div class="ml-auto flex gap-2">
        <select class="h-7 border border-gray-200 rounded-lg px-2 text-[12px] bg-white">
          <option>Sector avg. (10 co.)</option>
          <option>VerdaTyres Corp</option>
        </select>
        <select class="h-7 border border-gray-200 rounded-lg px-2 text-[12px] bg-white">
          <option>2009–2023</option>
          <option>2018–2023</option>
        </select>
      </div>
    </div>

    <!-- Energy section -->
    <template v-if="show('energy')">
      <SectionHeader title="⚡ Energy KPIs" color="#F59E0B" />
      <div class="grid grid-cols-2 gap-3 mb-4">
        <ChartCard title="Energy Intensity KPI" subtitle="GJ / metric tonne · 2009–2023">
          <canvas ref="energyKpiChart"></canvas>
        </ChartCard>
        <ChartCard title="Fuel Mix — % of Total Energy" subtitle="Stacked area · 2009–2023">
          <canvas ref="fuelMixChart"></canvas>
        </ChartCard>
        <ChartCard title="Renewable Electricity Share" subtitle="% of total electricity">
          <canvas ref="renewChart"></canvas>
        </ChartCard>
        <ChartCard title="Fossil Energy Share" subtitle="% from fossil fuels">
          <canvas ref="fossilChart"></canvas>
        </ChartCard>
      </div>
    </template>

    <!-- CO2 section -->
    <template v-if="show('co2')">
      <SectionHeader title="CO₂ Emissions" color="#0E1117" />
      <div class="grid grid-cols-2 gap-3 mb-4">
        <ChartCard title="Total CO₂ — Scope 1 & 2" subtitle="Million T.CO₂ · 2009–2023">
          <canvas ref="co2Chart"></canvas>
        </ChartCard>
        <ChartCard title="CO₂ Intensity KPI" subtitle="T.CO₂ / metric tonne">
          <canvas ref="co2KpiChart"></canvas>
        </ChartCard>
        <ChartCard title="Scope 1 vs Scope 2 — 2023" subtitle="Breakdown by source">
          <canvas ref="scopeDonut"></canvas>
        </ChartCard>
        <ChartCard title="Production Volume" subtitle="Million metric T · 2009–2023">
          <canvas ref="prodChart"></canvas>
        </ChartCard>
      </div>
    </template>

    <!-- Water section -->
    <template v-if="show('water')">
      <SectionHeader title="💧 Water" color="#0891B2" />
      <div class="grid grid-cols-2 gap-3 mb-4">
        <ChartCard title="Total Water Withdrawals" subtitle="Million m³ · 2009–2023">
          <canvas ref="waterChart"></canvas>
        </ChartCard>
        <ChartCard title="Water Intensity KPI" subtitle="m³ / metric tonne">
          <canvas ref="waterKpiChart"></canvas>
        </ChartCard>
      </div>
    </template>

    <!-- Waste section -->
    <template v-if="show('waste')">
      <SectionHeader title="♻ Waste" color="#7C3AED" />
      <div class="grid grid-cols-2 gap-3 mb-4">
        <ChartCard title="Waste Recovery Rate" subtitle="% recovered · 2009–2023">
          <canvas ref="wasteRateChart"></canvas>
        </ChartCard>
        <ChartCard title="Waste Volume Generated" subtitle="Thousand metric T">
          <canvas ref="wasteVolChart"></canvas>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from "vue";
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

const activeFilter = ref("all");
const FILTERS = [
  { value: "all",    label: "All KPIs" },
  { value: "energy", label: "Energy"   },
  { value: "co2",    label: "CO₂"      },
  { value: "water",  label: "Water"    },
  { value: "waste",  label: "Waste"    },
];
function show(section) {
  return activeFilter.value === "all" || activeFilter.value === section;
}

// Section header component
const SectionHeader = defineComponent({
  props: { title: String, color: String },
  setup(props) {
    return () => h("div", {
      class: "font-head text-[13px] font-bold mb-2 pb-1 inline-block",
      style: `border-bottom: 2.5px solid ${props.color}`
    }, props.title);
  },
});

// Chart card wrapper
const ChartCard = defineComponent({
  props: { title: String, subtitle: String },
  setup(props, { slots }) {
    return () => h("div", { class: "bg-white border border-gray-100 rounded-xl overflow-hidden" }, [
      h("div", { class: "px-4 pt-3 pb-2 border-b border-gray-50" }, [
        h("div", { class: "text-[13px] font-semibold" }, props.title),
        h("div", { class: "text-[11px] text-gray-400 mt-0.5" }, props.subtitle),
      ]),
      h("div", { class: "p-4" }, [
        h("div", { style: "height: 162px" }, slots.default?.()),
      ]),
    ]);
  },
});

// Data
const Y  = ["'09","'10","'11","'12","'13","'14","'15","'16","'17","'18","'19","'20","'21","'22","'23"];
const DATA = {
  enk:  [10.8,10.5,10.2,10.0,9.8,9.6,9.5,9.4,9.3,9.2,9.1,9.7,9.7,9.1,8.7],
  ren:  [2,2,3,3,4,5,6,7,9,12,16,22,20,31,38.8],
  foss: [99,98.5,98,97.5,97,96,95,94,93,92,90,86,84,72,65],
  fN:   [50,50,50,51,51,51,51,51,51,51,51,51,51,50,50],
  fE:   [38,38,38,38,39,39,39,39,39,39,39,40,40,41,41],
  fL:   [4,4,4,4,3.5,3.5,3.5,3.5,3.5,3.5,3.5,3,3,3,4.2],
  fC:   [4,3.5,3.5,3,3,3,3,2.5,2,2,2,2,2,2,1.2],
  co2:  [3.1,3.0,2.9,2.85,2.8,2.78,2.72,2.65,2.6,2.55,2.5,2.42,2.27,2.06,2.05],
  co2k: [0.82,0.79,0.76,0.74,0.72,0.71,0.69,0.67,0.66,0.64,0.63,0.60,0.58,0.576,0.551],
  s1:   [1.8,1.75,1.7,1.65,1.62,1.60,1.56,1.52,1.50,1.48,1.45,1.40,1.32,1.05,1.03],
  wa:   [16,16.2,16.5,16.8,17,17.2,17.5,17.8,18,18.5,18.3,18.8,19,20.9,21.5],
  wkp:  [7.2,7.0,6.8,6.6,6.5,6.4,6.3,6.2,6.1,6.0,5.9,5.85,5.71,5.73,5.78],
  wrc:  [78,79,80,80,81,81,82,82,82,83,83,83,83,85,85.8],
  wv:   [250,255,260,268,275,280,285,290,292,298,302,308,315,335,338],
  prd:  [2.4,2.5,2.6,2.7,2.8,2.9,2.95,3.0,3.05,3.15,3.2,2.9,3.32,3.58,3.72],
};

const BASE_OPTS = {
  responsive: true, maintainAspectRatio: false,
  animation: { duration: 900, easing: "easeOutQuart" },
  plugins: { legend: { display: false }, tooltip: { backgroundColor: "#0E1117", titleColor: "#fff", bodyColor: "rgba(255,255,255,.65)", borderColor: "rgba(255,255,255,.1)", borderWidth: 1, padding: 8, cornerRadius: 6 } },
  scales: { x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } }, y: { grid: { color: "rgba(0,0,0,.04)" }, ticks: { color: "#94A3B8", font: { size: 10 } } } },
};
const LG = { display: true, position: "top", labels: { color: "#64748B", boxWidth: 9, font: { size: 11 }, padding: 9 } };

// Chart refs
const energyKpiChart = ref(null); const fuelMixChart = ref(null);
const renewChart = ref(null);     const fossilChart = ref(null);
const co2Chart = ref(null);       const co2KpiChart = ref(null);
const scopeDonut = ref(null);     const prodChart = ref(null);
const waterChart = ref(null);     const waterKpiChart = ref(null);
const wasteRateChart = ref(null); const wasteVolChart = ref(null);

function mk(el, type, data, extra = {}) {
  if (!el.value) return;
  new Chart(el.value, { type, data, options: { ...BASE_OPTS, ...extra } });
}

function line(data, color, fill = true) {
  return { data, borderColor: color, backgroundColor: color.replace(")", ",.07)").replace("rgb", "rgba"), fill, tension: 0.4, pointRadius: 2, borderWidth: 2 };
}
function bar(data, color) {
  return { data, backgroundColor: color, borderRadius: 3 };
}

onMounted(() => {
  mk(energyKpiChart, "bar", { labels: Y, datasets: [{ ...bar(DATA.enk, "rgba(14,17,23,.55)"), backgroundColor: DATA.enk.map((_,i) => i===14 ? "#E31E24" : "rgba(14,17,23,.55)") }] });
  mk(fuelMixChart, "line", { labels: Y, datasets: [
    { label: "Nat. Gas", ...line(DATA.fN,"#0E1117"), fill: true, backgroundColor: "rgba(14,17,23,.13)" },
    { label: "Electricity", ...line(DATA.fE,"#0891B2"), fill: true, backgroundColor: "rgba(8,145,178,.09)" },
    { label: "LPG", ...line(DATA.fL,"#F59E0B"), fill: true, backgroundColor: "rgba(245,158,11,.08)" },
    { label: "Coal", ...line(DATA.fC,"#78716C"), fill: true, backgroundColor: "rgba(120,113,108,.08)" },
  ]}, { plugins: { legend: LG, tooltip: BASE_OPTS.plugins.tooltip } });
  mk(renewChart, "line", { labels: Y, datasets: [{ ...line(DATA.ren,"#16A34A"), pointRadius: 2, pointBackgroundColor: "#16A34A" }] });
  mk(fossilChart, "bar", { labels: Y, datasets: [bar(DATA.foss,"rgba(14,17,23,.5)")] });

  mk(co2Chart, "line", { labels: Y, datasets: [
    { label: "Scope 1", data: DATA.s1, borderColor: "#0E1117", backgroundColor: "rgba(14,17,23,.08)", fill: true, tension: 0.4, pointRadius: 2, borderWidth: 2 },
    { label: "Scope 2", data: DATA.co2.map((v,i)=>+(v-DATA.s1[i]).toFixed(2)), borderColor: "#0891B2", backgroundColor: "rgba(8,145,178,.06)", fill: true, tension: 0.4, pointRadius: 2, borderWidth: 2 },
  ]}, { plugins: { legend: LG, tooltip: BASE_OPTS.plugins.tooltip } });
  mk(co2KpiChart, "line", { labels: Y, datasets: [{ ...line(DATA.co2k,"#0E1117") }] });
  mk(scopeDonut, "doughnut", { labels: ["Scope 1 (Direct)","Scope 2 (Electricity)"], datasets: [{ data: [1.03,1.02], backgroundColor: ["#0E1117","#0891B2"], borderWidth: 0, hoverOffset: 5 }] },
    { scales: undefined, cutout: "62%", plugins: { legend: { display: true, position: "right", labels: { color: "#64748B", boxWidth: 9, font: { size: 11 } } }, tooltip: BASE_OPTS.plugins.tooltip } });
  mk(prodChart, "bar", { labels: Y, datasets: [bar(DATA.prd,"rgba(100,116,139,.45)")] });

  mk(waterChart, "bar", { labels: Y, datasets: [{ ...bar(DATA.wa,"rgba(8,145,178,.45)"), borderColor: "#0891B2", borderWidth: 1 }] });
  mk(waterKpiChart, "line", { labels: Y, datasets: [{ ...line(DATA.wkp,"#0891B2") }] });

  mk(wasteRateChart, "line", { labels: Y, datasets: [{ ...line(DATA.wrc,"#7C3AED"), pointBackgroundColor: "#7C3AED" }] });
  mk(wasteVolChart, "bar", { labels: Y, datasets: [bar(DATA.wv,"rgba(124,58,237,.4)")] });
});
</script>
