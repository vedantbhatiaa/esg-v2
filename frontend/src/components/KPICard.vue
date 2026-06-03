<template>
  <div class="bg-white border border-[#E2E8F0] rounded-xl p-4 flex flex-col gap-1">
    <div class="text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider">{{ label }}</div>
    <div class="text-[24px] font-extrabold leading-none mt-1" :style="{ color }">
      {{ value ?? '—' }}
      <span v-if="unit && !String(value||'').includes(unit)"
        class="text-[12px] font-medium text-[#94A3B8] ml-1">{{ unit }}</span>
    </div>
    <div v-if="delta !== null && delta !== undefined" class="flex items-center gap-1 mt-1">
      <span class="text-[11px] font-semibold px-1.5 py-0.5 rounded"
        :class="deltaClass">
        {{ delta > 0 ? '+' : '' }}{{ delta?.toFixed(1) }}%
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:       { type: String,  required: true },
  value:       { type: [String, Number], default: null },
  unit:        { type: String,  default: '' },
  delta:       { type: Number,  default: null },
  lowerBetter: { type: Boolean, default: true },
  color:       { type: String,  default: '#0F172A' },
})

const isGood = computed(() => {
  if (props.delta === null || props.delta === undefined) return null
  return props.lowerBetter ? props.delta <= 0 : props.delta >= 0
})

const deltaClass = computed(() => {
  if (isGood.value === null) return 'text-[#64748B] bg-[#F1F5F9]'
  return isGood.value
    ? 'text-[#16A34A] bg-green-50'
    : 'text-red-500 bg-red-50'
})
</script>
