<template>
  <div>
    <!-- Filter bar -->
    <div class="flex gap-2 mb-4 flex-wrap items-center">
      <select class="h-7 border border-gray-200 rounded-lg px-2 text-[12px] bg-white">
        <option>All companies</option>
        <option>EpsilonWheel Co</option>
        <option>VerdaTyres Corp</option>
      </select>
      <select class="h-7 border border-gray-200 rounded-lg px-2 text-[12px] bg-white">
        <option>All flags</option>
        <option>Errors only</option>
        <option>Warnings only</option>
      </select>
      <select class="h-7 border border-gray-200 rounded-lg px-2 text-[12px] bg-white">
        <option>Year: 2023</option>
        <option>Year: 2022</option>
      </select>
      <div class="ml-auto flex gap-2">
        <div class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1 text-[12px] text-gray-500">8 / 10 submitted</div>
        <div class="bg-red-50 border border-red-200 rounded-lg px-3 py-1 text-[12px] text-red-700 font-semibold">3 require action</div>
      </div>
    </div>

    <div class="grid gap-3" style="grid-template-columns: 3fr 2fr">
      <!-- Verification queue -->
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-50 text-[13px] font-semibold">Verification Queue</div>
        <div class="overflow-x-auto">
          <table class="w-full text-[12px] border-collapse">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Company</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">KPI</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Value</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">YoY</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Flag</th>
                <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Status</th>
                <th class="px-3 py-2.5 border-b border-gray-100"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in QUEUE" :key="row.id"
                :class="row.severity === 'error' ? 'bg-red-50/60' : row.severity === 'warning' ? 'bg-yellow-50/60' : ''"
                class="border-b border-gray-50 last:border-none">
                <td class="px-4 py-2.5 font-semibold">{{ row.company }}</td>
                <td class="px-3 py-2.5">{{ row.kpi }}</td>
                <td class="px-3 py-2.5 tabular-nums">{{ row.value }}</td>
                <td class="px-3 py-2.5 tabular-nums font-semibold"
                  :class="row.yoy?.includes('+') && row.severity==='error' ? 'text-red-500' : row.yoy?.includes('+') ? 'text-amber-500' : 'text-green-600'">
                  {{ row.yoy }}
                </td>
                <td class="px-3 py-2.5">
                  <span class="text-[10px] font-semibold px-2 py-0.5 rounded border"
                    :class="{
                      'bg-red-50 text-red-600 border-red-200': row.severity === 'error',
                      'bg-yellow-50 text-yellow-700 border-yellow-200': row.severity === 'warning',
                      'bg-green-50 text-green-700 border-green-200': row.severity === 'ok',
                    }">
                    {{ row.severity === 'error' ? 'Error' : row.severity === 'warning' ? 'Warning' : 'OK' }}
                  </span>
                </td>
                <td class="px-3 py-2.5">
                  <span class="text-[10px] font-semibold px-2 py-0.5 rounded border"
                    :class="{
                      'bg-gray-50 text-gray-500 border-gray-200': row.status === 'pending',
                      'bg-blue-50 text-blue-600 border-blue-200': row.status === 'review',
                      'bg-green-50 text-green-700 border-green-200': row.status === 'verified',
                    }">
                    {{ row.status === 'pending' ? 'Pending' : row.status === 'review' ? 'In Review' : 'Verified' }}
                  </span>
                </td>
                <td class="px-3 py-2.5">
                  <button @click="openSlideOver(row)"
                    class="px-2.5 h-6 border border-gray-200 rounded text-[11px] hover:border-navy hover:text-navy transition-colors">
                    Review
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right column: status pie + rules -->
      <div class="flex flex-col gap-3">
        <div class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-[13px] font-semibold mb-3">Cycle Status</div>
          <div class="h-32 mb-3"><canvas ref="statusPie"></canvas></div>
          <div class="space-y-1.5 text-[11.5px]">
            <div class="flex justify-between"><span class="text-gray-500">Submitted:</span><span class="font-semibold">8 / 10</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Verified:</span><span class="font-semibold text-green-600">5</span></div>
            <div class="flex justify-between"><span class="text-gray-500">Action needed:</span><span class="font-semibold text-red-600">2</span></div>
            <div class="flex justify-between"><span class="text-gray-500">In Review:</span><span class="font-semibold text-amber-500">1</span></div>
          </div>
        </div>
        <div class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-[13px] font-semibold mb-2">Auto-Flag Rules Active</div>
          <div class="space-y-1.5 text-[11.5px] text-gray-500">
            <div>⚠ Warning: YoY change &gt; ±15%</div>
            <div>✗ Error: YoY change &gt; ±30%</div>
            <div>✗ Error: ISO certified sites &gt; total sites</div>
            <div>✗ Error: Recovery rate &gt; 100%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Slide-over panel -->
    <div v-if="selectedRow" class="fixed inset-0 z-50 flex justify-end">
      <div class="absolute inset-0 bg-black/20" @click="selectedRow = null"></div>
      <div class="relative w-[480px] bg-white h-full shadow-2xl overflow-y-auto">
        <div class="px-5 py-4 border-b flex items-center justify-between">
          <div>
            <div class="text-[14px] font-bold">{{ selectedRow.company }} — Verification</div>
            <div class="text-[11px] text-gray-400 mt-0.5">2023 · {{ selectedRow.kpi }}</div>
          </div>
          <button @click="selectedRow = null" class="w-7 h-7 bg-gray-100 rounded-lg text-sm hover:bg-gray-200">✕</button>
        </div>
        <div class="p-5">
          <div class="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
            <div class="text-[12px] font-semibold text-red-700">{{ selectedRow.message }}</div>
            <div class="text-[10.5px] text-red-600 mt-1">Current: {{ selectedRow.value }} · YoY: {{ selectedRow.yoy }}</div>
          </div>
          <div class="text-[12px] font-semibold mb-2 mt-4">Analyst action</div>
          <textarea class="w-full h-20 border border-gray-200 rounded-lg p-3 text-[12px] resize-none focus:outline-none focus:border-blue-300"
            placeholder="Add verification comment…"></textarea>
          <div class="flex gap-2 mt-3">
            <button class="flex-1 h-8 bg-navy text-white rounded-lg text-[12px] font-semibold hover:bg-[#1a1a5a] transition-colors">Request Re-submit</button>
            <button class="flex-1 h-8 border border-green-400 text-green-600 rounded-lg text-[12px] font-semibold hover:bg-green-50 transition-colors">Approve with Note</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

const statusPie  = ref(null);
const selectedRow = ref(null);

const QUEUE = [
  { id:1, company:"EpsilonWheel Co", kpi:"Total CO₂",     value:"2,818,000 T",  yoy:"+34.2%", severity:"error",   status:"pending", message:"CO₂ +34.2% YoY — exceeds ±30% error threshold" },
  { id:2, company:"EpsilonWheel Co", kpi:"ISO Sites",      value:"56/52",        yoy:"—",      severity:"error",   status:"pending", message:"Certified sites (56) exceeds total sites (52) — logical impossibility" },
  { id:3, company:"VerdaTyres Corp", kpi:"Renew. Elec.",   value:"5,200,000 GJ", yoy:"+27.3%", severity:"warning", status:"review",  message:"Renewable electricity +27.3% YoY — exceeds ±15% warning threshold" },
  { id:4, company:"EpsilonWheel Co", kpi:"Natural Gas",    value:"17,342,000 GJ",yoy:"+22.1%", severity:"warning", status:"pending", message:"Natural gas +22.1% YoY — review required" },
  { id:5, company:"DeltaGrip GmbH",  kpi:"All KPIs",       value:"—",            yoy:"—",      severity:"ok",      status:"verified",message:"All values within expected range" },
  { id:6, company:"AlphaTread Ltd",  kpi:"All KPIs",       value:"—",            yoy:"—",      severity:"ok",      status:"verified",message:"All values within expected range" },
];

function openSlideOver(row) { selectedRow.value = row; }

onMounted(() => {
  if (statusPie.value) {
    new Chart(statusPie.value, {
      type: "doughnut",
      data: {
        labels: ["Verified","In Review","Action Req.","Pending"],
        datasets: [{ data: [5,1,2,2], backgroundColor: ["#16A34A","#F59E0B","#DC2626","#E2E8F0"], borderWidth: 0, hoverOffset: 4 }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: "65%",
        plugins: { legend: { display: true, position: "bottom", labels: { color: "#64748B", boxWidth: 8, font: { size: 10 } } } },
      },
    });
  }
});
</script>
