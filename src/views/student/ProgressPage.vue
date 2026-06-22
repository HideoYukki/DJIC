<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'
import { api } from '@/api'

const auth = useAuthStore()
const db   = useDbStore()
const userId = computed(() => auth.user?.id)

const totalXP  = computed(() => db.getTotalXP(userId.value))
const level    = computed(() => Math.floor(totalXP.value / 500) + 1)
const xpToNext = computed(() => level.value * 500)

const enrolledCourses = computed(() => db.getEnrolledCourses(userId.value))

const stats = computed(() => ({
  xp:               totalXP.value,
  level:            level.value,
  xpToNext:         xpToNext.value,
  coursesCompleted: enrolledCourses.value.filter(c => db.getCourseProgress(userId.value, c.id) === 100).length,
  totalCourses:     enrolledCourses.value.length,
  totalTime:        '—',
  streak:           0,
}))

const courses = computed(() =>
  enrolledCourses.value.map(c => {
    const progress = db.getCourseProgress(userId.value, c.id)
    const completed = db.getCompletedMaterials(userId.value, c.id).length
    return {
      id: c.id,
      title: c.title,
      progress,
      xpEarned: completed * 10,
      totalXP:  (db.getCourseMaterials(c.id).length) * 10,
      lastActivity: '—',
    }
  })
)

const weeklyActivity = computed(() => {
  const activity = [
    { day: 'Pon', minutes: 0 },
    { day: 'Wt',  minutes: 0 },
    { day: 'Śr',  minutes: 0 },
    { day: 'Czw', minutes: 0 },
    { day: 'Pt',  minutes: 0 },
    { day: 'Sob', minutes: 0 },
    { day: 'Nd',  minutes: 0 },
  ]
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  db.progress
    .filter(p => p.userId === userId.value && p.completedAt)
    .forEach(p => {
      const d = new Date(p.completedAt)
      if (d.getTime() >= weekAgo) {
        // JS getDay(): 0=Nd, 1=Pon, ..., 6=Sob → index w tablicy (Pon=0)
        const idx = (d.getDay() + 6) % 7
        activity[idx].minutes += 10
      }
    })
  return activity
})

const maxMinutes = computed(() => Math.max(...weeklyActivity.value.map(d => d.minutes)) || 1)
const barHeight = (min) => Math.round((min / maxMinutes.value) * 100)

onMounted(async () => {
  await Promise.all([
    db.fetchEnrollments(userId.value),
    db.fetchProgress(userId.value),
    db.fetchAchievements(userId.value),
  ])
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <h1>Moje <span>Postępy</span></h1>
        <p class="subtitle">Analizuj swoją naukę i obserwuj wzrost</p>
      </header>

      <!-- Główne statystyki -->
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-top">
            <span class="stat-icon">⚡</span>
            <span class="stat-label">Poziom {{ stats.level }}</span>
          </div>
          <div class="stat-value">{{ stats.xp }} XP</div>
          <div class="xp-bar"><div class="xp-fill" :style="{ width: (stats.xp / stats.xpToNext * 100) + '%' }"></div></div>
          <div class="stat-note">{{ stats.xpToNext - stats.xp }} XP do poziomu {{ stats.level + 1 }}</div>
        </div>
        <div class="stat-card"><span class="sc-icon">🔥</span><div class="sc-val">{{ stats.streak }}</div><div class="sc-label">Dni z rzędu</div></div>
        <div class="stat-card"><span class="sc-icon">⏱️</span><div class="sc-val">{{ stats.totalTime }}</div><div class="sc-label">Łączny czas nauki</div></div>
        <div class="stat-card"><span class="sc-icon">📚</span><div class="sc-val">{{ stats.totalCourses }}</div><div class="sc-label">Aktywne kursy</div></div>
      </div>

      <div class="section-card">
        <h2>Aktywność w tym tygodniu</h2>
        <div class="bar-chart">
          <div v-for="d in weeklyActivity" :key="d.day" class="bar-group">
            <div class="bar-track">
              <div class="bar-fill" :style="{ height: barHeight(d.minutes) + '%' }"></div>
            </div>
            <span class="bar-label">{{ d.day }}</span>
            <span class="bar-val">{{ d.minutes }}m</span>
          </div>
        </div>
      </div>

      <!-- Postęp per kurs -->
      <div class="section-card">
        <h2>Postęp w kursach</h2>
        <div class="courses-progress">
          <div v-for="c in courses" :key="c.id" class="course-prog-row">
            <div class="course-prog-info">
              <div>
                <h3>{{ c.title }}</h3>
                <small>Ostatnia aktywność: {{ c.lastActivity }}</small>
              </div>
              <div class="course-prog-xp">
                <span class="xp-earned">{{ c.xpEarned }} XP</span>
                <span class="xp-total">/ {{ c.totalXP }}</span>
              </div>
            </div>
            <div class="prog-bar-track">
              <div class="prog-bar-fill" :style="{ width: c.progress + '%' }"></div>
              <span class="prog-pct">{{ c.progress }}%</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; h1 { font-size: 2rem; font-weight: 800; span { color: #3b82f6; } } .subtitle { color: #64748b; margin-top: 0.4rem; } }

.stats-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; @media (max-width: 768px) { grid-template-columns: 1fr 1fr; } }
.stat-card {
  background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem;
  &.primary { display: flex; flex-direction: column; gap: 0.5rem; }
  .stat-top { display: flex; align-items: center; gap: 0.5rem; .stat-icon { font-size: 1.1rem; } .stat-label { font-size: 0.78rem; color: #64748b; font-weight: 700; text-transform: uppercase; } }
  .stat-value { font-size: 1.8rem; font-weight: 900; color: white; }
  .xp-bar { height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; }
  .xp-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #6366f1); border-radius: 3px; }
  .stat-note { font-size: 0.75rem; color: #64748b; }
  .sc-icon { font-size: 1.5rem; display: block; margin-bottom: 0.5rem; }
  .sc-val { font-size: 1.6rem; font-weight: 800; }
  .sc-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
}

.section-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.75rem; margin-bottom: 1.5rem; h2 { font-size: 1.05rem; font-weight: 700; margin: 0 0 1.5rem; } }

.bar-chart { display: flex; align-items: flex-end; gap: 0.75rem; height: 120px; }
.bar-group {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 0.3rem; height: 100%;
  .bar-track { flex: 1; width: 100%; background: rgba(255,255,255,0.05); border-radius: 0.4rem; display: flex; align-items: flex-end; overflow: hidden; }
  .bar-fill { width: 100%; background: #3b82f6; border-radius: 0.4rem 0.4rem 0 0; min-height: 2px; transition: height 0.3s ease; }
  .bar-label { font-size: 0.72rem; color: #64748b; }
  .bar-val { font-size: 0.65rem; color: #475569; }
}

.courses-progress { display: flex; flex-direction: column; gap: 1.5rem; }
.course-prog-row { }
.course-prog-info { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; h3 { font-size: 0.9rem; font-weight: 700; margin: 0 0 0.15rem; } small { color: #475569; font-size: 0.75rem; } }
.course-prog-xp { text-align: right; .xp-earned { color: #f59e0b; font-weight: 700; font-size: 0.9rem; } .xp-total { color: #475569; font-size: 0.78rem; } }
.prog-bar-track { height: 8px; background: rgba(255,255,255,0.07); border-radius: 4px; overflow: hidden; position: relative; }
.prog-bar-fill { height: 100%; background: #3b82f6; border-radius: 4px; }
.prog-pct { position: absolute; right: 0; top: -18px; font-size: 0.72rem; color: #64748b; }
</style>