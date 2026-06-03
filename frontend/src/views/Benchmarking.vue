<template>
  <div>
    <!-- Band legend -->
    <div class="flex items-center gap-4 text-[10.5px] text-gray-500 mb-4 flex-wrap">
      <span class="font-semibold">Quartile bands:</span>
      <div class="flex items-center gap-1.5"><div class="w-4 h-2 rounded bg-green-100"></div>Top 25%</div>
      <div class="flex items-center gap-1.5"><div class="w-4 h-2 rounded bg-yellow-100"></div>Middle 50%</div>
      <div class="flex items-center gap-1.5"><div class="w-4 h-2 rounded bg-red-100"></div>Bottom 25%</div>
      <div class="flex items-center gap-1.5"><div class="w-0.5 h-4 bg-navy rounded"></div>Your position</div>
    </div>

    <!-- Quartile bands card -->
    <div class="bg-white border border-gray-100 rounded-xl mb-4">
      <div class="px-5 py-3 border-b border-gray-50">
        <div class="text-[13px] font-semibold">KPI Quartile Benchmarking — 2023</div>
        <div class="text-[11px] text-gray-400 mt-0.5">{{ auth.companyName || 'Your company' }} vs. all 10 TIP member companies</div>
      </div>
      <div class="p-5 space-y-4">
        <div v-for="band in BANDS" :key="band.key" class="flex items-center gap-3">
          <div class="text-[11.5px] font-medium w-48 flex-shrink-0 leading-tight">{{ band.label }}</div>
          <div class="flex-1 h-3.5 rounded bg-gray-100 relative">
            <!-- bottom 25% -->
            <div class="absolute top-0 left-0 h-full w-1/4 rounded-l-sm"
              :class="band.lowerBetter ? 'bg-green-100' : 'bg-red-100'"></div>
            <!-- middle 50% -->
            <div class="absolute top-0 left-1/4 h-full w-1/2 bg-yellow-100"></div>
            <!-- top 25% -->
            <div class="absolute top-0 left-3/4 h-full w-1/4 rounded-r-sm"
              :class="band.lowerBetter ? 'bg-red-100' : 'bg-green-100'"></div>
            <!-- position pin -->
            <div class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-0.5 h-5 bg-navy rounded"
              :style="{ left: band.position + '%' }">
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 text-[9px] font-bold text-navy whitespace-nowrap bg-white px-1 rounded border border-gray-200">
                {{ band.myVal }}
              </div>
            </div>
          </div>
          <div class="w-24 flex-shrink-0 text-right">
            <div class="text-[12px] font-bold font-head">{{ band.myVal }}</div>
            <div class="text-[10px] font-semibold" :class="band.rankColor">{{ band.rank }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scorecard table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-50">
        <div class="text-[13px] font-semibold">All Companies Scorecard — 2023</div>
        <div class="text-[11px] text-gray-400 mt-0.5">Anonymous peer comparison · dss+ verified</div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-[12.5px] border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Company</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">CO₂ KPI</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Energy KPI</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Renew.%</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Water KPI</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">ISO%</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Waste Rec.</th>
              <th class="px-3 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Rating</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in SCORECARD" :key="row.name"
              :class="row.isMe ? 'bg-indigo-50 font-semibold' : 'hover:bg-gray-50'"
              class="border-b border-gray-50 last:border-none">
              <td class="px-4 py-2.5">{{ row.name }}{{ row.isMe ? ' ◀' : '' }}</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.co2 <= 0.6 ? 'text-green-600' : 'text-red-500'">{{ row.co2 }}</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.enk <= 8.8 ? 'text-green-600' : 'text-red-500'">{{ row.enk }}</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.ren >= 40 ? 'text-green-600' : 'text-gray-500'">{{ row.ren }}%</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.wat <= 5.8 ? 'text-green-600' : 'text-red-500'">{{ row.wat }}</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.iso >= 95 ? 'text-green-600' : 'text-red-500'">{{ row.iso }}%</td>
              <td class="px-3 py-2.5 tabular-nums" :class="row.wrc >= 88 ? 'text-green-600' : 'text-gray-500'">{{ row.wrc }}%</td>
              <td class="px-3 py-2.5">
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded border"
                  :class="{
                    'bg-green-50 text-green-700 border-green-200': row.rating === 'Leader' || row.rating === 'Strong',
                    'bg-yellow-50 text-yellow-700 border-yellow-200': row.rating === 'Average',
                    'bg-red-50 text-red-600 border-red-200': row.rating === 'Review',
                  }">{{ row.rating }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from "@/stores/auth.js";
const auth = useAuthStore();

const BANDS = [
  { key: "co2",  label: "CO₂ Intensity (T.CO₂/T) ↓ better", myVal: "0.551", position: 28, rank: "Top 25%", rankColor: "text-green-600", lowerBetter: true  },
  { key: "enk",  label: "Energy Intensity (GJ/T) ↓ better",  myVal: "8.7",   position: 47, rank: "Average", rankColor: "text-gray-500",  lowerBetter: true  },
  { key: "ren",  label: "Renewable Electricity (%) ↑ better", myVal: "38.8%", position: 64, rank: "Top 25%", rankColor: "text-green-600", lowerBetter: false },
  { key: "wat",  label: "Water Intensity (m³/T) ↓ better",   myVal: "5.78",  position: 44, rank: "Average", rankColor: "text-gray-500",  lowerBetter: true  },
  { key: "iso",  label: "ISO 14001 Coverage (%) ↑ better",   myVal: "100%",  position: 91, rank: "Top 25%", rankColor: "text-green-600", lowerBetter: false },
  { key: "wrc",  label: "Waste Recovery (%) ↑ better",       myVal: "85.8%", position: 48, rank: "Average", rankColor: "text-gray-500",  lowerBetter: false },
];

const SCORECARD = [
  { name: "VerdaTyres Corp", isMe: true, co2: 0.551, enk: 8.7,  ren: 38.8, wat: 5.78, iso: 100, wrc: 85.8, rating: "Strong" },
  { name: "AlphaTread Ltd",  isMe: false, co2: 0.610, enk: 8.4,  ren: 52.1, wat: 5.42, iso: 100, wrc: 88.2, rating: "Strong" },
  { name: "DeltaGrip GmbH",  isMe: false, co2: 0.580, enk: 7.9,  ren: 60.0, wat: 5.20, iso: 100, wrc: 92.4, rating: "Leader" },
  { name: "GammaTire SA",    isMe: false, co2: 0.630, enk: 8.1,  ren: 35.0, wat: 5.65, iso:  94, wrc: 91.0, rating: "Strong" },
  { name: "Company E",       isMe: false, co2: 0.720, enk: 9.2,  ren: 28.4, wat: 6.10, iso:  82, wrc: 84.1, rating: "Average" },
  { name: "Company F",       isMe: false, co2: 0.690, enk: 9.0,  ren: 22.5, wat: 6.20, iso:  88, wrc: 82.0, rating: "Average" },
  { name: "Company G",       isMe: false, co2: 0.760, enk: 9.6,  ren: 18.0, wat: 6.55, iso:  76, wrc: 78.3, rating: "Review" },
];
</script>
