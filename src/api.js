import axios from 'axios'
import { ref } from 'vue'

const ACCESS_KEY  = 'djic_access'
const REFRESH_KEY = 'djic_refresh'

export const isServerOffline = ref(false)

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Dołącz access token do każdego żądania ────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Obsługa wygaśniętego tokenu (401) — próba odświeżenia ────────────────────
let refreshing = false
let queue = []

function processQueue(error, token = null) {
  queue.forEach(({ resolve, reject }) => error ? reject(error) : resolve(token))
  queue = []
}

api.interceptors.response.use(
  (response) => {
    isServerOffline.value = false
    return response
  },
  async (error) => {
    if (!error.response) {
      isServerOffline.value = true
    } else {
      isServerOffline.value = false
    }

    const original = error.config

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    const refreshToken = localStorage.getItem(REFRESH_KEY)
    if (!refreshToken) {
      clearTokens()
      sessionStorage.removeItem('djic_user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (refreshing) {
      return new Promise((resolve, reject) => {
        queue.push({ resolve, reject })
      }).then((token) => {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      })
    }

    original._retry = true
    refreshing = true

    try {
      const { data } = await axios.post(
        `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'}/auth/token/refresh/`,
        { refresh: refreshToken },
      )
      saveTokens(data.access, refreshToken)
      processQueue(null, data.access)
      original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    } catch (err) {
      processQueue(err)
      clearTokens()
      sessionStorage.removeItem('djic_user')
      window.location.href = '/login'
      return Promise.reject(err)
    } finally {
      refreshing = false
    }
  },
)

// ── Helpery tokenów ───────────────────────────────────────────────────────────
export function saveTokens(access, refresh) {
  localStorage.setItem(ACCESS_KEY, access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY)
}
