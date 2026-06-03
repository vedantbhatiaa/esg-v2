<template>
  <div class="bg-white border border-gray-100 rounded-xl p-4 relative overflow-hidden">
    <!-- top accent bar -->
    <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: color }"></div>

    <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{{ label }}</div>

    <div class="font-head text-2xl font-bold text-gray-900 my-1 leading-none">
      {{ value ?? "—" }}
    </div>

    <div class="text-[11px] text-gray-400">{{ unit }}</div>

    <!-- YoY delta badge -->
    <div v-if="delta !== null" class="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold px-1.5 py-0.5 rounded-lg"
      :class="deltaClass">
      {{ deltaArrow }} {{ Math.abs(delta) }}% {{ deltaLabel }}
    </div>

    <!-- mini sparkline slot -->
    <div v-if="$slots.chart" class="h-8 mt-2">
      <slot name="chart" />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  label:      { type: String, required: true },
  value:      { type: [Number, String], default: null },
  unit:       { type: String, default: "" },
  delta:      { type: Number, default: null },       // YoY % change
  deltaLabel: { type: String, default: "YoY" },
  lowerBetter:{ type: Boolean, default: true },       // whether falling delta is good
  color:      { type: String, default: "#0891B2" },
});

const isGood = computed(() =>
  props.delta === null ? null :
  props.lowerBetter ? props.delta < 0 : props.delta > 0
);

const deltaClass = computed(() => {
  if (isGood.value === null) return "bg-gray-100 text-gray-500";
  return isGood.value
    ? "bg-green-50 text-green-700"
    : "bg-red-50 text-red-600";
});

const deltaArrow = computed(() => {
  if (props.delta === null) return "";
  return props.delta < 0 ? "▼" : props.delta > 0 ? "▲" : "→";
});
</script>
