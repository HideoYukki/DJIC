<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const auth = useAuthStore()
const db   = useDbStore()

const userId  = computed(() => auth.user?.id)
const userName = computed(() => auth.userName || 'Uczeń')

onMounted(async () => {
  const uid = userId.value
  await Promise.all([
    db.fetchEnrollments(uid),
    db.fetchProgress(uid),
    db.fetchAchievements(uid),
    db.fetchCourses(),
  ])
})

const enrolledCourses = computed(() =>
  db.getEnrolledCourses(userId.value).map(c => {
    const allMats      = db.getCourseMaterials(c.id)
    const completedIds = db.getCompletedMaterials(userId.value, c.id)
    const nextMat      = allMats.find(m => !completedIds.includes(m.id))
    return {
      ...c,
      progress:          db.getCourseProgress(userId.value, c.id),
      chapter:           nextMat?.title ?? 'Kurs ukończony',
      chaptersCount:     allMats.length,
      completedChapters: completedIds.length,
    }
  })
)

const totalXP          = computed(() => db.getTotalXP(userId.value))
const achievements     = computed(() => db.getUserAchievements(userId.value))
const unlockedCount    = computed(() => achievements.value.filter(a => a.unlocked).length)
const totalCompleted   = computed(() => enrolledCourses.value.reduce((s, c) => s + c.completedChapters, 0))

const xpLevel        = computed(() => Math.floor(totalXP.value / 500) + 1)
const xpToNextLevel  = computed(() => xpLevel.value * 500)

const recentActivity = computed(() =>
  db.progress
    .filter(p => p.userId === userId.value)
    .slice(-5)
    .reverse()
    .map(p => {
      const mat    = db.getMaterialById(p.courseId, p.materialId)
      const course = db.getCourseById(p.courseId)
      return {
        icon:   '✅',
        text:   mat ? `Ukończono: ${mat.title}` : 'Ukończono materiał',
        course: course?.title ?? '',
        time:   p.completedAt ? new Date(p.completedAt).toLocaleDateString('pl-PL') : '',
      }
    })
)

const recommended = computed(() =>
  db.allCourses
    .filter(c => c.status === 'ACTIVE' && !db.isEnrolled(userId.value, c.id))
    .slice(0, 3)
)

const xpPercent = (xp, max) => Math.round((xp / max) * 100)
</script>

<template>
  <div class="page-wrapper">
    <div class="container">

      <!-- Nagłówek -->
      <header class="page-header">
        <div class="greeting">
          <div class="avatar">{{ userName.charAt(0).toUpperCase() }}</div>
          <div>
            <h1>Cześć, <span>{{ userName.split(' ')[0] }}</span> 👋</h1>
            <p>Kontynuuj naukę tam, gdzie ją przerwałeś.</p>
          </div>
        </div>
        <div class="xp-widget">
          <div class="xp-label">Poziom {{ xpLevel }} · {{ totalXP }} XP</div>
          <div class="xp-bar-track">
            <div class="xp-bar-fill" :style="{ width: xpPercent(totalXP, xpToNextLevel) + '%' }"></div>
          </div>
          <div class="xp-next">{{ xpToNextLevel - totalXP }} XP do poziomu {{ xpLevel + 1 }}</div>
        </div>
      </header>

      <!-- Szybkie statystyki -->
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-icon">📚</span>
          <div><strong>{{ enrolledCourses.length }}</strong><small>Aktywne kursy</small></div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">✅</span>
          <div><strong>{{ totalCompleted }}</strong><small>Ukończone lekcje</small></div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🏆</span>
          <div><strong>{{ unlockedCount }}</strong><small>Odznaki</small></div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">⏱️</span>
          <div><strong>—</strong><small>Czas nauki</small></div>
        </div>
      </div>

      <div class="dashboard-grid">

        <!-- Aktywne kursy -->
        <section class="section-card">
          <div class="section-header">
            <h2>Kontynuuj naukę</h2>
            <router-link to="/my-courses" class="see-all">Wszystkie kursy →</router-link>
          </div>
          <div class="courses-list">
            <div v-for="c in enrolledCourses" :key="c.id" class="course-row">
              <div class="course-thumb-mini">📖</div>
              <div class="course-info">
                <h3>{{ c.title }}</h3>
                <p class="lesson-name">Następna lekcja: {{ c.chapter }}</p>
                <div class="progress-bar-wrap">
                  <div class="progress-bar" :style="{ width: c.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ c.progress }}% · {{ c.completedChapters }}/{{ c.chaptersCount }} rozdziałów</span>
              </div>
              <router-link :to="`/courses/${c.id}/learn`" class="btn-continue">Kontynuuj</router-link>
            </div>
          </div>
        </section>

        <!-- Aktywność -->
        <section class="section-card">
          <div class="section-header">
            <h2>Ostatnia aktywność</h2>
          </div>
          <!-- TODO: GET /api/user/activity/?limit=10 → lista ostatnich działań z timestampem -->
          <div class="activity-list">
            <div v-for="(act, i) in recentActivity" :key="i" class="activity-row">
              <span class="act-icon">{{ act.icon }}</span>
              <div class="act-info">
                <p>{{ act.text }}</p>
                <small v-if="act.course">{{ act.course }} · {{ act.time }}</small>
                <small v-else>{{ act.time }}</small>
              </div>
            </div>
          </div>
          <router-link to="/progress" class="btn-link">Zobacz pełne statystyki →</router-link>
        </section>

      </div>

      <!-- Polecane kursy -->
      <section class="section-card">
        <div class="section-header">
          <h2>Polecane dla Ciebie</h2>
          <!-- TODO: GET /api/courses/recommended/?userId= → kursy dopasowane na podstawie profilu -->
          <router-link to="/courses" class="see-all">Przeglądaj wszystkie →</router-link>
        </div>
        <div v-if="recommended.length" class="recommended-grid">
          <div v-for="c in recommended" :key="c.id" class="rec-card" @click="$router.push(`/courses/${c.id}`)">
            <div class="rec-thumb">📖</div>
            <div class="rec-info">
              <span class="rec-tag">{{ c.category }}</span>
              <h4>{{ c.title }}</h4>
              <span class="rec-meta">⭐ {{ c.rating || '—' }} · {{ c.author || '—' }}</span>
            </div>
          </div>
        </div>
        <p v-else class="empty-rec">Zapisz się na więcej kursów, aby zobaczyć rekomendacje.</p>
      </section>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1200px; margin: 0 auto; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.greeting {
  display: flex;
  align-items: center;
  gap: 1rem;
  .avatar {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.3rem;
  }
  h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } }
  p { color: #64748b; margin: 0; font-size: 0.9rem; }
}

.xp-widget {
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  min-width: 260px;
  .xp-label { font-size: 0.82rem; font-weight: 700; color: #60a5fa; margin-bottom: 0.5rem; }
  .xp-bar-track { height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden; margin-bottom: 0.4rem; }
  .xp-bar-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #6366f1); border-radius: 4px; transition: width 0.5s ease; }
  .xp-next { font-size: 0.75rem; color: #64748b; }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
  @media (max-width: 700px) { grid-template-columns: repeat(2, 1fr); }
}
.stat-card {
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 1rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  .stat-icon { font-size: 1.5rem; }
  strong { display: block; font-size: 1.4rem; font-weight: 800; }
  small { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.section-card {
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 1.25rem;
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;
  h2 { font-size: 1.1rem; font-weight: 700; margin: 0; }
  .see-all { color: #3b82f6; text-decoration: none; font-size: 0.83rem; font-weight: 600; &:hover { text-decoration: underline; } }
}

.courses-list { display: flex; flex-direction: column; gap: 1.25rem; }
.course-row {
  display: flex; align-items: center; gap: 1rem;
  .course-thumb-mini { font-size: 1.8rem; flex-shrink: 0; opacity: 0.7; }
  .course-info { flex: 1; min-width: 0; }
  h3 { font-size: 0.9rem; font-weight: 700; margin: 0 0 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .lesson-name { color: #64748b; font-size: 0.78rem; margin-bottom: 0.5rem; }
  .progress-bar-wrap { height: 5px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; margin-bottom: 0.25rem; }
  .progress-bar { height: 100%; background: #3b82f6; border-radius: 3px; }
  .progress-text { color: #475569; font-size: 0.72rem; }
}
.btn-continue {
  padding: 0.5rem 1rem;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 0.6rem;
  color: #60a5fa;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
  transition: 0.2s;
  flex-shrink: 0;
  &:hover { background: rgba(59,130,246,0.2); }
}

.activity-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1rem; }
.activity-row {
  display: flex; gap: 0.85rem; align-items: flex-start;
  .act-icon { font-size: 1rem; flex-shrink: 0; margin-top: 0.05rem; }
  .act-info { p { margin: 0 0 0.15rem; font-size: 0.87rem; color: #e2e8f0; } small { color: #64748b; font-size: 0.75rem; } }
}
.btn-link { color: #3b82f6; text-decoration: none; font-size: 0.83rem; font-weight: 600; &:hover { text-decoration: underline; } }

.recommended-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}
.rec-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 1rem;
  overflow: hidden;
  cursor: pointer;
  transition: 0.2s;
  &:hover { border-color: rgba(59,130,246,0.3); transform: translateY(-2px); }
  .rec-thumb { height: 90px; background: rgba(30,41,59,0.5); display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
  .rec-info { padding: 0.9rem; }
  .rec-tag { font-size: 0.68rem; color: #3b82f6; font-weight: 700; text-transform: uppercase; }
  h4 { font-size: 0.87rem; font-weight: 700; margin: 0.35rem 0; line-height: 1.3; }
  .rec-meta { font-size: 0.75rem; color: #64748b; }
}

.empty-rec { color: #475569; font-size: 0.85rem; margin: 0; padding: 1rem 0; }
</style>