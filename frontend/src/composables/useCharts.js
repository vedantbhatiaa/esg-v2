/**
 * useCharts.js — shared Chart.js constants and helpers
 * Used by: Home, Analysis, Dashboard, Benchmarking, Reports, Portfolio
 */
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

// ── Design tokens (match Streamlit ui_components.py)
export const C = {
  navy:   "#0A2240",
  red:    "#C8102E",
  green:  "#00916E",
  teal:   "#0891B2",
  amber:  "#D97706",
  purple: "#7C3AED",
  gray:   "#6B7280",
  grid:   "#F3F4F6",
  co2:    "#475569",
  energy: "#F59E0B",
  water:  "#0891B2",
  waste:  "#7C3AED",
  renew:  "#16A34A",
};

export const TOOLTIP = {
  backgroundColor: "#0A2240",
  titleColor: "#fff",
  bodyColor: "rgba(255,255,255,.75)",
  borderColor: "rgba(255,255,255,.1)",
  borderWidth: 1,
  padding: 8,
  cornerRadius: 6,
};

export const AXIS = {
  x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } },
  y: { grid: { color: "rgba(0,0,0,.04)" }, ticks: { color: "#94A3B8", font: { size: 10 } } },
};

export const ANIMATION = { duration: 900, easing: "easeOutQuart" };

export const LEGEND = {
  display: true,
  position: "top",
  labels: { color: "#64748B", boxWidth: 9, font: { size: 11 }, padding: 9 },
};

// ── Year range (2009–2023, matching Streamlit LONG_YEARS)
export const YEARS       = Array.from({ length: 15 }, (_, i) => 2009 + i);
export const YEAR_LABELS = YEARS.map(y => `'${String(y).slice(2)}`);

// ── Static fallback data (LONG_DATA from Streamlit app.py)
export const FALLBACK = {
  energy:     [28.1,32.3,33.6,32.4,33.0,32.4,31.8,32.1,33.0,34.2,33.2,28.5,32.3,32.5,32.4],
  co2:        [2.41,2.69,2.88,2.80,2.87,2.86,2.73,2.72,2.80,2.85,2.76,2.22,2.27,2.06,2.05],
  water:      [22.4,23.8,24.9,24.4,23.9,22.9,22.9,23.5,23.5,23.2,23.1,20.3,21.1,20.9,21.5],
  scope1:     [1.08,1.19,1.21,1.17,1.20,1.15,1.09,1.08,1.12,1.15,1.11,0.94,1.06,1.05,1.03],
  scope2:     [1.33,1.50,1.67,1.63,1.67,1.71,1.64,1.64,1.68,1.70,1.65,1.27,1.21,1.01,1.02],
  energy_kpi: [9.9,9.2,8.9,9.2,9.1,8.9,8.9,8.8,8.9,8.8,8.6,9.3,9.7,9.1,8.7],
  co2_kpi:    [0.850,0.765,0.764,0.795,0.789,0.791,0.771,0.748,0.758,0.729,0.715,0.729,0.684,0.576,0.551],
  renew_pct:  [0,0,0,0,0,0,0,2.3,2.2,9.7,10.6,21.8,31.4,40.6,48.3],
  waste_recov:[83,83,84,84,84,84,84,85,85,85,85,86,86,85,86],
  prod:       [2.84,3.51,3.77,3.52,3.64,3.62,3.54,3.63,3.70,3.91,3.86,3.05,3.32,3.58,3.72],
  fuel_mix: {
    "Natural Gas": [46,46,47,47,47,46,47,47,48,49,49,49,49,49,50],
    "Electricity":  [34.7,34.2,34.9,34.6,35.3,36.7,37.1,37.9,38.2,38.8,39.1,39.3,39.8,40.4,40.7],
    "Fuel Oil":     [8.5,6.7,6,5.8,5.1,4.8,3.7,3.2,3,2.6,2.4,1.8,1.4,0.5,0.5],
    "LPG":          [2.4,2.4,2.3,3.6,3.5,3.5,3.5,3.6,3.5,3.6,3.7,3.9,3.9,4.1,4.2],
    "Coal":         [3.2,3.1,2.8,2.8,3.7,3.6,2.3,2,2.1,1.6,1.4,1.2,1.2,1.2,1.2],
    "Other":        [5.2,7.6,7,5.4,5.4,5.4,6.4,5.3,4.7,4.4,4,4.8,4.3,4.8,3.4],
  },
};

/** Merge live API series with fallback, replacing null/NaN values */
export function mergeSeries(apiSeries, fallback) {
  if (!apiSeries || !Array.isArray(apiSeries)) return fallback;
  return apiSeries.map((v, i) =>
    (v !== null && v !== undefined && !isNaN(v)) ? v : (fallback?.[i] ?? null)
  );
}

/** Destroy all chart instances safely */
export function destroyCharts(charts) {
  Object.values(charts).forEach(c => { try { c.destroy(); } catch (_) {} });
}

/** Line dataset shorthand */
export function lineDataset(label, data, color, fill = false) {
  return {
    label, data,
    borderColor: color,
    backgroundColor: fill ? color + "18" : "transparent",
    fill, tension: 0.4, pointRadius: 3,
    pointBackgroundColor: color, borderWidth: 2,
  };
}

/** Bar dataset shorthand */
export function barDataset(label, data, color) {
  return { label, data, backgroundColor: color, borderRadius: 3, borderWidth: 0 };
}

/** Base chart options */
export function baseOptions(showLegend = true, extra = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: ANIMATION,
    plugins: {
      legend: showLegend ? LEGEND : { display: false },
      tooltip: TOOLTIP,
    },
    scales: AXIS,
    interaction: { mode: "index", intersect: false },
    ...extra,
  };
}