<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const route = useRoute()

const students = ref([])

const search = ref('')
const filtered = computed(() => students.value.filter(s =>
  !search.value || s.name.toLowerCase().includes(search.value.toLowerCase()) || s.email.includes(search.value)
))

const exportCSV = () => {
  alert('Eksport CSV — funkcja dostępna po połączeniu z backendem.')
}

const progressColor = (p) => p >= 80 ? '#10b981' : p >= 40 ? '#f59e0b' : '#ef4444'

onMounted(async () => {
  try {
    const { data } = await api.get(`/analytics/courses/${route.params.id}/students/`)
    students.value = (data.results ?? data ?? []).map(s => ({
      id: s.user_id,
      name: s.name ?? '—',
      email: s.email ?? '—',
      progress: s.progress_percent ?? 0,
      completedMaterials: s.completed_materials ?? 0,
      totalMaterials: s.total_materials ?? 0,
      quizAvg: null,
      lastActive: '—',
      enrolled: s.enrolled_at?.slice(0, 10) ?? '—',
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${route.params.id}/analytics`" class="back-link">← Analityka kursu</router-link>
        <div class="header-row">
          <h1>Uczniowie <span>({{ students.length }})</span></h1>
          <button class="btn-export" @click="exportCSV">📥 Eksportuj CSV</button>
        </div>
      </div>

      <div class="search-bar">
        <span>🔍</span>
        <input v-model="search" type="text" placeholder="Szukaj po nazwie lub e-mail..." />
      </div>

      <!-- Tabela uczniów -->
      <div class="students-table">
        <div class="table-header">
          <span>Uczeń</span>
          <span>Postęp</span>
          <span>Śr. quiz</span>
          <span>Ostatnia aktywność</span>
          <span>Data zapisu</span>
        </div>
        <div v-for="s in filtered" :key="s.id" class="student-row">
          <div class="student-info">
            <div class="student-avatar">{{ s.name.charAt(0) }}</div>
            <div>
              <strong>{{ s.name }}</strong>
              <small>{{ s.email }}</small>
            </div>
          </div>
          <div class="progress-cell">
            <div class="prog-bar-sm">
              <div class="prog-fill-sm" :style="{ width: s.progress + '%', background: progressColor(s.progress) }"></div>
            </div>
            <span :style="{ color: progressColor(s.progress) }">{{ s.progress }}%</span>
          </div>
          <div class="quiz-cell">
            {{ s.quizAvg !== null ? s.quizAvg + '%' : '—' }}
          </div>
          <div class="activity-cell">{{ s.lastActive }}</div>
          <div class="date-cell">{{ s.enrolled }}</div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="empty">Brak wyników dla "{{ search }}"</div>

      <!-- TODO: Paginacja → GET /api/creator/courses/:id/students/?page=X -->
      <div class="pagination">
        <button class="page-btn" disabled>← Poprzednia</button>
        <span class="page-info">Strona 1 z 1</span>
        <button class="page-btn" disabled>Następna →</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; justify-content: space-between; align-items: center; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.btn-export { padding: 0.65rem 1.25rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 0.7rem; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: 0.2s; &:hover { background: rgba(255,255,255,0.09); } }

.search-bar { display: flex; align-items: center; gap: 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; padding: 0.65rem 1rem; margin-bottom: 1.5rem; span { color: #475569; } input { flex: 1; background: none; border: none; color: white; font-size: 0.88rem; outline: none; &::placeholder { color: #475569; } } }

.students-table { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; overflow: hidden; }
.table-header { display: grid; grid-template-columns: 2fr 1.5fr 1fr 1.5fr 1fr; gap: 1rem; padding: 0.85rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.student-row { display: grid; grid-template-columns: 2fr 1.5fr 1fr 1.5fr 1fr; gap: 1rem; align-items: center; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); transition: 0.15s; &:last-child { border-bottom: none; } &:hover { background: rgba(255,255,255,0.02); } }
.student-info { display: flex; align-items: center; gap: 0.75rem; .student-avatar { width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; flex-shrink: 0; } strong { display: block; font-size: 0.87rem; } small { color: #64748b; font-size: 0.72rem; } }
.progress-cell { display: flex; align-items: center; gap: 0.6rem; .prog-bar-sm { height: 5px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; flex: 1; max-width: 80px; } .prog-fill-sm { height: 100%; border-radius: 3px; } span { font-size: 0.8rem; font-weight: 700; } }
.quiz-cell { font-size: 0.87rem; color: #94a3b8; }
.activity-cell { font-size: 0.82rem; color: #64748b; }
.date-cell { font-size: 0.78rem; color: #475569; }

.empty { text-align: center; padding: 3rem; color: #64748b; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1.5rem; margin-top: 1.5rem; .page-info { color: #64748b; font-size: 0.85rem; } }
.page-btn { padding: 0.55rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.6rem; cursor: pointer; font-size: 0.82rem; font-weight: 600; &:disabled { opacity: 0.4; cursor: not-allowed; } &:hover:not(:disabled) { background: rgba(255,255,255,0.08); } }
</style>