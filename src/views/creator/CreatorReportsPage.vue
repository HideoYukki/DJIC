<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const reports = ref([])

const downloadReport = (id) => {
  window.open(`/api/analytics/courses/${id}/report/`, '_blank')
}

onMounted(async () => {
  try {
    const { data } = await api.get('courses/creator/')
    reports.value = (data.results ?? data ?? []).map(c => ({
      id: c.id,
      course: c.title,
      period: new Date().toLocaleDateString('pl-PL', { month: 'long', year: 'numeric' }),
      students: c.students_count ?? 0,
      completions: 0,
      revenue: '—',
      status: 'ready',
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/creator/dashboard" class="back-link">← Panel twórcy</router-link>
        <h1>Raporty <span>kursów</span></h1>
        <p class="subtitle">Miesięczne podsumowania wszystkich Twoich kursów</p>
      </div>

      <div class="reports-table">
        <div class="table-header">
          <span>Kurs</span>
          <span>Okres</span>
          <span>Uczniów</span>
          <span>Ukończeń</span>
          <span>Status</span>
          <span>Akcje</span>
        </div>
        <div v-for="r in reports" :key="r.id" class="report-row">
          <div class="report-course">
            <strong>{{ r.course }}</strong>
          </div>
          <div class="report-period">{{ r.period }}</div>
          <div class="report-num">{{ r.students }}</div>
          <div class="report-num">{{ r.completions }}</div>
          <div>
            <span class="status-chip" :class="r.status">
              {{ r.status === 'ready' ? '✅ Gotowy' : '⏳ Generowanie...' }}
            </span>
          </div>
          <div class="report-actions">
            <button class="btn-action" :disabled="r.status !== 'ready'" @click="downloadReport(r.id)">📥 PDF</button>
            <router-link :to="`/creator/reports/${r.id}`" class="btn-action-link">Szczegóły →</router-link>
          </div>
        </div>
      </div>

      <div class="info-box">
        <!-- TODO: GET /api/creator/reports/?auto_generate=true → raporty generowane automatycznie 1. dnia każdego miesiąca -->
        <span>ℹ️</span>
        <p>Raporty miesięczne są generowane automatycznie 1. dnia każdego miesiąca. Możesz też wygenerować raport ręcznie z poziomu analityki kursu.</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1000px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } } .subtitle { color: #64748b; font-size: 0.85rem; } }

.reports-table { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; overflow: hidden; margin-bottom: 1.5rem; }
.table-header { display: grid; grid-template-columns: 2fr 1fr 0.8fr 0.8fr 1fr 1.2fr; gap: 0.75rem; padding: 0.85rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.report-row { display: grid; grid-template-columns: 2fr 1fr 0.8fr 0.8fr 1fr 1.2fr; gap: 0.75rem; align-items: center; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); transition: 0.15s; &:last-child { border-bottom: none; } &:hover { background: rgba(255,255,255,0.02); } }
.report-course strong { font-size: 0.87rem; }
.report-period, .report-num { font-size: 0.87rem; color: #94a3b8; }

.status-chip { padding: 0.25rem 0.65rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 600; &.ready { background: rgba(16,185,129,0.1); color: #10b981; } &.generating { background: rgba(245,158,11,0.1); color: #f59e0b; } }

.report-actions { display: flex; align-items: center; gap: 0.5rem; }
.btn-action { padding: 0.35rem 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.5rem; cursor: pointer; font-size: 0.75rem; font-weight: 600; transition: 0.15s; &:disabled { opacity: 0.4; cursor: not-allowed; } &:hover:not(:disabled) { background: rgba(255,255,255,0.09); } }
.btn-action-link { color: #3b82f6; text-decoration: none; font-size: 0.78rem; font-weight: 700; &:hover { text-decoration: underline; } }

.info-box { display: flex; gap: 0.75rem; align-items: flex-start; background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.15); border-radius: 1rem; padding: 1rem 1.25rem; span { font-size: 1rem; flex-shrink: 0; } p { color: #94a3b8; font-size: 0.82rem; line-height: 1.5; margin: 0; } }
</style>