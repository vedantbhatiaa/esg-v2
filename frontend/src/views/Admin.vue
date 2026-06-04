<template>
  <div>
    <h2 class="text-xl font-bold text-gray-900 mb-1">Admin</h2>
    <p class="text-sm text-gray-400 mb-5">Platform administration · dss+ internal only</p>

    <!-- Summary cards -->
    <div class="grid grid-cols-4 gap-3 mb-5">
      <div v-for="m in summary" :key="m.label" class="bg-white border border-gray-100 rounded-xl p-4">
        <div class="text-xs text-gray-400 mb-1">{{ m.label }}</div>
        <div class="text-2xl font-bold text-navy">{{ m.value }}</div>
        <div class="text-xs text-gray-400">{{ m.unit }}</div>
      </div>
    </div>

    <!-- Companies table -->
    <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 text-sm font-semibold">
        All Companies — Submission Status
      </div>
      <div v-if="loading" class="px-5 py-8 text-center text-sm text-gray-400">Loading…</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs border-collapse">
          <thead><tr class="bg-gray-50">
            <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Company</th>
            <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">ID</th>
            <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Email</th>
            <th class="px-4 py-2.5 text-left text-[9px] font-bold text-gray-400 uppercase border-b border-gray-100">Status</th>
          </tr></thead>
          <tbody>
            <tr v-for="co in companies" :key="co.id"
              class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-2.5 font-semibold text-navy">{{ co.name }}</td>
              <td class="px-4 py-2.5 text-gray-500 font-mono text-[11px]">{{ co.id }}</td>
              <td class="px-4 py-2.5 text-gray-500">{{ co.email }}</td>
              <td class="px-4 py-2.5">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold"
                  :class="co.submission_status==='submitted'?'bg-green-100 text-green-700':'bg-yellow-100 text-yellow-700'">
                  {{ co.submission_status || 'pending' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "@/services/api.js";

const loading   = ref(false);
const companies = ref([]);

const summary = computed(() => [
  { label:"Total Companies", value:companies.value.length,                                          unit:"registered" },
  { label:"Submitted",       value:companies.value.filter(c=>c.submission_status==="submitted").length, unit:"this cycle" },
  { label:"Pending",         value:companies.value.filter(c=>c.submission_status!=="submitted").length, unit:"not submitted" },
  { label:"Platform",        value:"V2",                                                            unit:"Vue 3 + Python" },
]);

async function load() {
  loading.value = true;
  try {
    const res = await api.getCompanies({ year: 2023 });
    // getCompanies normalises to names - we need full objects, fetch raw
    const raw = await fetch("/api/companies?year=2023").then(r=>r.json()).catch(()=>[]);
    companies.value = Array.isArray(raw) && raw.length && typeof raw[0]==="object" ? raw : [];
  } catch(e) { console.error("Admin:", e); }
  finally { loading.value = false; }
}

onMounted(load);
</script>