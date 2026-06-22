<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const auth = useAuthStore()
const db   = useDbStore()

const userId = computed(() => auth.user?.id)

onMounted(async () => {
  const uid = userId.value
  await Promise.all([
    db.fetchEnrollments(uid),
    db.fetchProgress(uid),
  ])
})

// TODO: GET $env(VITE_API_URL)/my-courses — lista zapisanych kursów z postępem
const courses = computed(() =>
  db.getEnrolledCourses(userId.value).map(c => {
    const allMats      = db.getCourseMaterials(c.id)
    const completedIds = db.getCompletedMaterials(userId.value, c.id)
    const lastMat      = completedIds.length
      ? allMats.find(m => m.id === completedIds.at(-1))
      : null
    return {
      ...c,
      progress:          db.getCourseProgress(userId.value, c.id),
      completedChapters: completedIds.length,
      totalChapters:     allMats.length,
      lastLesson:        lastMat?.title ?? (allMats[0]?.title ?? '—'),
      xpEarned:          completedIds.length * 50,
    }
  })
)

const totalXP = computed(() => courses.value.reduce((s, c) => s + c.xpEarned, 0))

const statusLabel = (progress) => {
  if (progress === 100) return { label: 'Ukończony', color: '#10b981' }
  if (progress > 0) return { label: 'W trakcie', color: '#3b82f6' }
  return { label: 'Nierozpoczęty', color: '#64748b' }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <h1>Moje <span>kursy</span></h1>
        <p class="subtitle">{{ courses.length }} kursów · łącznie {{ totalXP }} XP</p>
      </header>

      <div class="courses-list">
        <div v-for="c in courses" :key="c.id" class="course-card">
          <!-- TODO: $env(VITE_API_URL)/courses/:id/thumbnail — CDN URL po integracji -->
          <img :src="c.thumbnail" :alt="c.title" class="course-thumb" />
          <div class="course-main">
            <div class="course-top">
              <span class="category">{{ c.category }}</span>
              <span class="status-badge" :style="{ color: statusLabel(c.progress).color }">
                ● {{ statusLabel(c.progress).label }}
              </span>
            </div>
            <h3>{{ c.title }}</h3>
            <p class="author">Autor: {{ c.author }}</p>
            <div class="progress-section">
              <div class="progress-info">
                <span>{{ c.completedChapters }}/{{ c.totalChapters }} rozdziałów</span>
                <span class="xp">+{{ c.xpEarned }} XP</span>
              </div>
              <div class="progress-bar-track">
                <div class="progress-bar-fill" :style="{ width: c.progress + '%' }"></div>
              </div>
            </div>
            <p class="last-lesson">Ostatnia lekcja: <em>{{ c.lastLesson }}</em></p>
          </div>
          <div class="course-actions">
            <router-link :to="`/courses/${c.id}/learn`" class="btn-continue">
              {{ c.progress === 100 ? '▶ Powtórz kurs' : '▶ Kontynuuj' }}
            </router-link>
            <router-link :to="`/courses/${c.id}`" class="btn-ghost">Szczegóły</router-link>
            <router-link v-if="c.progress === 100" :to="`/courses/${c.id}/certificate`" class="btn-cert">🏅 Certyfikat</router-link>
          </div>
        </div>
      </div>

      <div class="discover-cta">
        <p>Chcesz poszerzyć wiedzę?</p>
        <router-link to="/courses" class="btn-primary">Odkryj nowe kursy →</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 2.5rem; h1 { font-size: 2rem; font-weight: 800; span { color: #3b82f6; } } .subtitle { color: #64748b; margin-top: 0.4rem; } }

.courses-list { display: flex; flex-direction: column; gap: 1.25rem; margin-bottom: 2.5rem; }

.course-card {
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 1.25rem;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 80px 1fr auto;
  gap: 1.5rem;
  align-items: center;
  transition: 0.2s;
  &:hover { border-color: rgba(59,130,246,0.25); }
  @media (max-width: 768px) { grid-template-columns: 1fr; .course-thumb { display: none; } }
}
.course-thumb { width: 80px; height: 80px; border-radius: 1rem; object-fit: cover; flex-shrink: 0; background: #1e293b; display: block; }
.course-top { display: flex; justify-content: space-between; margin-bottom: 0.4rem; }
.category { font-size: 0.72rem; color: #3b82f6; font-weight: 700; text-transform: uppercase; }
.status-badge { font-size: 0.75rem; font-weight: 700; }
h3 { font-size: 1.05rem; font-weight: 700; margin: 0 0 0.2rem; }
.author { color: #64748b; font-size: 0.82rem; margin-bottom: 0.75rem; }
.progress-section { margin-bottom: 0.4rem; }
.progress-info { display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748b; margin-bottom: 0.35rem; .xp { color: #f59e0b; font-weight: 700; } }
.progress-bar-track { height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: #3b82f6; border-radius: 3px; }
.last-lesson { font-size: 0.78rem; color: #475569; em { color: #64748b; font-style: normal; } }
.course-actions { display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-end; min-width: 140px; }
.btn-continue { padding: 0.6rem 1.1rem; background: #3b82f6; color: white; border-radius: 0.65rem; text-decoration: none; font-size: 0.83rem; font-weight: 700; text-align: center; white-space: nowrap; transition: 0.2s; &:hover { background: #2563eb; } }
.btn-ghost { padding: 0.5rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.65rem; text-decoration: none; font-size: 0.8rem; font-weight: 600; text-align: center; transition: 0.2s; &:hover { border-color: rgba(255,255,255,0.15); } }
.btn-cert { padding: 0.5rem 1rem; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #f59e0b; border-radius: 0.65rem; text-decoration: none; font-size: 0.8rem; font-weight: 700; text-align: center; transition: 0.2s; &:hover { background: rgba(245,158,11,0.18); } }

.discover-cta { text-align: center; padding: 2rem; p { color: #64748b; margin-bottom: 1rem; } }
.btn-primary { display: inline-block; padding: 0.8rem 2rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; transition: 0.2s; &:hover { background: #2563eb; } }
</style>