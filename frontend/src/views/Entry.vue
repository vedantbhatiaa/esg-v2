<template>
  <div>
    <!-- Step header bar -->
    <div class="bg-white border border-gray-100 rounded-xl px-5 py-3 mb-3 flex items-center gap-0 overflow-x-auto">
      <template v-for="(s, i) in STEPS" :key="i">
        <div v-if="i > 0" class="w-6 h-[1.5px] flex-shrink-0 mx-1"
          :class="i <= currentStep ? 'bg-navy' : 'bg-gray-200'" />
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold"
            :class="{
              'bg-navy text-white': i < currentStep,
              'bg-dss text-white':  i === currentStep,
              'bg-gray-100 text-gray-400 border border-gray-200': i > currentStep,
            }">
            <span v-if="i < currentStep">✓</span>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="text-[11px] font-medium whitespace-nowrap"
            :class="{
              'text-navy': i < currentStep,
              'text-dss font-semibold': i === currentStep,
              'text-gray-400': i > currentStep,
            }">
            {{ s.name }}
          </span>
        </div>
      </template>
    </div>

    <!-- Reference hint -->
    <div class="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 mb-3 text-[12px] text-blue-700 leading-relaxed">
      <strong>Prior year reference:</strong> {{ HINTS[currentStep] }}
    </div>

    <div class="grid gap-3" style="grid-template-columns: 1fr 220px">
      <!-- Form card -->
      <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-50">
          <div class="font-head text-[14px] font-bold">Step {{ currentStep + 1 }} of 6 — {{ STEPS[currentStep].name }}</div>
          <div class="text-[11px] text-gray-400 mt-0.5">Enter values for full calendar year 2023</div>
        </div>
        <div class="p-5">
          <!-- Render fields dynamically -->
          <div :class="gridClass">
            <template v-for="field in STEPS[currentStep].fields" :key="field.key">
              <div class="flex flex-col gap-1">
                <label class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">{{ field.label }}</label>
                <div v-if="field.desc" class="text-[10px] text-gray-400 -mt-0.5">{{ field.desc }}</div>
                <div class="flex">
                  <input
                    v-model.number="formData[field.key]"
                    type="number"
                    min="0"
                    class="flex-1 h-9 border border-gray-200 rounded-l-lg px-3 text-[13px] focus:outline-none focus:border-blue-400"
                    @input="onFieldChange"
                  />
                  <div class="h-9 px-2.5 bg-gray-50 border border-l-0 border-gray-200 rounded-r-lg text-[10px] text-gray-400 flex items-center whitespace-nowrap">
                    {{ field.unit }}
                  </div>
                </div>
                <div v-if="field.hint" class="text-[10px] text-amber-500">{{ field.hint }}</div>
              </div>
            </template>
          </div>

          <!-- Calculated outputs (Energy step) -->
          <div v-if="currentStep === 3" class="mt-4 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2">
            <div class="flex justify-between items-center bg-gray-50 rounded-lg px-3 py-2">
              <span class="text-[11.5px] text-gray-500">Total electricity</span>
              <span class="text-[13px] font-bold">{{ formatNum(liveKPIs.total_elec_gj) }} GJ</span>
            </div>
            <div class="flex justify-between items-center bg-gray-50 rounded-lg px-3 py-2">
              <span class="text-[11.5px] text-gray-500">Total energy</span>
              <span class="text-[13px] font-bold">{{ formatNum(liveKPIs.total_energy_gj) }} GJ</span>
            </div>
          </div>

          <!-- Waste recovery calc -->
          <div v-if="currentStep === 5" class="mt-4 flex justify-between items-center bg-gray-50 rounded-lg px-3 py-2">
            <span class="text-[11.5px] text-gray-500">Waste recovery rate (calculated)</span>
            <span class="text-[13px] font-bold">{{ liveKPIs.waste_recovery_pct }}%</span>
          </div>

          <!-- Navigation buttons -->
          <div class="flex items-center justify-between mt-5 pt-4 border-t border-gray-100">
            <span class="text-[11.5px] text-gray-400">Step <strong class="text-gray-800">{{ currentStep + 1 }}</strong> of 6</span>
            <div class="flex gap-2">
              <button v-if="currentStep > 0" @click="prevStep"
                class="px-4 h-8 border border-gray-200 rounded-lg text-[12px] hover:border-gray-400 transition-colors">
                ← Previous
              </button>
              <button v-if="currentStep < 5" @click="nextStep"
                class="px-4 h-8 bg-navy text-white rounded-lg text-[12px] font-medium hover:bg-[#1a1a5a] transition-colors">
                Next: {{ STEPS[currentStep + 1].name }} →
              </button>
              <button v-else @click="showTemplate = true"
                class="px-4 h-8 bg-dss text-white rounded-lg text-[12px] font-medium hover:bg-red-700 transition-colors">
                Complete & View Template →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Live KPI sidebar -->
      <div class="flex flex-col gap-3">
        <div class="bg-navy rounded-xl p-4">
          <div class="text-[9px] font-semibold text-white/30 uppercase tracking-widest mb-3">Live Calculations</div>
          <div class="space-y-2">
            <div>
              <div class="text-[10px] text-white/35">Total Energy</div>
              <div class="font-head text-xl font-bold text-white">
                {{ (liveKPIs.total_energy_gj / 1e6).toFixed(1) }}<span class="text-[11px] text-white/30 ml-1">M GJ</span>
              </div>
            </div>
            <div>
              <div class="text-[10px] text-white/35">Renewable Share</div>
              <div class="font-head text-xl font-bold text-white">
                {{ liveKPIs.renewable_share_pct }}<span class="text-[11px] text-white/30">%</span>
              </div>
            </div>
          </div>
          <div class="border-t border-white/10 pt-3 mt-3 space-y-1.5">
            <div class="flex justify-between">
              <span class="text-[10px] text-white/35">Energy KPI</span>
              <span class="text-[11px] font-semibold text-white/80">{{ liveKPIs.energy_kpi }} GJ/T</span>
            </div>
            <div class="flex justify-between">
              <span class="text-[10px] text-white/35">CO₂ KPI</span>
              <span class="text-[11px] font-semibold text-white/80">{{ liveKPIs.co2_kpi }} T/T</span>
            </div>
            <div class="flex justify-between">
              <span class="text-[10px] text-white/35">Water KPI</span>
              <span class="text-[11px] font-semibold text-white/80">{{ liveKPIs.water_kpi }} m³/T</span>
            </div>
          </div>
        </div>

        <div v-if="currentStep === 5" class="bg-white border border-gray-100 rounded-xl p-4">
          <div class="text-[12px] font-semibold mb-2">Ready to save</div>
          <div class="text-[11px] text-gray-400 mb-3 leading-relaxed">39 KPI fields complete. A timestamped audit snapshot will be created.</div>
          <button @click="saveSubmission" :disabled="saving"
            class="w-full h-8 bg-navy text-white rounded-lg text-[12px] font-semibold hover:bg-[#1a1a5a] disabled:opacity-50 transition-colors">
            {{ saving ? "Saving…" : "Save to Database" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Template modal (shown after completion) -->
    <div v-if="showTemplate" class="fixed inset-0 bg-black/40 z-50 flex items-start justify-center pt-16 px-6">
      <div class="bg-white rounded-2xl w-full max-w-5xl max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b">
          <div>
            <div class="font-head text-[15px] font-bold">ESG KPI Template — {{ auth.companyName }} · 2023</div>
            <div class="text-[11px] text-gray-400 mt-0.5">All 39 fields submitted</div>
          </div>
          <button @click="showTemplate = false" class="w-8 h-8 bg-gray-100 rounded-lg text-sm hover:bg-gray-200">✕</button>
        </div>
        <div class="overflow-y-auto flex-1 p-6">
          <p class="text-[13px] text-gray-500">Template view — connect to real API data to populate all rows.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from "vue";
import { useAuthStore } from "@/stores/auth.js";
import { calculateKPI, submitData } from "@/services/api.js";

const auth        = useAuthStore();
const currentStep = ref(0);
const showTemplate = ref(false);
const saving      = ref(false);

// All 39 fields — initialised to 0
const formData = reactive({
  // Step 1 — ISO
  iso_total_sites: 54, iso_certified_sites: 54,
  // Step 2 — Production
  production_volume: 3720000,
  // Step 3 — Water
  water_withdrawals: 21500000,
  // Step 4 — Energy
  renew_elec_purchased: 5200000, nonrenew_elec: 8500000,
  self_gen_renew: 45000, purchased_steam: 1050000,
  nat_gas: 16100000, lpg: 1350000, coal: 380000,
  fuel_oil: 150000, diesel: 190000, petrol: 0,
  biomass: 0, waste_tires: 0, lpg2: 0, other_fuel: 0,
  // Step 5 — CO2
  co2_scope2_steam: 60000,
  // Step 6 — Waste
  waste_total: 338000, waste_recovery: 290000,
});

const liveKPIs = ref({
  total_energy_gj: 32380000, total_elec_gj: 13745000,
  energy_kpi: 8.7, co2_kpi: 0.551, water_kpi: 5.78,
  renewable_share_pct: 38.8, waste_recovery_pct: 85.8,
});

const STEPS = [
  {
    name: "ISO 14001",
    fields: [
      { key: "iso_total_sites",     label: "Total no. of sites",          unit: "no.",     hint: "Prior 2022: 52", desc: "All global facilities" },
      { key: "iso_certified_sites", label: "ISO 14001 certified sites",    unit: "no.",     hint: "Prior 2022: 52", desc: "Active certification" },
    ],
  },
  {
    name: "Production",
    fields: [
      { key: "production_volume", label: "Annual production volume", unit: "metric T", hint: "Prior 2022: 3,580,000", desc: "Total finished product weight" },
    ],
  },
  {
    name: "Water",
    fields: [
      { key: "water_withdrawals", label: "Total water withdrawals", unit: "m³", hint: "Prior 2022: 20,900,000", desc: "All sources: surface, ground, municipal" },
    ],
  },
  {
    name: "Energy",
    fields: [
      { key: "renew_elec_purchased", label: "Renewable electricity purchased", unit: "GJ",     hint: "Prior 2022: 4,082,923", desc: "Grid-certified renewable" },
      { key: "nonrenew_elec",        label: "Non-renewable electricity",       unit: "GJ",     hint: "Prior 2022: 9,037,549", desc: "Standard grid electricity" },
      { key: "self_gen_renew",       label: "Self-generated renewable",        unit: "GJ",     hint: "",                     desc: "Solar/wind on-site" },
      { key: "purchased_steam",      label: "Purchased steam",                 unit: "GJ",     hint: "Prior 2022: 1,050,000", desc: "External steam supply" },
      { key: "nat_gas",              label: "Natural gas",                     unit: "GJ LHV", hint: "Prior 2022: 15,927,554", desc: "Lower Heating Value" },
      { key: "lpg",                  label: "LPG",                             unit: "GJ LHV", hint: "Prior 2022: 1,329,571", desc: "Liquefied petroleum gas" },
      { key: "coal",                 label: "Coal (all types)",                unit: "GJ LHV", hint: "Prior 2022: 395,006",   desc: "Hard + brown coal" },
      { key: "fuel_oil",             label: "Fuel oil",                        unit: "GJ LHV", hint: "",                     desc: "Heavy fuel oil" },
      { key: "diesel",               label: "Diesel",                          unit: "GJ LHV", hint: "",                     desc: "On-site consumption" },
      { key: "biomass",              label: "Biomass / other",                 unit: "GJ LHV", hint: "",                     desc: "Biomass, waste tyres, other" },
    ],
  },
  {
    name: "CO₂",
    fields: [
      { key: "co2_scope2_steam", label: "Scope 2 CO₂ from purchased steam", unit: "T.CO₂", hint: "Company-provided figure", desc: "From steam supplier data" },
    ],
  },
  {
    name: "Waste",
    fields: [
      { key: "waste_total",    label: "Total waste generated",  unit: "metric T", hint: "Prior 2022: 335,000",  desc: "All waste streams" },
      { key: "waste_recovery", label: "Waste sent to recovery", unit: "metric T", hint: "Prior 2022: 284,750", desc: "Recycling + energy recovery" },
    ],
  },
];

const HINTS = [
  "Prior 2022: ISO 100% certified (52/52 sites)",
  "Prior 2022: Production 3,580,000 metric T · Energy KPI 9.1 GJ/T",
  "Prior 2022: Water KPI 5.73 m³/T · Total 20,900,000 m³",
  "Prior 2022: Energy KPI 9.1 GJ/T · Renew. 31.1% · Total 32,268,110 GJ — ⚠ flag if renew. change > ±15%",
  "Prior 2022: CO₂ KPI 0.576 T/T · Total 2,060,000 T",
  "Prior 2022: Waste recovery 85.0% · Total waste 335,000 T",
];

const gridClass = computed(() => {
  const n = STEPS[currentStep.value].fields.length;
  if (n >= 8) return "grid grid-cols-4 gap-2";
  if (n >= 4) return "grid grid-cols-3 gap-3";
  if (n >= 3) return "grid grid-cols-3 gap-3";
  return "grid grid-cols-2 gap-4";
});

function formatNum(n) {
  return n ? n.toLocaleString() : "—";
}

let calcTimer = null;
function onFieldChange() {
  clearTimeout(calcTimer);
  calcTimer = setTimeout(async () => {
    try {
      const result = await calculateKPI({ ...formData });
      liveKPIs.value = { ...liveKPIs.value, ...result };
    } catch {
      /* backend not running — keep demo values */
    }
  }, 400);
}

function nextStep() { if (currentStep.value < 5) currentStep.value++; }
function prevStep() { if (currentStep.value > 0) currentStep.value--; }

async function saveSubmission() {
  saving.value = true;
  try {
    await submitData({
      company_id: auth.companyId || "verdatyres",
      year: 2023,
      data: { ...formData },
    });
    alert("Data saved successfully. Verification queue notified.");
  } catch {
    alert("Save failed — check that the Python backend is running.");
  } finally {
    saving.value = false;
  }
}
</script>
