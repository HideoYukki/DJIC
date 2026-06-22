<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const courses = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/admin/courses/')
    courses.value = (data.results ?? []).map(c => ({
      id: c.id,
      title: c.title,
      creator: c.creator_name ?? '—',
      status: c.status,
      students: c.students_count ?? 0,
      created: c.created_at?.slice(0, 10) ?? '—',
    }))
  } catch (_) {}
})

const search = ref('')
const statusFilter = ref('ALL')

const filtered = computed(() => courses.value.filter(c => {
  const matchSearch = !search.value || c.title.toLowerCase().includes(search.value.toLowerCase()) || c.creator.toLowerCase().includes(search.value.toLowerCase())
  const matchStatus = statusFilter.value === 'ALL' || c.status === statusFilter.value
  return matchSearch && matchStatus
}))

const statusMeta = {
  DRAFT:    { label: 'Szkic',    color: '#64748b' },
  REVIEW:   { label: 'Recenzja', color: '#f59e0b' },
  ACTIVE:   { label: 'Aktywny',  color: '#10b981' },
  ARCHIVED: { label: 'Archiwum', color: '#475569' },
}
const sm = (s) => statusMeta[s] || { label: s, color: '#64748b' }

const reviewCount = computed(() => courses.value.filter(c => c.status === 'REVIEW').length)
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/dashboard" class="back-link">← Panel admina</router-link>
        <div class="header-row">
          <h1>Kursy <span>({{ courses.length }})</span></h1>
          <div v-if="reviewCount > 0" class="review-alert">
            ⏳ {{ reviewCount }} kurs{{ reviewCount > 1 ? 'y' : '' }} czeka{{ reviewCount === 1 ? '' : 'ją' }} na recenzję
          </div>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-bar">
          <span>🔍</span>
          <input v-model="search" type="text" placeholder="Szukaj kursu lub twórcy…" />
        </div>
        <div class="status-tabs">
          <button v-for="s in ['ALL', 'DRAFT', 'REVIEW', 'ACTIVE', 'ARCHIVED']" :key="s"
            class="status-tab" :class="{ active: statusFilter === s }"
            @click="statusFilter = s">
            {{ s === 'ALL' ? 'Wszystkie' : statusMeta[s]?.label || s }}
          </button>
        </div>
      </div>

      <div class="courses-table">
        <div class="table-header">
          <span>Kurs</span>
          <span>Twórca</span>
          <span>Status</span>
          <span>Uczniowie</span>
          <span>Utworzono</span>
          <span>Akcje</span>
        </div>
        <div v-for="c in filtered" :key="c.id" class="course-row">
          <div class="course-title-cell">
            <div class="course-icon">📚</div>
            <span>{{ c.title }}</span>
          </div>
          <div class="creator-cell">{{ c.creator }}</div>
          <div>
            <span class="status-chip" :style="{ color: sm(c.status).color, background: sm(c.status).color + '1a' }">
              {{ sm(c.status).label }}
            </span>
          </div>
          <div class="num-cell">{{ c.students }}</div>
          <div class="date-cell">{{ c.created }}</div>
          <div class="actions-cell">
            <router-link v-if="c.status === 'REVIEW'" :to="`/admin/courses/${c.id}/review`" class="action-btn primary">
              Recenzuj
            </router-link>
            <router-link v-else :to="`/admin/courses/${c.id}/review`" class="action-btn">
              Podgląd
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="empty">Brak kursów pasujących do kryteriów</div>

      <!-- TODO: Paginacja -->
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
.container { max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.review-alert { padding: 0.4rem 1rem; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #fbbf24; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }

.toolbar { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; }
.search-bar { display: flex; align-items: center; gap: 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; padding: 0.65rem 1rem; flex: 1; min-width: 200px; span { color: #475569; } input { flex: 1; background: none; border: none; color: white; font-size: 0.88rem; outline: none; &::placeholder { color: #475569; } } }
.status-tabs { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.status-tab { padding: 0.45rem 0.85rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #64748b; border-radius: 0.6rem; cursor: pointer; font-size: 0.78rem; font-weight: 600; transition: 0.15s; &.active { background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.3); color: #60a5fa; } }

.courses-table { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; overflow: hidden; }
.table-header { display: grid; grid-template-columns: 3fr 1.5fr 1fr 0.8fr 1fr 1fr; gap: 0.75rem; padding: 0.85rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.course-row { display: grid; grid-template-columns: 3fr 1.5fr 1fr 0.8fr 1fr 1fr; gap: 0.75rem; align-items: center; padding: 0.9rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); transition: 0.15s; &:last-child { border-bottom: none; } &:hover { background: rgba(255,255,255,0.02); } }
.course-title-cell { display: flex; align-items: center; gap: 0.65rem; .course-icon { width: 32px; height: 32px; background: rgba(59,130,246,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; } span { font-size: 0.87rem; font-weight: 600; } }
.creator-cell { font-size: 0.82rem; color: #94a3b8; }
.status-chip { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 0.5rem; font-size: 0.7rem; font-weight: 800; }
.num-cell, .date-cell { font-size: 0.82rem; color: #64748b; }
.actions-cell { display: flex; gap: 0.4rem; }
.action-btn { padding: 0.35rem 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.5rem; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: 0.15s; white-space: nowrap; &:hover { background: rgba(59,130,246,0.1); color: #60a5fa; } &.primary { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.25); color: #fbbf24; &:hover { background: rgba(245,158,11,0.18); } } }

.empty { text-align: center; padding: 3rem; color: #64748b; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1.5rem; margin-top: 1.5rem; .page-info { color: #64748b; font-size: 0.85rem; } }
.page-btn { padding: 0.55rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.6rem; cursor: pointer; font-size: 0.82rem; font-weight: 600; &:disabled { opacity: 0.4; cursor: not-allowed; } }
</style>