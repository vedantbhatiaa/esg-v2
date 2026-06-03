<template>
  <div ref="chartEl" class="plotly-wrapper" :style="{ height: height + 'px' }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  traces:    { type: Array,  required: true },
  layout:    { type: Object, default: () => ({}) },
  config:    { type: Object, default: () => ({}) },
  height:    { type: Number, default: 320 },
  chartKey:  { type: [String, Number], default: null },  // change to force full re-render
})

const chartEl  = ref(null)
let   Plotly   = null
let   observer = null

// ── Design tokens (matching Streamlit ui_components.py) ───────────────────────
const NAVY   = '#0A2240'
const TEXT   = '#0F172A'
const MUTED  = '#64748B'
const BORDER = '#E2E8F0'
const FONT   = 'Inter, ui-sans-serif, system-ui, sans-serif'

const BASE_LAYOUT = {
  font:       { family: FONT, size: 12, color: TEXT },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor:  'rgba(0,0,0,0)',
  margin:     { t: 36, r: 24, b: 40, l: 52 },
  legend:     { orientation: 'h', yanchor: 'bottom', y: -0.22, xanchor: 'left', x: 0,
                font: { size: 11, color: MUTED }, bgcolor: 'rgba(0,0,0,0)', borderwidth: 0 },
  xaxis:      { gridcolor: '#F1F5F9', linecolor: BORDER, tickcolor: BORDER,
                tickfont: { size: 11, color: MUTED }, automargin: true },
  yaxis:      { gridcolor: '#F1F5F9', linecolor: BORDER, tickcolor: BORDER,
                tickfont: { size: 11, color: MUTED }, automargin: true,
                zeroline: false },
  hoverlabel: { bgcolor: '#FFFFFF', font: { family: FONT, size: 12 },
                bordercolor: BORDER },
  hovermode:  'x unified',
  autosize:   true,
}

// Restart animations on ALL chart elements
function _forceAnimRestart() {
  if (!chartEl.value) return
  const els = chartEl.value.querySelectorAll(
    '.barlayer .point path, .scatterlayer .trace .js-line, .scatterlayer .trace .point path, .pielayer .trace .slice path'
  )
  els.forEach(el => {
    el.style.animation = 'none'
    void el.offsetWidth          // force reflow
    el.style.animation = ''
  })
}

async function _render() {
  if (!chartEl.value || !props.traces?.length) return
  if (!Plotly) {
    Plotly = (await import('plotly.js-dist')).default
  }
  const mergedLayout = {
    ...BASE_LAYOUT,
    height: props.height,
    ...props.layout,
    xaxis:  { ...BASE_LAYOUT.xaxis, ...(props.layout?.xaxis || {}) },
    yaxis:  { ...BASE_LAYOUT.yaxis, ...(props.layout?.yaxis || {}) },
  }
  const mergedConfig = {
    displayModeBar: false,
    responsive:     true,
    ...props.config,
  }

  await Plotly.react(chartEl.value, props.traces, mergedLayout, mergedConfig)
  await nextTick()

  // Start MutationObserver to restart animations when Plotly swaps SVG nodes
  if (!observer) {
    observer = new MutationObserver(() => {
      setTimeout(_forceAnimRestart, 30)
    })
    observer.observe(chartEl.value, { childList: true, subtree: true })
  }

  setTimeout(_forceAnimRestart, 80)
}

onMounted(_render)

// Re-render when traces change OR chartKey changes (forces identical animation for all bars)
watch(() => [props.traces, props.chartKey], _render, { deep: true })

onBeforeUnmount(async () => {
  observer?.disconnect()
  if (Plotly && chartEl.value) Plotly.purge(chartEl.value)
})
</script>

<style scoped>
.plotly-wrapper { width: 100%; }
</style>
