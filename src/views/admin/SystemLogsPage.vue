<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const logs = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('admin/logs/?page_size=50')
    logs.value = (data.results ?? []).map(l => ({
      id: l.id,
      level: l.level ?? 'INFO',
      action: l.source ?? '—',
      user: l.user_id ?? 'system',
      message: l.message ?? '',
      ip: '—',
      time: l.created_at ? new Date(l.created_at).toLocaleString('pl-PL') : '',
    }))
  } catch (_) {}
})

const levelFilter = ref('ALL')
const search = ref('')
const levels = ['ALL', 'INFO', 'WARN', 'ERROR']

const filtered = computed(() => logs.value.filter(l => {
  const matchLevel = levelFilter.value === 'ALL' || l.level === levelFilter.value
  const matchSearch = !search.value ||
    l.user.toLowerCase().includes(search.value.toLowerCase()) ||
    l.message.toLowerCase().includes(search.value.toLowerCase()) ||
    l.action.toLowerCase().includes(search.value.toLowerCase())
  return matchLevel && matchSearch
}))

const levelMeta = {
  INFO:  { color: '#3b82f6', bg: '#3b82f610' },
  WARN:  { color: '#f59e0b', bg: '#f59e0b10' },
  ERROR: { color: '#ef4444', bg: '#ef444410' },
}
const lm = (l) => levelMeta[l] || { color: '#64748b', bg: 'transparent' }

const errorCount = computed(() => logs.value.filter(l => l.level === 'ERROR').length)
const warnCount  = computed(() => logs.value.filter(l => l.level === 'WARN').length)

const exportingCsv = ref(false)
const exportCsv = async () => {
  exportingCsv.value = true
  try {
    const params = levelFilter.value !== 'ALL' ? { level: levelFilter.value } : {}
    const { data } = await api.get('admin/logs/export/', { params, responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([data], { type: 'text/csv;charset=utf-8' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `system_logs_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (_) {} finally {
    exportingCsv.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/dashboard" class="back-link">← Panel admina</router-link>
        <div class="header-row">
          <h1>Logi <span>systemowe</span></h1>
          <div class="summary-chips">
            <span class="chip error">{{ errorCount }} błędów</span>
            <span class="chip warn">{{ warnCount }} ostrzeżeń</span>
          </div>
        </div>
        <p class="subtitle">Audyt zdarzeń · {{ new Date().toLocaleDateString('pl-PL') }}</p>
      </div>

      <div class="toolbar">
        <div class="search-bar">
          <span>🔍</span>
          <input v-model="search" type="text" placeholder="Szukaj użytkownika, akcji, komunikatu…" />
        </div>
        <div class="level-tabs">
          <button
            v-for="l in levels" :key="l"
            class="level-tab"
            :class="{ active: levelFilter === l }"
            :style="levelFilter === l && l !== 'ALL' ? { borderColor: levelMeta[l]?.color + '55', color: levelMeta[l]?.color } : {}"
            @click="levelFilter = l">
            {{ l === 'ALL' ? 'Wszystkie' : l }}
          </button>
        </div>
        <button class="btn-export" :disabled="exportingCsv" @click="exportCsv">
          {{ exportingCsv ? '⏳ Eksportowanie…' : '⬇ Eksportuj CSV' }}
        </button>
      </div>

      <div class="logs-table">
        <div class="table-header">
          <span>Poziom</span>
          <span>Akcja</span>
          <span>Użytkownik</span>
          <span>Komunikat</span>
          <span>IP</span>
          <span>Czas</span>
        </div>
        <div v-for="log in filtered" :key="log.id" class="log-row" :class="log.level.toLowerCase()">
          <div>
            <span class="level-chip" :style="{ color: lm(log.level).color, background: lm(log.level).bg }">
              {{ log.level }}
            </span>
          </div>
          <div class="action-cell">{{ log.action }}</div>
          <div class="user-cell">{{ log.user }}</div>
          <div class="msg-cell">{{ log.message }}</div>
          <div class="ip-cell">{{ log.ip }}</div>
          <div class="time-cell">{{ log.time }}</div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="empty">Brak logów pasujących do kryteriów</div>

      <!-- TODO: Paginacja z cursor-based paginacją dla wydajności -->
      <div class="pagination">
        <button class="page-btn" disabled>← Wcześniejsze</button>
        <span class="page-info">Strona 1 z 1</span>
        <button class="page-btn" disabled>Nowsze →</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1300px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } .subtitle { color: #64748b; font-size: 0.82rem; margin: 0.25rem 0 0; } }
.header-row { display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.summary-chips { display: flex; gap: 0.5rem; }
.chip { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.72rem; font-weight: 800; &.error { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.2); } &.warn { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); } }

.toolbar { display: flex; gap: 0.75rem; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; }
.search-bar { display: flex; align-items: center; gap: 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; padding: 0.65rem 1rem; flex: 1; min-width: 200px; span { color: #475569; } input { flex: 1; background: none; border: none; color: white; font-size: 0.88rem; outline: none; &::placeholder { color: #475569; } } }
.level-tabs { display: flex; gap: 0.35rem; }
.level-tab { padding: 0.45rem 0.85rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #64748b; border-radius: 0.6rem; cursor: pointer; font-size: 0.78rem; font-weight: 700; transition: 0.15s; &.active { background: rgba(59,130,246,0.1); } }
.btn-export { padding: 0.5rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #94a3b8; border-radius: 0.65rem; cursor: pointer; font-size: 0.78rem; font-weight: 600; white-space: nowrap; transition: 0.15s; &:hover { background: rgba(255,255,255,0.06); } }

.logs-table { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; overflow: hidden; overflow-x: auto; }
.table-header { display: grid; grid-template-columns: 0.6fr 0.8fr 1.5fr 3fr 1fr 1.5fr; gap: 0.75rem; padding: 0.85rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; min-width: 800px; }
.log-row { display: grid; grid-template-columns: 0.6fr 0.8fr 1.5fr 3fr 1fr 1.5fr; gap: 0.75rem; align-items: center; padding: 0.75rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); min-width: 800px; &:last-child { border-bottom: none; } &.error { background: rgba(239,68,68,0.025); } &.warn { background: rgba(245,158,11,0.02); } }
.level-chip { display: inline-block; padding: 0.18rem 0.55rem; border-radius: 0.4rem; font-size: 0.68rem; font-weight: 800; }
.action-cell { font-size: 0.78rem; font-family: monospace; color: #94a3b8; }
.user-cell { font-size: 0.82rem; color: #cbd5e1; }
.msg-cell { font-size: 0.82rem; color: #94a3b8; }
.ip-cell { font-size: 0.75rem; font-family: monospace; color: #64748b; }
.time-cell { font-size: 0.72rem; font-family: monospace; color: #64748b; }

.empty { text-align: center; padding: 3rem; color: #64748b; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1.5rem; margin-top: 1.5rem; .page-info { color: #64748b; font-size: 0.85rem; } }
.page-btn { padding: 0.55rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.6rem; cursor: pointer; font-size: 0.82rem; font-weight: 600; &:disabled { opacity: 0.4; cursor: not-allowed; } }
</style>