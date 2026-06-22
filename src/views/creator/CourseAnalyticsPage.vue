<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()

const metrics = ref([
  { label: 'Łącznie uczniów',      value: '—', icon: '👥', trend: '' },
  { label: 'Wskaźnik ukończenia',  value: '—', icon: '✅', trend: '' },
  { label: 'Śr. postęp',          value: '—', icon: '📊', trend: '' },
  { label: 'Materiałów łącznie',   value: '—', icon: '📚', trend: '' },
])

const dropoutPoints = ref([])

const chartSeries = ref([{ name: 'Nowe zapisy', data: [] }])
const chartOptions = ref({
  chart: { type: 'area', background: 'transparent', toolbar: { show: false }, animations: { enabled: true } },
  colors: ['#3b82f6'],
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.02 } },
  stroke: { curve: 'smooth', width: 2 },
  xaxis: { type: 'datetime', labels: { style: { colors: '#64748b' }, datetimeUTC: false }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: { labels: { style: { colors: '#64748b' } }, min: 0, tickAmount: 4, forceNiceScale: true },
  grid: { borderColor: 'rgba(255,255,255,0.05)', strokeDashArray: 4 },
  theme: { mode: 'dark' },
  tooltip: { theme: 'dark', x: { format: 'dd MMM' } },
  dataLabels: { enabled: false },
})

onMounted(async () => {
  try {
    const { data } = await api.get(`/analytics/courses/${route.params.id}/`)
    metrics.value[0].value = String(data.total_enrolled ?? '—')
    metrics.value[1].value = `${data.completion_rate ?? 0}%`
    metrics.value[2].value = `${data.avg_progress_percent ?? 0}%`
    metrics.value[3].value = String(data.total_materials ?? '—')
  } catch (_) {}

  try {
    const { data } = await api.get(`/analytics/courses/${route.params.id}/views/`, { params: { period: 14 } })
    chartSeries.value = [{
      name: 'Nowe zapisy',
      data: (data.days ?? []).map(d => [new Date(d.date).getTime(), d.count]),
    }]
  } catch (_) {}

  try {
    const { data } = await api.get(`/analytics/courses/${route.params.id}/dropouts/`)
    dropoutPoints.value = (data.results ?? []).slice(0, 6).map(d => ({
      material: d.material_title,
      dropouts: d.enrolled - d.completions,
      percent: d.dropout_rate,
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${route.params.id}/edit`" class="back-link">← Edycja kursu</router-link>
        <h1>Analityka <span>kursu</span></h1>
        <p class="subtitle">Dane aktualizowane co 5 minut · Kurs: Podstawy Vue.js 3</p>
      </div>

      <!-- Metryki -->
      <div class="metrics-grid">
        <div v-for="m in metrics" :key="m.label" class="metric-card">
          <span class="metric-icon">{{ m.icon }}</span>
          <div class="metric-value">{{ m.value }}</div>
          <div class="metric-label">{{ m.label }}</div>
          <div class="metric-trend">{{ m.trend }}</div>
        </div>
      </div>

      <!-- Wykres wyświetleń -->
      <div class="chart-card">
        <h2>Nowe zapisy — ostatnie 14 dni</h2>
        <VueApexCharts
          type="area"
          height="200"
          :series="chartSeries"
          :options="chartOptions"
        />
      </div>

      <!-- Punkty odpadania -->
      <div class="dropout-card">
        <h2>Punkty odpadania uczniów</h2>
        <p class="dropout-desc">Materiały, po których uczniowie najczęściej kończą naukę. Rozważ ich poprawę.</p>
        <div v-if="dropoutPoints.length" class="dropout-list">
          <div v-for="d in dropoutPoints" :key="d.material" class="dropout-row">
            <span class="dropout-mat">{{ d.material }}</span>
            <div class="dropout-bar-wrap">
              <div class="dropout-bar" :style="{ width: d.percent + '%' }"></div>
            </div>
            <span class="dropout-count">{{ d.dropouts }} uczniów ({{ d.percent }}%)</span>
          </div>
        </div>
        <p v-else class="dropout-empty">Brak danych — za mało uczniów lub wszystkie materiały ukończone.</p>
      </div>

      <!-- Quick links -->
      <div class="quick-links-row">
        <router-link :to="`/creator/courses/${route.params.id}/students`" class="quick-card">
          <span>👥</span><strong>Lista uczniów</strong><small>Postępy i aktywność</small>
        </router-link>
        <router-link :to="`/creator/reports/${route.params.id}`" class="quick-card">
          <span>📋</span><strong>Szczegółowy raport</strong><small>Eksport do PDF</small>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } } .subtitle { color: #64748b; font-size: 0.85rem; } }

.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.metric-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; .metric-icon { font-size: 1.4rem; display: block; margin-bottom: 0.5rem; } .metric-value { font-size: 2rem; font-weight: 900; margin-bottom: 0.25rem; } .metric-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; } .metric-trend { font-size: 0.72rem; color: #10b981; margin-top: 0.25rem; } }

.chart-card, .dropout-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.75rem; margin-bottom: 1.5rem; h2 { font-size: 1rem; font-weight: 700; margin: 0 0 1.25rem; } }

.dropout-empty { color: #475569; font-size: 0.85rem; text-align: center; padding: 1.5rem 0; }

.dropout-desc { color: #64748b; font-size: 0.85rem; margin-bottom: 1.25rem; }
.dropout-list { display: flex; flex-direction: column; gap: 1rem; }
.dropout-row { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; .dropout-mat { flex: 1; font-size: 0.87rem; color: #e2e8f0; min-width: 200px; } .dropout-bar-wrap { width: 120px; height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; flex-shrink: 0; } .dropout-bar { height: 100%; background: #ef4444; border-radius: 3px; } .dropout-count { font-size: 0.78rem; color: #ef4444; white-space: nowrap; } }

.quick-links-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.quick-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1rem; padding: 1.25rem; text-decoration: none; color: white; display: flex; align-items: center; gap: 1rem; transition: 0.2s; &:hover { border-color: rgba(59,130,246,0.25); background: rgba(59,130,246,0.06); } span { font-size: 1.5rem; } strong { display: block; font-size: 0.9rem; } small { color: #64748b; font-size: 0.75rem; } }
</style>