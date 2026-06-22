<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const route = useRoute()

const report = ref({
  course: '',
  period: new Date().toLocaleDateString('pl-PL', { month: 'long', year: 'numeric' }),
  generated: new Date().toISOString().slice(0, 10),
  stats: { enrolled: 0, completions: 0, dropouts: 0, avgProgress: 0, avgQuizScore: 0, avgTime: '—' },
  topMaterials: [],
  weakMaterials: [],
})

onMounted(async () => {
  const id = route.params.courseId
  try {
    const { data } = await api.get(`/analytics/courses/${id}/`)
    report.value.course = data.title ?? ''
    report.value.stats.enrolled    = data.total_enrolled ?? 0
    report.value.stats.completions = data.total_completed ?? 0
    report.value.stats.dropouts    = (data.total_enrolled ?? 0) - (data.total_completed ?? 0)
    report.value.stats.avgProgress = data.avg_progress_percent ?? 0
  } catch (_) {}
})

const printReport = () => window.print()

const downloadingPdf = ref(false)
const downloadPdf = async () => {
  downloadingPdf.value = true
  const id = route.params.courseId
  try {
    const { data } = await api.get(`/analytics/courses/${id}/report/pdf/`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `raport_${id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (_) {} finally {
    downloadingPdf.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header no-print">
        <router-link to="/creator/reports" class="back-link">← Wszystkie raporty</router-link>
        <div class="header-row">
          <h1>Raport <span>kursu</span></h1>
          <button class="btn-print" :disabled="downloadingPdf" @click="downloadPdf">
            {{ downloadingPdf ? '⏳ Generowanie…' : '⬇ Pobierz PDF' }}
          </button>
          <button class="btn-print" @click="printReport">🖨️ Drukuj</button>
        </div>
      </div>

      <!-- Nagłówek raportu -->
      <div class="report-header">
        <div>
          <h2>{{ report.course }}</h2>
          <p>Okres: {{ report.period }} · Wygenerowano: {{ report.generated }}</p>
        </div>
        <div class="report-badge">📋 Raport miesięczny</div>
      </div>

      <!-- Główne metryki -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ report.stats.enrolled }}</div>
          <div class="stat-label">Łącznie uczniów</div>
        </div>
        <div class="stat-card success">
          <div class="stat-value">{{ report.stats.completions }}</div>
          <div class="stat-label">Ukończeń</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-value">{{ report.stats.dropouts }}</div>
          <div class="stat-label">Rezygnacji</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ report.stats.avgProgress }}%</div>
          <div class="stat-label">Śr. postęp</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ report.stats.avgQuizScore }}%</div>
          <div class="stat-label">Śr. wynik quizów</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ report.stats.avgTime }}</div>
          <div class="stat-label">Śr. czas nauki</div>
        </div>
      </div>

      <!-- Najlepsze materiały -->
      <div class="section-card">
        <h3>Materiały z najwyższym ukończeniem</h3>
        <div class="mat-list">
          <div v-for="m in report.topMaterials" :key="m.title" class="mat-row">
            <span class="mat-title">{{ m.title }}</span>
            <div class="mat-bar-wrap">
              <div class="mat-bar top" :style="{ width: m.completionRate + '%' }"></div>
            </div>
            <span class="mat-rate top-rate">{{ m.completionRate }}%</span>
            <span class="mat-views">{{ m.views }} wyświetleń</span>
          </div>
        </div>
      </div>

      <!-- Słabe materiały -->
      <div class="section-card">
        <h3>Materiały wymagające poprawy</h3>
        <p class="section-note">Materiały z najniższym wskaźnikiem ukończenia — rozważ ich uproszczenie lub podzielenie na mniejsze części.</p>
        <div class="mat-list">
          <div v-for="m in report.weakMaterials" :key="m.title" class="mat-row">
            <span class="mat-title">{{ m.title }}</span>
            <div class="mat-bar-wrap">
              <div class="mat-bar weak" :style="{ width: m.completionRate + '%' }"></div>
            </div>
            <span class="mat-rate weak-rate">{{ m.completionRate }}%</span>
            <span class="mat-views">{{ m.views }} wyświetleń</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 950px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; justify-content: space-between; align-items: center; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.btn-print { padding: 0.65rem 1.2rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 0.7rem; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: 0.2s; &:hover { background: rgba(255,255,255,0.09); } }

.report-header { display: flex; justify-content: space-between; align-items: flex-start; background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; margin-bottom: 1.5rem; h2 { font-size: 1.25rem; font-weight: 800; margin: 0 0 0.3rem; } p { color: #64748b; font-size: 0.82rem; margin: 0; } .report-badge { font-size: 0.78rem; font-weight: 700; color: #60a5fa; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); border-radius: 0.6rem; padding: 0.35rem 0.85rem; white-space: nowrap; } }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1rem; padding: 1.25rem; text-align: center; .stat-value { font-size: 2rem; font-weight: 900; margin-bottom: 0.25rem; } .stat-label { font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; } &.success .stat-value { color: #10b981; } &.warning .stat-value { color: #f59e0b; } }

.section-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.75rem; margin-bottom: 1.25rem; h3 { font-size: 1rem; font-weight: 700; margin: 0 0 1.25rem; } }
.section-note { color: #64748b; font-size: 0.82rem; margin: -0.75rem 0 1rem; }
.mat-list { display: flex; flex-direction: column; gap: 0.75rem; }
.mat-row { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.mat-title { flex: 1; font-size: 0.87rem; color: #e2e8f0; min-width: 160px; }
.mat-bar-wrap { width: 120px; height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; flex-shrink: 0; }
.mat-bar { height: 100%; border-radius: 3px; &.top { background: #10b981; } &.weak { background: #ef4444; } }
.mat-rate { font-size: 0.8rem; font-weight: 700; white-space: nowrap; &.top-rate { color: #10b981; } &.weak-rate { color: #ef4444; } }
.mat-views { font-size: 0.75rem; color: #475569; white-space: nowrap; }

.chart-placeholder { background: rgba(15,23,42,0.4); border: 2px dashed rgba(255,255,255,0.08); border-radius: 1.25rem; padding: 3rem; text-align: center; color: #475569; span { font-size: 2.5rem; display: block; margin-bottom: 0.75rem; } p { font-size: 0.9rem; color: #64748b; margin-bottom: 0.4rem; } small { font-size: 0.75rem; } }

@media print { .no-print { display: none !important; } .page-wrapper { background: white !important; color: black !important; } }
</style>