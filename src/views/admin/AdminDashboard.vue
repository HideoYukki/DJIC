<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const stats = ref([
  { label: 'Użytkownicy',     value: '—', icon: '👥', trend: '', color: '#3b82f6' },
  { label: 'Kursy aktywne',   value: '—', icon: '📚', trend: '', color: '#10b981' },
  { label: 'Oczekuje recenzji', value: '—', icon: '⏳', trend: 'Wymaga uwagi', color: '#f59e0b' },
  { label: 'Wszystkie kursy', value: '—', icon: '🔥', trend: '', color: '#8b5cf6' },
])

const pendingCourses = ref([])
const recentActivity = ref([])

const activityIcon = (type) => ({ user: '👤', course: '📚', publish: '✅', warn: '⚠️' })[type] || '•'

onMounted(async () => {
  try {
    const [summaryRes, coursesRes, logsRes] = await Promise.all([
      api.get('analytics/admin/summary/'),
      api.get('admin/courses/'),
      api.get('admin/logs/?page_size=5'),
    ])
    const s = summaryRes.data
    stats.value[0].value = String(s.total_users ?? '—')
    stats.value[1].value = String(s.active_courses ?? '—')
    stats.value[2].value = String(s.pending_review ?? '—')
    stats.value[3].value = String(s.total_courses ?? '—')

    pendingCourses.value = (coursesRes.data.results ?? [])
      .filter(c => c.status === 'REVIEW')
      .slice(0, 5)
      .map(c => ({ id: c.id, title: c.title, creator: c.creator_name ?? '—', submitted: c.created_at?.slice(0, 10) ?? '' }))

    recentActivity.value = (logsRes.data.results ?? []).map(l => ({
      action: l.message,
      user: l.user_id ?? 'system',
      time: l.created_at ? new Date(l.created_at).toLocaleString('pl-PL') : '',
      type: l.level === 'ERROR' ? 'warn' : 'info',
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <div class="admin-badge">ADMIN</div>
        <h1>Panel <span>administracyjny</span></h1>
        <p class="subtitle">Przegląd systemu · {{ new Date().toLocaleDateString('pl-PL') }}</p>
      </div>

      <!-- Metryki -->
      <div class="stats-grid">
        <div v-for="s in stats" :key="s.label" class="stat-card" :style="{ '--accent': s.color }">
          <span class="stat-icon">{{ s.icon }}</span>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-trend">{{ s.trend }}</div>
        </div>
      </div>

      <div class="two-col">
        <!-- Oczekujące recenzje -->
        <div class="panel">
          <div class="panel-header">
            <h2>Oczekujące recenzje <span class="badge-count">{{ pendingCourses.length }}</span></h2>
            <router-link to="/admin/courses" class="see-all">Zobacz wszystkie</router-link>
          </div>
          <div class="review-list">
            <div v-for="c in pendingCourses" :key="c.id" class="review-row">
              <div>
                <strong>{{ c.title }}</strong>
                <small>{{ c.creator }} · Przesłano: {{ c.submitted }}</small>
              </div>
              <router-link :to="`/admin/courses/${c.id}/review`" class="btn-review">Recenzuj</router-link>
            </div>
          </div>
        </div>

        <!-- Ostatnia aktywność -->
        <div class="panel">
          <div class="panel-header">
            <h2>Ostatnia aktywność</h2>
            <router-link to="/admin/logs" class="see-all">Pełne logi</router-link>
          </div>
          <div class="activity-list">
            <div v-for="(a, i) in recentActivity" :key="i" class="activity-row">
              <span class="act-icon">{{ activityIcon(a.type) }}</span>
              <div>
                <span class="act-action">{{ a.action }}</span>
                <small>{{ a.user }} · {{ a.time }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Szybkie linki -->
      <div class="quick-links">
        <router-link to="/admin/users" class="quick-link">👥 Zarządzaj użytkownikami</router-link>
        <router-link to="/admin/courses" class="quick-link">📚 Przeglądaj kursy</router-link>
        <router-link to="/admin/settings" class="quick-link">⚙️ Ustawienia platformy</router-link>
        <router-link to="/admin/logs" class="quick-link">📋 Logi systemowe</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .admin-badge { display: inline-block; background: rgba(239,68,68,0.15); color: #ef4444; font-size: 0.65rem; font-weight: 800; letter-spacing: 2px; padding: 0.25rem 0.75rem; border-radius: 999px; border: 1px solid rgba(239,68,68,0.25); margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } } .subtitle { color: #64748b; font-size: 0.85rem; } }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.75rem; @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; border-top: 3px solid var(--accent); .stat-icon { font-size: 1.4rem; display: block; margin-bottom: 0.5rem; } .stat-value { font-size: 2rem; font-weight: 900; margin-bottom: 0.2rem; } .stat-label { font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; } .stat-trend { font-size: 0.72rem; color: var(--accent); margin-top: 0.25rem; } }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem; @media (max-width: 768px) { grid-template-columns: 1fr; } }
.panel { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; h2 { font-size: 0.95rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem; } .see-all { color: #3b82f6; font-size: 0.78rem; font-weight: 700; text-decoration: none; &:hover { text-decoration: underline; } } }
.badge-count { background: rgba(239,68,68,0.15); color: #ef4444; font-size: 0.7rem; font-weight: 800; padding: 0.15rem 0.5rem; border-radius: 999px; }

.review-list, .activity-list { display: flex; flex-direction: column; gap: 0.75rem; }
.review-row { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; padding: 0.75rem; background: rgba(255,255,255,0.02); border-radius: 0.75rem; strong { display: block; font-size: 0.87rem; margin-bottom: 0.2rem; } small { color: #64748b; font-size: 0.72rem; } }
.btn-review { padding: 0.4rem 0.85rem; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.25); color: #60a5fa; border-radius: 0.55rem; text-decoration: none; font-size: 0.78rem; font-weight: 700; white-space: nowrap; transition: 0.15s; &:hover { background: rgba(59,130,246,0.18); } }

.activity-row { display: flex; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); &:last-child { border-bottom: none; } .act-icon { width: 28px; height: 28px; background: rgba(255,255,255,0.04); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; } .act-action { display: block; font-size: 0.85rem; margin-bottom: 0.15rem; } small { color: #64748b; font-size: 0.72rem; } }

.quick-links { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); } }
.quick-link { display: flex; align-items: center; gap: 0.6rem; padding: 0.85rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 0.85rem; text-decoration: none; color: #94a3b8; font-size: 0.85rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(59,130,246,0.06); border-color: rgba(59,130,246,0.2); color: #60a5fa; } }
</style>