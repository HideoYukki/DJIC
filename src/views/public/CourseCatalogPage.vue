<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDbStore } from '@/stores/db'

const router = useRouter()
const db = useDbStore()

const allCourses = computed(() => db.allCourses)

onMounted(() => db.fetchCourses())

const searchQuery = ref('')
const selectedLevel = ref('')
const selectedCategory = ref('')

const categories = ['Frontend', 'Backend', 'Bazy danych', 'DevOps', 'Bezpieczeństwo']
const levels = ['Początkujący', 'Średniozaawansowany', 'Zaawansowany']

const filtered = computed(() => {
  return allCourses.value.filter((c) => {
    const matchSearch = !searchQuery.value || c.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || c.tags.some(t => t.toLowerCase().includes(searchQuery.value.toLowerCase()))
    const matchLevel = !selectedLevel.value || c.level === selectedLevel.value
    const matchCat = !selectedCategory.value || c.category === selectedCategory.value
    return matchSearch && matchLevel && matchCat
  })
})

const clearFilters = () => {
  searchQuery.value = ''
  selectedLevel.value = ''
  selectedCategory.value = ''
}

const goToDetail = (id) => router.push(`/courses/${id}`)

const levelColor = (level) => {
  if (level === 'Początkujący') return '#10b981'
  if (level === 'Średniozaawansowany') return '#f59e0b'
  return '#ef4444'
}
</script>

<template>
  <div class="catalog-page">
    <div class="container">

      <header class="page-header">
        <div>
          <h1>Eksploruj <span>kursy</span></h1>
          <p class="subtitle">{{ allCourses.length }} kursów dostępnych · bez logowania</p>
        </div>
      </header>

      <!-- Filtry -->
      <div class="filters-bar">
        <div class="search-wrap">
          <span class="search-icon">🔍</span>
          <input v-model="searchQuery" type="text" placeholder="Szukaj kursu lub tagu..." />
        </div>
        <select v-model="selectedLevel">
          <option value="">Wszystkie poziomy</option>
          <option v-for="l in levels" :key="l" :value="l">{{ l }}</option>
        </select>
        <select v-model="selectedCategory">
          <option value="">Wszystkie kategorie</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <button v-if="searchQuery || selectedLevel || selectedCategory" @click="clearFilters" class="btn-clear">
          Wyczyść filtry ✕
        </button>
      </div>

      <!-- Wyniki -->
      <p class="results-count">{{ filtered.length }} kursów</p>

      <div v-if="filtered.length > 0" class="course-grid">
        <div
          v-for="course in filtered"
          :key="course.id"
          class="course-card"
          @click="goToDetail(course.id)"
        >
          <!-- TODO: $env(VITE_API_URL)/courses/:id/thumbnail — CDN URL po integracji z backendem -->
          <img :src="course.thumbnail" :alt="course.title" class="course-thumb" loading="lazy" />

          <div class="course-body">
            <div class="course-meta-top">
              <span class="category-tag">{{ course.category }}</span>
              <span class="level-badge" :style="{ color: levelColor(course.level) }">{{ course.level }}</span>
            </div>
            <h3>{{ course.title }}</h3>
            <p class="course-desc">{{ course.description }}</p>
            <div class="course-footer">
              <span class="author">👤 {{ course.author }}</span>
              <span class="stats">📚 {{ course.chaptersCount }} rozdz. · ⭐ {{ course.rating }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <span class="empty-icon">🔍</span>
        <h3>Brak wyników</h3>
        <p>Spróbuj zmienić kryteria wyszukiwania.</p>
        <button @click="clearFilters" class="btn-primary">Pokaż wszystkie kursy</button>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.catalog-page {
  background: #020617;
  min-height: 100vh;
  padding: 100px 20px 60px;
  color: white;
}
.container { max-width: 1200px; margin: 0 auto; }

.page-header {
  margin-bottom: 2.5rem;
  h1 { font-size: 2.5rem; font-weight: 800; margin: 0 0 0.4rem; span { color: #3b82f6; } }
  .subtitle { color: #64748b; font-size: 0.95rem; }
}

.filters-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}
.search-wrap {
  position: relative;
  flex: 1;
  min-width: 200px;
  .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); opacity: 0.5; }
  input {
    width: 100%; padding: 0.75rem 1rem 0.75rem 42px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 0.75rem;
    color: white; outline: none; box-sizing: border-box;
    font-size: 0.9rem;
    &::placeholder { color: #475569; }
    &:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
  }
}
select {
  padding: 0.75rem 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 0.75rem;
  color: #94a3b8;
  outline: none; cursor: pointer;
  font-size: 0.87rem;
  option { background: #0f172a; }
}
.btn-clear {
  padding: 0.6rem 1rem;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.2);
  border-radius: 0.65rem;
  color: #ef4444;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: 0.2s;
  &:hover { background: rgba(239,68,68,0.2); }
}

.results-count { color: #475569; font-size: 0.85rem; margin-bottom: 1.5rem; }

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.course-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 1.25rem;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s;
  &:hover { transform: translateY(-4px); border-color: rgba(59,130,246,0.3); box-shadow: 0 12px 30px rgba(0,0,0,0.4); }
}

.course-thumb {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  background: #1e293b;
}

.course-body { padding: 1.25rem; }

.course-meta-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.category-tag { font-size: 0.7rem; color: #3b82f6; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.level-badge { font-size: 0.7rem; font-weight: 700; }

h3 { font-size: 1.05rem; color: #f1f5f9; font-weight: 700; margin: 0 0 0.5rem; line-height: 1.35; }
.course-desc { color: #64748b; font-size: 0.82rem; line-height: 1.5; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.course-footer {
  display: flex; justify-content: space-between;
  font-size: 0.78rem; color: #475569;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  .empty-icon { font-size: 3rem; display: block; margin-bottom: 1rem; }
  h3 { font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 0.5rem; }
  p { color: #64748b; margin-bottom: 2rem; }
}
.btn-primary {
  padding: 0.75rem 2rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
  &:hover { background: #2563eb; }
}
</style>