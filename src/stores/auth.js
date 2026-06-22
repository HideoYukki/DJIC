import { defineStore } from 'pinia'
import { api, saveTokens, clearTokens } from '@/api'

const SESSION_KEY = 'djic_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null'),
    loading: false,
    error: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.user,
    isStudent:  (state) => state.user?.role === 'STUDENT',
    isCreator:  (state) => state.user?.role === 'CREATOR',
    isAdmin:    (state) => state.user?.role === 'ADMIN',
    role:       (state) => state.user?.role ?? null,
    userName:   (state) => state.user?.name ?? state.user?.email ?? '',
  },

  actions: {
    _setUser(userData) {
      this.user = userData
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(userData))
    },

    // ── Logowanie ─────────────────────────────────────────────────────────────
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/login/', { email, password })
        saveTokens(data.access, data.refresh)
        this._setUser(data.user)
        return { ok: true, role: data.user.role }
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Błąd logowania. Spróbuj ponownie.'
        return { ok: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // ── Rejestracja ───────────────────────────────────────────────────────────
    async register(payload) {
      this.loading = true
      this.error = null
      try {
        await api.post('/auth/register/', payload)
        return { ok: true }
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Błąd rejestracji. Spróbuj ponownie.'
        return { ok: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // ── Wylogowanie ───────────────────────────────────────────────────────────
    async logout() {
      try {
        const refresh = localStorage.getItem('djic_refresh')
        if (refresh) await api.post('/auth/logout/', { refresh })
      } catch (_) {
        // Wyloguj lokalnie nawet jeśli serwer nie odpowie
      } finally {
        clearTokens()
        this.user = null
        sessionStorage.removeItem(SESSION_KEY)
      }
    },

    // ── Odświeżenie danych profilu ────────────────────────────────────────────
    async fetchMe() {
      try {
        const { data } = await api.get('/users/me/')
        this._setUser({ ...this.user, ...data })
      } catch (_) {}
    },
  },
})
