<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const courses = ref([])

const filterStatus = ref('')
const statuses = ['ACTIVE', 'DRAFT', 'REVIEW', 'ARCHIVED']

const filtered = computed(() =>
  filterStatus.value ? courses.value.filter(c => c.status === filterStatus.value) : courses.value
)

const statusConfig = (s) => ({
  ACTIVE: { label: 'Aktywny', color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
  DRAFT: { label: 'Szkic', color: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
  REVIEW: { label: 'W recenzji', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
  ARCHIVED: { label: 'Archiwum', color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
}[s] || { label: s, color: '#64748b', bg: 'rgba(100,116,139,0.1)' })

const deleteCourse = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć ten kurs?')) return
  try {
    await api.delete(`/courses/${id}/edit/`)
    courses.value = courses.value.filter(c => c.id !== id)
  } catch (_) {}
}

onMounted(async () => {
  try {
    const { data } = await api.get('courses/creator/')
    courses.value = (data.results ?? data ?? []).map(c => ({
      id: c.id,
      title: c.title,
      status: c.status,
      students: c.students_count ?? 0,
      chapters: 0,
      rating: c.rating ?? null,
      updatedAt: c.updated_at?.slice(0, 10) ?? '',
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <div>
          <h1>Moje <span>kursy</span></h1>
          <p class="subtitle">{{ courses.length }} kursów · zarządzaj i edytuj</p>
        </div>
        <router-link to="/creator/courses/new" class="btn-primary">+ Utwórz kurs</router-link>
      </header>

      <!-- Filtry statusu -->
      <div class="filter-tabs">
        <button class="tab" :class="{ active: filterStatus === '' }" @click="filterStatus = ''">Wszystkie ({{ courses.length }})</button>
        <button v-for="s in statuses" :key="s" class="tab" :class="{ active: filterStatus === s }" @click="filterStatus = s">
          {{ statusConfig(s).label }} ({{ courses.filter(c => c.status === s).length }})
        </button>
      </div>

      <!-- Tabela kursów -->
      <div class="courses-list">
        <div v-for="c in filtered" :key="c.id" class="course-row">
          <div class="course-main">
            <div class="status-chip" :style="{ color: statusConfig(c.status).color, background: statusConfig(c.status).bg }">
              {{ statusConfig(c.status).label }}
            </div>
            <h3>{{ c.title }}</h3>
            <div class="course-meta">
              <span>📚 {{ c.chapters }} rozdziałów</span>
              <span>👥 {{ c.students }} uczniów</span>
              <span v-if="c.rating">⭐ {{ c.rating }}</span>
              <span class="updated">Aktualizacja: {{ c.updatedAt }}</span>
            </div>
          </div>

          <div class="course-actions">
            <router-link :to="`/creator/courses/${c.id}/edit`" class="btn-action">✏️ Edytuj</router-link>
            <router-link :to="`/creator/courses/${c.id}/materials`" class="btn-action">📎 Materiały</router-link>
            <router-link :to="`/creator/courses/${c.id}/analytics`" class="btn-action">📊 Analityka</router-link>
            <router-link v-if="c.status === 'DRAFT' || c.status === 'REVIEW'" :to="`/creator/courses/${c.id}/publish`" class="btn-action publish">🚀 Opublikuj</router-link>
            <button class="btn-delete" @click="deleteCourse(c.id)">🗑️</button>
          </div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="empty-state">
        <span>📂</span>
        <p>Brak kursów w tej kategorii</p>
        <router-link to="/creator/courses/new" class="btn-primary">Utwórz pierwszy kurs</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; h1 { font-size: 2rem; font-weight: 800; span { color: #3b82f6; } margin: 0 0 0.3rem; } .subtitle { color: #64748b; margin: 0; } }
.btn-primary { padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(59,130,246,0.3); transition: 0.2s; &:hover { background: #2563eb; } display: inline-block; }

.filter-tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab { padding: 0.5rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.6rem; color: #64748b; cursor: pointer; font-size: 0.82rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(255,255,255,0.07); } &.active { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.25); color: #60a5fa; } }

.courses-list { display: flex; flex-direction: column; gap: 1rem; }
.course-row {
  background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem;
  display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;
  transition: 0.2s; &:hover { border-color: rgba(255,255,255,0.12); }
}
.course-main { flex: 1; }
.status-chip { display: inline-block; padding: 0.22rem 0.65rem; border-radius: 0.4rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
h3 { font-size: 0.98rem; font-weight: 700; margin: 0 0 0.5rem; }
.course-meta { display: flex; gap: 1rem; font-size: 0.78rem; color: #64748b; flex-wrap: wrap; .updated { margin-left: auto; } }
.course-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.btn-action { padding: 0.45rem 0.85rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.55rem; color: #94a3b8; text-decoration: none; font-size: 0.78rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(255,255,255,0.08); color: white; } &.publish { color: #10b981; border-color: rgba(16,185,129,0.25); background: rgba(16,185,129,0.07); &:hover { background: rgba(16,185,129,0.12); } } }
.btn-delete { padding: 0.45rem 0.65rem; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); border-radius: 0.55rem; color: #ef4444; cursor: pointer; font-size: 0.82rem; transition: 0.15s; &:hover { background: rgba(239,68,68,0.15); } }

.empty-state { text-align: center; padding: 4rem; span { font-size: 3rem; display: block; margin-bottom: 1rem; } p { color: #64748b; margin-bottom: 1.5rem; } }
</style>