<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const stats = ref([
  { icon: '👥', label: 'Uczniowie',      value: '—', trend: '', color: '#3b82f6' },
  { icon: '📚', label: 'Aktywne kursy', value: '—', trend: '', color: '#10b981' },
  { icon: '📋', label: 'Wszystkich kursów', value: '—', trend: '', color: '#f59e0b' },
  { icon: '✏️', label: 'Szkice',        value: '—', trend: '', color: '#8b5cf6' },
])

const courses = ref([])
const recentEnrollments = ref([])

const statusBadge = (s) => ({ ACTIVE: { label: 'Aktywny', color: '#10b981' }, DRAFT: { label: 'Szkic', color: '#64748b' }, REVIEW: { label: 'Recenzja', color: '#f59e0b' }, ARCHIVED: { label: 'Archiwum', color: '#ef4444' } }[s] || { label: s, color: '#64748b' })

onMounted(async () => {
  try {
    const [coursesRes, summaryRes] = await Promise.all([
      api.get('courses/creator/'),
      api.get('analytics/creator/summary/'),
    ])
    courses.value = (coursesRes.data.results ?? coursesRes.data ?? []).map(c => ({
      id: c.id,
      title: c.title,
      students: c.students_count ?? 0,
      rating: c.rating ?? null,
      status: c.status,
      completion: 0,
    }))
    const s = summaryRes.data
    stats.value[0].value = String(s.total_students ?? '—')
    stats.value[1].value = String(s.active_courses ?? '—')
    stats.value[2].value = String(s.total_courses ?? '—')
    stats.value[3].value = String(s.draft_courses ?? '—')
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <div>
          <h1>Panel <span>Twórcy</span></h1>
          <p class="subtitle">Witaj! Oto podsumowanie Twoich kursów.</p>
        </div>
        <router-link to="/creator/courses/new" class="btn-primary">+ Nowy kurs</router-link>
      </header>

      <!-- Statystyki -->
      <div class="stats-grid">
        <div v-for="s in stats" :key="s.label" class="stat-card">
          <div class="stat-icon" :style="{ color: s.color }">{{ s.icon }}</div>
          <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-trend">{{ s.trend }}</div>
        </div>
      </div>

      <div class="dashboard-grid">

        <!-- Kursy -->
        <div class="section-card">
          <div class="section-header">
            <h2>Twoje kursy</h2>
            <router-link to="/creator/courses" class="see-all">Zarządzaj wszystkimi →</router-link>
          </div>
          <div class="courses-table">
            <div v-for="c in courses" :key="c.id" class="course-row">
              <div class="course-info">
                <h3>{{ c.title }}</h3>
                <div class="course-meta">
                  <span class="status-dot" :style="{ color: statusBadge(c.status).color }">● {{ statusBadge(c.status).label }}</span>
                  <span>👥 {{ c.students }}</span>
                  <span>⭐ {{ c.rating }}</span>
                </div>
              </div>
              <div class="course-actions-mini">
                <router-link :to="`/creator/courses/${c.id}/analytics`" class="btn-mini">Analityka</router-link>
                <router-link :to="`/creator/courses/${c.id}/edit`" class="btn-mini">Edytuj</router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Ostatnie zapisy -->
        <div class="section-card">
          <div class="section-header">
            <h2>Ostatnie zapisy</h2>
            <!-- TODO: GET /api/creator/enrollments/?limit=10 → lista ostatnich zapisów z danymi ucznia -->
          </div>
          <div class="enrollments-list">
            <div v-for="(e, i) in recentEnrollments" :key="i" class="enrollment-row">
              <div class="student-avatar">{{ e.student.charAt(0) }}</div>
              <div class="enrollment-info">
                <strong>{{ e.student }}</strong>
                <small>{{ e.course }}</small>
              </div>
              <span class="enroll-time">{{ e.time }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Wykresy - placeholder -->
      <div class="section-card chart-placeholder">
        <h2>Aktywność uczniów — ostatnie 30 dni</h2>
        <!-- TODO: Zintegruj ApexCharts / Chart.js → GET /api/creator/analytics/activity/?days=30 -->
        <div class="chart-mock">
          <div class="chart-bar-row">
            <div v-for="i in 30" :key="i" class="chart-bar" :style="{ height: (Math.sin(i * 0.5) * 40 + 50) + '%' }"></div>
          </div>
          <p class="chart-note">Wykres aktywności będzie renderowany przez bibliotekę ApexCharts po integracji z API.</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; h1 { font-size: 2rem; font-weight: 800; span { color: #3b82f6; } margin: 0 0 0.3rem; } .subtitle { color: #64748b; margin: 0; } }
.btn-primary { padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(59,130,246,0.3); transition: 0.2s; &:hover { background: #2563eb; } }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; .stat-icon { font-size: 1.5rem; margin-bottom: 0.5rem; } .stat-value { font-size: 2rem; font-weight: 900; margin-bottom: 0.25rem; } .stat-label { font-size: 0.78rem; color: #64748b; font-weight: 600; text-transform: uppercase; } .stat-trend { font-size: 0.75rem; color: #475569; margin-top: 0.25rem; } }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; @media (max-width: 900px) { grid-template-columns: 1fr; } }
.section-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.75rem; margin-bottom: 1.5rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; h2 { font-size: 1rem; font-weight: 700; margin: 0; } .see-all { color: #3b82f6; text-decoration: none; font-size: 0.82rem; font-weight: 600; } }

.courses-table { display: flex; flex-direction: column; gap: 0.85rem; }
.course-row { display: flex; align-items: center; gap: 1rem; padding: 0.9rem; background: rgba(255,255,255,0.03); border-radius: 0.75rem; transition: 0.15s; &:hover { background: rgba(255,255,255,0.05); } .course-info { flex: 1; } h3 { font-size: 0.88rem; font-weight: 700; margin: 0 0 0.3rem; } .course-meta { display: flex; gap: 0.85rem; font-size: 0.75rem; color: #64748b; } .status-dot { font-weight: 700; font-size: 0.75rem; } }
.course-actions-mini { display: flex; gap: 0.4rem; }
.btn-mini { padding: 0.35rem 0.7rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.45rem; color: #94a3b8; text-decoration: none; font-size: 0.72rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(59,130,246,0.1); color: #60a5fa; border-color: rgba(59,130,246,0.2); } }

.enrollments-list { display: flex; flex-direction: column; gap: 0.75rem; }
.enrollment-row { display: flex; align-items: center; gap: 0.85rem; }
.student-avatar { width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; flex-shrink: 0; }
.enrollment-info { flex: 1; strong { display: block; font-size: 0.87rem; } small { color: #64748b; font-size: 0.75rem; } }
.enroll-time { font-size: 0.72rem; color: #475569; white-space: nowrap; }

.chart-placeholder { }
.chart-mock {
  .chart-bar-row { display: flex; align-items: flex-end; gap: 3px; height: 100px; margin-bottom: 1rem; }
  .chart-bar { flex: 1; background: rgba(59,130,246,0.3); border-radius: 2px 2px 0 0; min-height: 4px; }
  .chart-note { color: #475569; font-size: 0.8rem; text-align: center; font-style: italic; }
}
</style>