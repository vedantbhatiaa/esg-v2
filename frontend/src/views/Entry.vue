<template>
  <div>
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <div class="text-xl font-bold text-gray-900">{{ auth.companyName }}</div>
        <div class="text-sm text-gray-400 mt-0.5">ESG KPI Data Entry</div>
      </div>
      <div class="flex gap-2 items-center">
        <select v-model="selYear" class="h-8 border border-gray-200 rounded-lg px-2 text-sm bg-white">
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="selYear && !isNewYear" class="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2 text-sm text-blue-700 mb-3">
      Editing existing data for <strong>{{ selYear }}</strong> (pre-filled from database)
    </div>
    <div v-else-if="isNewYear" class="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2 text-sm text-blue-700 mb-3">
      Entering new data for <strong>{{ selYear }}</strong>
    </div>

    <div class="grid gap-3" style="grid-template-columns:1fr 224px">
      <!-- Main form -->
      <div class="space-y-4">

        <!-- Section 1: ISO 14001 -->
        <Section title="1. ISO 14001 Certification" subtitle="Number of sites and certified sites" :color="'#16A34A'">
          <div class="grid grid-cols-3 gap-3">
            <FieldInput label="Total no. of sites" unit="no." v-model.number="form.total_sites" :hint="hints.total_sites" step="1" />
            <FieldInput label="ISO 14001 certified sites" unit="no." v-model.number="form.iso_sites" :hint="hints.iso_sites" step="1" />
            <MetricBox label="% Certified (live)" :value="isoPct + '%'" />
          </div>
        </Section>

        <!-- Section 2: Production -->
        <Section title="2. Production Volume" subtitle="Annual tire/rubber production in metric tonnes" :color="'#475569'">
          <FieldInput label="Production" unit="metric T" v-model.number="form.production" :hint="hints.production" />
        </Section>

        <!-- Section 3: Water -->
        <Section title="3. Water Withdrawals" subtitle="Total water intake from all sources (m³)" :color="'#0891B2'">
          <div class="grid grid-cols-3 gap-3">
            <FieldInput class="col-span-2" label="Water withdrawals" unit="m³" v-model.number="form.water_withdrawals" :hint="hints.water_withdrawals" />
            <MetricBox label="Water KPI (m³/T)" :value="waterKpi" />
          </div>
        </Section>

        <!-- Section 4: Energy -->
        <Section title="4. Energy Consumption" subtitle="Electricity and fuel consumption (GJ)" :color="'#F59E0B'">
          <div class="grid grid-cols-3 gap-3">
            <FieldInput label="Renewable elec. purchased" unit="GJ" v-model.number="form.renew_elec_purchased" :hint="hints.renew_elec_purchased" />
            <FieldInput label="Non-renewable elec." unit="GJ" v-model.number="form.nonrenew_elec_purchased" :hint="hints.nonrenew_elec_purchased" />
            <FieldInput label="Self-generated renewable" unit="GJ" v-model.number="form.self_gen_elec" />
            <FieldInput label="Purchased Steam" unit="GJ" v-model.number="form.purchased_steam" :hint="hints.purchased_steam" />
            <FieldInput label="Sold Electricity" unit="GJ" v-model.number="form.sold_electricity" />
            <FieldInput label="Sold Steam" unit="GJ" v-model.number="form.sold_steam" />
            <FieldInput label="Natural Gas" unit="GJ LHV" v-model.number="form.nat_gas" :hint="hints.nat_gas" />
            <FieldInput label="Coal (all types)" unit="GJ LHV" v-model.number="form.coal_sub" :hint="hints.coal_sub" />
            <FieldInput label="Propane" unit="GJ LHV" v-model.number="form.propane" />
            <FieldInput label="Fuel Oil" unit="GJ LHV" v-model.number="form.fuel_oil_heavy_a" />
            <FieldInput label="Diesel" unit="GJ LHV" v-model.number="form.diesel" :hint="hints.diesel" />
            <FieldInput label="Petrol" unit="GJ LHV" v-model.number="form.petrol" />
            <FieldInput label="Biomass" unit="GJ LHV" v-model.number="form.biomass" />
            <FieldInput label="Waste tires" unit="metric T" v-model.number="form.waste_tires_mt" />
            <FieldInput label="LPG" unit="GJ LHV" v-model.number="form.lpg" :hint="hints.lpg" />
            <FieldInput label="Other fuels" unit="GJ LHV" v-model.number="form.other_fuels" />
          </div>
          <!-- Computed summary -->
          <div class="grid grid-cols-4 gap-2 mt-3">
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Total Electricity</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum(liveKPIs.total_electricity) }} GJ</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Total Energy</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum(liveKPIs.total_energy) }} GJ</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Energy KPI</span>
              <span class="text-sm font-bold tabular-nums">{{ (liveKPIs.energy_kpi||0).toFixed(2) }} GJ/T</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Renewable Share</span>
              <span class="text-sm font-bold tabular-nums">{{ (liveKPIs.renew_share_pct||0).toFixed(1) }}%</span>
            </div>
          </div>
        </Section>

        <!-- Section 5: CO2 -->
        <Section title="5. CO₂ Scope 2 Steam" subtitle="Scope 1 auto-calculated from fuels. Enter Scope 2 steam separately." :color="'#DC2626'">
          <div class="grid grid-cols-2 gap-3">
            <FieldInput label="CO₂ Scope 2 Steam" unit="T.CO₂" v-model.number="form.co2_scope2_steam" :hint="hints.co2_scope2_steam" />
            <MetricBox label="CO₂ KPI (T/T)" :value="(liveKPIs.co2_kpi||0).toFixed(3)" />
          </div>
          <div class="grid grid-cols-3 gap-2 mt-3">
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Scope 1 (T.CO₂)</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum(liveKPIs.total_co2_scope1) }}</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Scope 2 (T.CO₂)</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum(liveKPIs.total_co2_scope2) }}</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Total CO₂ (T)</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum(liveKPIs.total_co2) }}</span>
            </div>
          </div>
        </Section>

        <!-- Section 6: Waste -->
        <Section title="6. Waste Management" subtitle="Total waste generated and recovered (metric T)" :color="'#7C3AED'">
          <div class="grid grid-cols-2 gap-3">
            <FieldInput label="Total waste generated" unit="metric T" v-model.number="form.waste_total" :hint="hints.waste_total" />
            <FieldInput label="Waste sent to recovery" unit="metric T" v-model.number="form.waste_recovery" :hint="hints.waste_recovery" />
          </div>
          <div v-if="wasteError" class="mt-2 text-xs text-red-600 font-medium">⚠ Waste recovered cannot exceed total waste.</div>
          <div class="grid grid-cols-3 gap-2 mt-3">
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Eliminated (T)</span>
              <span class="text-sm font-bold tabular-nums">{{ fmtNum((form.waste_total||0)-(form.waste_recovery||0)) }}</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Recovery Rate</span>
              <span class="text-sm font-bold tabular-nums">{{ wasteRecovPct.toFixed(1) }}%</span>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 flex justify-between items-center">
              <span class="text-xs text-gray-500">Waste KPI (kg/T)</span>
              <span class="text-sm font-bold tabular-nums">{{ (form.production > 0 ? ((form.waste_total||0)/form.production*1000).toFixed(1) : "—") }}</span>
            </div>
          </div>
        </Section>

        <!-- Submit button -->
        <button @click="submitData" :disabled="saving || wasteError"
          class="w-full h-11 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-50"
          style="background:#0A2240">
          {{ saving ? "Saving…" : "✅ Submit & Save Data" }}
        </button>
        <div v-if="saveMsg" class="mt-2 px-4 py-2.5 rounded-lg text-sm"
          :class="saveOk ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-600'">
          {{ saveMsg }}
        </div>
      </div>

      <!-- Live KPI sidebar -->
      <div class="flex flex-col gap-3">
        <div class="rounded-xl p-4" style="background:#0A2240">
          <div class="text-[9px] font-semibold text-white/30 uppercase tracking-widest mb-3">Live Calculations</div>
          <div class="space-y-3 mb-3">
            <div>
              <div class="text-[10px] text-white/35">Total Energy</div>
              <div class="text-2xl font-bold text-white leading-tight">
                {{ liveKPIs.total_energy ? (liveKPIs.total_energy/1e6).toFixed(1) : "—" }}<span class="text-xs text-white/30 ml-1">M GJ</span>
              </div>
            </div>
            <div>
              <div class="text-[10px] text-white/35">Renewable Share</div>
              <div class="text-2xl font-bold text-white leading-tight">
                {{ (liveKPIs.renew_share_pct||0).toFixed(1) }}<span class="text-xs text-white/30">%</span>
              </div>
            </div>
          </div>
          <div class="border-t border-white/10 pt-3 space-y-1.5">
            <div v-for="kpi in sidebarKPIs" :key="kpi.label" class="flex justify-between">
              <span class="text-[10px] text-white/35">{{ kpi.label }}</span>
              <span class="text-[11px] font-semibold text-white/80">{{ kpi.value }}</span>
            </div>
          </div>
        </div>
        <!-- Flags -->
        <div v-if="liveFlags.length && liveFlags[0].severity !== 'ok'" class="bg-white border border-gray-100 rounded-xl p-3">
          <div class="text-xs font-semibold text-gray-600 mb-2">Validation flags</div>
          <div v-for="f in liveFlags" :key="f.message"
            class="mb-1.5 px-3 py-2 rounded-lg text-xs font-medium"
            :class="f.severity === 'error' ? 'bg-red-50 text-red-600 border border-red-100' : f.severity === 'warning' ? 'bg-yellow-50 text-yellow-700 border border-yellow-100' : 'bg-green-50 text-green-700 border border-green-100'">
            {{ f.severity === 'error' ? '✕' : f.severity === 'warning' ? '!' : '✓' }} {{ f.message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineComponent, h } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.js";
import api from "@/services/api.js";

const auth   = useAuthStore();
const router = useRouter();

// ── Year options ───────────────────────────────────────────────────────────
const availableYears = ref([]);
const selYear = ref(2023);
const isNewYear = ref(true);
const YEAR_RANGE = Array.from({length:16},(_,i)=>2009+i); // 2009..2024
const yearOptions = computed(() => {
  const set = new Set([...availableYears.value, ...YEAR_RANGE]);
  return [...set].sort((a,b) => b-a);
});

// ── Form — all 23 TemplateInputs fields ───────────────────────────────────
const defaultForm = () => ({
  total_sites: 0, iso_sites: 0, production: 0,
  water_withdrawals: 0,
  renew_elec_purchased: 0, nonrenew_elec_purchased: 0, self_gen_elec: 0,
  purchased_steam: 0, sold_electricity: 0, sold_steam: 0,
  nat_gas: 0, coal_sub: 0, propane: 0, fuel_oil_heavy_a: 0,
  diesel: 0, petrol: 0, biomass: 0, waste_tires_mt: 0, lpg: 0, other_fuels: 0,
  co2_scope2_steam: 0,
  waste_total: 0, waste_recovery: 0,
});
const form  = ref(defaultForm());
const hints = ref({});

// ── Live KPIs (client-side calc for sidebar, mirrors formula_engine.py) ───
const EF = { nat_gas:0.0561, coal_sub:0.0961, propane:0.0631, fuel_oil_heavy_a:0.0774,
             diesel:0.0741, petrol:0.0693, biomass:0, waste_tires_mt:0.0475, lpg:0.0561, other_fuels:0.0719 };
const WASTE_TIRE_HV = 36.23;
const SCOPE2_EF     = 0.45;

const liveKPIs = computed(() => {
  const f = form.value;
  const p = Math.max(f.production || 1, 1);
  const wt_gj = (f.waste_tires_mt || 0) * WASTE_TIRE_HV;
  const total_elec = (f.renew_elec_purchased||0) + (f.nonrenew_elec_purchased||0) + (f.self_gen_elec||0);
  const total_e = total_elec + (f.purchased_steam||0) + (f.nat_gas||0) + (f.coal_sub||0) +
    (f.propane||0) + (f.fuel_oil_heavy_a||0) + (f.diesel||0) + (f.petrol||0) +
    (f.biomass||0) + wt_gj + (f.lpg||0) + (f.other_fuels||0) -
    (f.sold_electricity||0) - (f.sold_steam||0);

  let scope1 = 0;
  for (const [k, ef] of Object.entries(EF)) scope1 += ((f[k]||0) * ef);
  scope1 += wt_gj * EF.waste_tires_mt;

  const scope2 = (f.co2_scope2_steam||0) + ((f.nonrenew_elec_purchased||0) / 3.6) * SCOPE2_EF;
  const total_co2 = scope1 + scope2;
  const renew_pct = total_elec > 0 ? ((f.renew_elec_purchased||0)+(f.self_gen_elec||0))/total_elec*100 : 0;

  return {
    total_electricity: Math.round(total_elec),
    total_energy:      Math.round(total_e),
    total_co2_scope1:  Math.round(scope1),
    total_co2_scope2:  Math.round(scope2),
    total_co2:         Math.round(total_co2),
    energy_kpi:        total_e / p,
    co2_kpi:           total_co2 / p,
    water_kpi:         (f.water_withdrawals||0) / p,
    renew_share_pct:   renew_pct,
    waste_recovery_pct:(f.waste_total > 0 ? (f.waste_recovery||0)/f.waste_total : 0),
  };
});

const isoPct        = computed(() => form.value.total_sites > 0 ? (form.value.iso_sites/form.value.total_sites*100).toFixed(1) : "0.0");
const waterKpi      = computed(() => form.value.production > 0 ? (form.value.water_withdrawals/form.value.production).toFixed(2) : "—");
const wasteRecovPct = computed(() => form.value.waste_total > 0 ? form.value.waste_recovery/form.value.waste_total*100 : 0);
const wasteError    = computed(() => form.value.waste_recovery > form.value.waste_total && form.value.waste_total > 0);

const liveFlags = computed(() => {
  const flags = [];
  if (wasteError.value) flags.push({ severity: "error", message: "Waste recovered > total waste" });
  if (form.value.iso_sites > form.value.total_sites && form.value.total_sites > 0)
    flags.push({ severity: "error", message: "ISO sites > total sites" });
  if (!flags.length) flags.push({ severity: "ok", message: "All checks passed" });
  return flags;
});

const sidebarKPIs = computed(() => [
  { label: "Energy KPI", value: (liveKPIs.value.energy_kpi||0).toFixed(2) + " GJ/T" },
  { label: "CO₂ KPI",    value: (liveKPIs.value.co2_kpi||0).toFixed(3) + " T/T" },
  { label: "Water KPI",  value: (liveKPIs.value.water_kpi||0).toFixed(2) + " m³/T" },
  { label: "Waste Rec.", value: (liveKPIs.value.waste_recovery_pct||0)*100 > 0 ? (liveKPIs.value.waste_recovery_pct*100).toFixed(1)+"%" : "—" },
]);

function fmtNum(n) { return n ? Math.round(n).toLocaleString() : "—"; }

// ── Load existing data ─────────────────────────────────────────────────────
async function loadYear(year) {
  try {
    const data = await api.getCompanyData(auth.companyName, year);
    if (data?.raw && Object.keys(data.raw).length > 0) {
      form.value  = { ...defaultForm(), ...data.raw };
      isNewYear.value = false;
      // Set hints from prior year
      if (data.kpis) {
        hints.value = {
          total_sites:   `Prior ${year-1}: ${data.raw.total_sites||'—'}`,
          production:    `Prior ${year-1}: ${data.raw.production ? Number(data.raw.production).toLocaleString() : '—'}`,
          water_withdrawals: `Prior ${year-1}: ${data.raw.water_withdrawals ? Number(data.raw.water_withdrawals).toLocaleString() : '—'}`,
        };
      }
    } else {
      form.value  = defaultForm();
      isNewYear.value = true;
    }
    if (data?.years) {
      availableYears.value = data.years;
    }
  } catch (_) {
    form.value = defaultForm();
    isNewYear.value = true;
  }
}

const saving  = ref(false);
const saveMsg = ref("");
const saveOk  = ref(false);

async function submitData() {
  if (wasteError.value) return;
  saving.value = true;
  saveMsg.value = "";
  try {
    const result = await api.submitData({
      company: auth.companyName,
      year:    selYear.value,
      data:    { ...form.value },
    });
    saveOk.value  = true;
    saveMsg.value = `✅ ${result.message}`;
    // Redirect to My Records
    setTimeout(() => router.push("/my-records"), 1500);
  } catch (e) {
    saveOk.value  = false;
    saveMsg.value = `❌ Save failed: ${e.response?.data?.error || e.message}. Check that the Python backend is running (func start).`;
  } finally {
    saving.value = false;
  }
}

onMounted(() => loadYear(selYear.value));
watch(selYear, loadYear);

// ── Sub-components ─────────────────────────────────────────────────────────
const Section = defineComponent({
  props: { title: String, subtitle: String, color: { default: "#16A34A" } },
  setup(props, { slots }) {
    return () => h("div", {}, [
      h("div", { style: `border-left:3px solid ${props.color};padding:4px 0 4px 12px;margin-bottom:10px` }, [
        h("div", { style: "font-size:14px;font-weight:700;color:#111827" }, props.title),
        h("div", { style: "font-size:11px;color:#6B7280;margin-top:2px" }, props.subtitle),
      ]),
      h("div", { class: "bg-white border border-gray-100 rounded-xl p-4" }, slots.default?.()),
    ]);
  },
});
const FieldInput = defineComponent({
  props: { label: String, unit: String, modelValue: Number, hint: String, step: { default: 1000 } },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    return () => h("div", { class: "flex flex-col gap-1" }, [
      h("label", { style: "font-size:10px;font-weight:600;color:#6B7280;text-transform:uppercase;letter-spacing:.35px" }, props.label),
      h("div", { class: "flex" }, [
        h("input", { type: "number", min: 0, step: props.step || 1000,
          value: props.modelValue || 0, class: "flex-1 h-9 border border-gray-200 rounded-l-lg px-3 text-sm focus:outline-none focus:border-blue-400",
          onInput: (e) => emit("update:modelValue", parseFloat(e.target.value) || 0) }),
        h("div", { class: "h-9 px-2 bg-gray-50 border border-l-0 border-gray-200 rounded-r-lg text-[10px] text-gray-400 flex items-center whitespace-nowrap" }, props.unit),
      ]),
      props.hint ? h("div", { style: "font-size:10px;color:#F59E0B" }, props.hint) : null,
    ]);
  },
});
const MetricBox = defineComponent({
  props: { label: String, value: [String, Number] },
  setup(props) {
    return () => h("div", { class: "flex flex-col justify-center bg-gray-50 rounded-lg px-3 py-2 border border-gray-100" }, [
      h("div", { style: "font-size:10px;color:#6B7280;font-weight:600" }, props.label),
      h("div", { style: "font-size:16px;font-weight:700;color:#0A2240;font-variant-numeric:tabular-nums" }, props.value),
    ]);
  },
});
</script>