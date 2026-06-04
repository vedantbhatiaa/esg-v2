<template>
  <div class="bg-white border border-gray-100 rounded-xl p-4 hover:shadow-md transition-all duration-200 cursor-default select-none"
    :style="{ animationDelay: delay + 'ms' }"
    style="animation: tipFadeIn 400ms ease-out both">
    <div class="text-[10.5px] font-semibold text-gray-400 uppercase tracking-[.5px] mb-2 leading-none">{{ label }}</div>
    <div class="text-[26px] font-bold leading-none mb-1 tabular-nums whitespace-nowrap overflow-hidden text-ellipsis"
      :style="{ color }">
      {{ value }}
      <span class="text-[12px] font-normal text-gray-400 ml-0.5">{{ unit }}</span>
    </div>
    <div v-if="delta" class="mt-1.5">
      <span class="text-[11px] font-semibold px-1.5 py-0.5 rounded"
        :class="deltaGood ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'">
        {{ deltaGood ? "▼" : "▲" }} {{ delta }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({
  label:       String,
  value:       [String, Number],
  unit:        String,
  delta:       { type: String, default: null },
  lowerBetter: { type: Boolean, default: true },
  color:       { type: String, default: "#0A2240" },
  delay:       { type: Number, default: 0 },
});

const deltaGood = computed(() => {
  if (!props.delta) return true;
  const num = parseFloat(props.delta);
  return props.lowerBetter ? num < 0 : num > 0;
});
</script>

<style>
@keyframes tipFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>