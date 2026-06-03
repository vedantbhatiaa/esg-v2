import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api.js'

export const useEsgStore = defineStore('esg', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const homeData        = ref(null)
  const myRecordsData   = ref(null)
  const benchmarkData   = ref(null)
  const analyticsData   = ref(null)
  const reportsData     = ref(null)
  const companies       = ref([])
  const loading         = ref({})
  const errors          = ref({})

  const selectedYear    = ref(null)   // home page year selector
  const dfVersion       = ref(0)      // increments on every save (forces chart re-key)

  // ── Helpers ────────────────────────────────────────────────────────────────
  function _setLoading(key, val) { loading.value[key] = val }
  function _setError(key, err)  { errors.value[key]  = err }

  // ── Actions ────────────────────────────────────────────────────────────────
  async function fetchHomeData(company, year) {
    _setLoading('home', true)
    try {
      const data = await api.getHomeData(company, year)
      homeData.value = data
      if (!selectedYear.value && data.available_years?.length)
        selectedYear.value = Math.max(...data.available_years)
    } catch (e) {
      _setError('home', e.message)
    } finally {
      _setLoading('home', false)
    }
  }

  async function fetchMyRecords(company, year) {
    _setLoading('records', true)
    try {
      myRecordsData.value = await api.getMyRecords(company, year)
    } catch (e) {
      _setError('records', e.message)
    } finally {
      _setLoading('records', false)
    }
  }

  async function fetchBenchmarks(company, year) {
    _setLoading('bench', true)
    try {
      benchmarkData.value = await api.getBenchmarks({ company_id: company, year })
    } catch (e) {
      _setError('bench', e.message)
    } finally {
      _setLoading('bench', false)
    }
  }

  async function fetchAnalytics(company, yearFrom, yearTo) {
    _setLoading('analytics', true)
    try {
      analyticsData.value = await api.getAnalytics({ company_id: company, year_from: yearFrom, year_to: yearTo })
    } catch (e) {
      _setError('analytics', e.message)
    } finally {
      _setLoading('analytics', false)
    }
  }

  async function fetchReports(company, year) {
    _setLoading('reports', true)
    try {
      reportsData.value = await api.getReports(company, year)
    } catch (e) {
      _setError('reports', e.message)
    } finally {
      _setLoading('reports', false)
    }
  }

  async function submitData(company, year, formData) {
    _setLoading('submit', true)
    try {
      const result = await api.submitData({ company_name: company, year, ...formData })
      dfVersion.value++          // force all chart re-renders
      await fetchHomeData(company, year)  // refresh home data
      return result
    } catch (e) {
      _setError('submit', e.message)
      throw e
    } finally {
      _setLoading('submit', false)
    }
  }

  // ── Computed ───────────────────────────────────────────────────────────────
  const availableYears  = computed(() => homeData.value?.available_years || [])
  const nextYear        = computed(() => homeData.value?.next_year || null)
  const homeKpis        = computed(() => homeData.value?.kpis || {})
  const homeYoy         = computed(() => homeData.value?.yoy  || {})
  const homeCharts      = computed(() => homeData.value?.charts || {})
  const submissionStatus= computed(() => homeData.value?.submission_status || {})

  return {
    homeData, myRecordsData, benchmarkData, analyticsData, reportsData,
    companies, loading, errors, selectedYear, dfVersion,
    availableYears, nextYear, homeKpis, homeYoy, homeCharts, submissionStatus,
    fetchHomeData, fetchMyRecords, fetchBenchmarks, fetchAnalytics,
    fetchReports, submitData,
  }
})
