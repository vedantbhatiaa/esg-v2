const BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

async function _fetch(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`)
  return json
}

const api = {
  // Auth
  login:           (email, password)     => _fetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  // Home
  getHomeData:     (company, year)       => _fetch(`/home?company=${encodeURIComponent(company)}&year=${year}`),

  // My Records
  getMyRecords:    (company, year)       => _fetch(`/records?company=${encodeURIComponent(company)}&year=${year}`),

  // Analytics / Dashboard
  getAnalytics:    (params)              => _fetch('/analytics?' + new URLSearchParams(params)),

  // Benchmarks
  getBenchmarks:   (params)              => _fetch('/benchmarks?' + new URLSearchParams(params)),

  // Reports
  getReports:      (company, year)       => _fetch(`/reports?company=${encodeURIComponent(company)}&year=${year}`),

  // Submit Data
  submitData:      (body)                => _fetch('/submissions', { method: 'POST', body: JSON.stringify(body) }),

  // Companies
  getCompanies:    ()                    => _fetch('/companies'),

  // Verification (DSS+)
  getVerificationQueue: ()               => _fetch('/verification'),
  setVerificationStatus: (body)          => _fetch('/verification', { method: 'POST', body: JSON.stringify(body) }),
}

export default api
export const { login, getHomeData, getMyRecords, getAnalytics, getBenchmarks,
               getReports, submitData, getCompanies } = api
