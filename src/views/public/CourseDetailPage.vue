<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const route = useRoute()
const auth  = useAuthStore()
const db    = useDbStore()

const userId = computed(() => auth.user?.id ?? null)

const course   = computed(() => db.getCourseById(route.params.id) ?? db.allCourses[0])
const chapters = computed(() => db.getCourseChapters(course.value?.id))
const enrolled = computed(() => userId.value ? db.isEnrolled(userId.value, course.value?.id) : false)

const expandedChapter = ref(null)
const enrolling = ref(false)

onMounted(async () => {
  const cid = route.params.id
  await db.fetchCourseDetail(cid)
  await db.fetchMaterials(cid)
  if (userId.value) await db.fetchEnrollments(userId.value)
})

const toggleChapter = (id) => { expandedChapter.value = expandedChapter.value === id ? null : id }

const totalMaterials = computed(() => chapters.value.reduce((s, ch) => s + ch.materials.length, 0))
const materialIcon   = (type) => ({ VIDEO: '▶', QUIZ: '❓', TEXT: '📄' }[type] || '📄')

async function enroll() {
  if (!auth.isLoggedIn) { return }
  enrolling.value = true
  await db.enroll(userId.value, course.value.id)
  enrolling.value = false
}
</script>

<template>
  <div class="detail-page">
    <div class="container">

      <!-- Breadcrumb -->
      <nav class="breadcrumb">
        <router-link to="/courses">Katalog</router-link>
        <span>›</span>
        <span>{{ course.category }}</span>
        <span>›</span>
        <span class="current">{{ course.title }}</span>
      </nav>

      <div class="layout">

        <!-- Główna treść -->
        <div class="main-content">
          <div class="course-header">
            <div class="tags-row">
              <span class="category-tag">{{ course.category }}</span>
              <span v-for="tag in course.tags" :key="tag" class="tag-pill">#{{ tag }}</span>
            </div>
            <h1>{{ course.title }}</h1>
            <div class="meta-row">
              <span class="rating">⭐ {{ course.rating }} ({{ course.ratingsCount }} ocen)</span>
              <span class="students">👥 {{ course.studentsCount }} uczniów</span>
              <span class="level">📊 {{ course.level }}</span>
            </div>
            <p class="author-line">Autor: <strong>{{ course.author }}</strong> · {{ course.authorBio }}</p>
          </div>

          <div class="description-card">
            <h2>O kursie</h2>
            <p>{{ course.description }}</p>
          </div>

          <!-- Program kursu -->
          <div class="curriculum-card">
            <div class="curriculum-header">
              <h2>Program kursu</h2>
              <span class="curriculum-meta">{{ chapters.length }} rozdziałów · {{ totalMaterials }} materiałów</span>
            </div>

            <div class="chapters-list">
              <div v-for="chapter in chapters" :key="chapter.id" class="chapter-item">
                <button class="chapter-toggle" @click="toggleChapter(chapter.id)">
                  <span class="chapter-icon">{{ expandedChapter === chapter.id ? '▾' : '▸' }}</span>
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <span class="chapter-count">{{ chapter.materials.length }} mat.</span>
                </button>
                <transition name="expand">
                  <div v-if="expandedChapter === chapter.id" class="materials-list">
                    <div v-for="mat in chapter.materials" :key="mat.title" class="material-row">
                      <span class="mat-icon">{{ materialIcon(mat.type) }}</span>
                      <span class="mat-title">{{ mat.title }}</span>
                      <span class="mat-type">{{ mat.type }}</span>
                      <span class="mat-duration">{{ mat.duration }}</span>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar: CTA -->
        <aside class="sidebar">
          <div class="cta-card">
            <!-- TODO: $env(VITE_API_URL)/courses/:id/thumbnail — CDN URL po integracji -->
            <img :src="course.thumbnail" :alt="course.title" class="course-preview-thumb" />

            <div class="price-section">
              <span class="price-label">Dostęp do kursu</span>
              <span class="price-free">BEZPŁATNY</span>
            </div>

            <template v-if="enrolled">
              <router-link :to="`/courses/${course.id}/learn`" class="btn-enroll btn-continue">
                ▶ Kontynuuj naukę
              </router-link>
            </template>
            <template v-else-if="auth.isLoggedIn">
              <button class="btn-enroll" :disabled="enrolling" @click="enroll">
                {{ enrolling ? 'Zapisywanie…' : 'Zapisz się i zacznij →' }}
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="btn-enroll">Zaloguj się, by rozpocząć →</router-link>
            </template>

            <ul class="cta-benefits">
              <li>✓ Nielimitowany dostęp</li>
              <li>✓ {{ totalMaterials }} materiałów dydaktycznych</li>
              <li>✓ Certyfikat ukończenia</li>
              <li>✓ Dostęp do quizów</li>
            </ul>
          </div>
        </aside>

      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.detail-page {
  background: #020617;
  min-height: 100vh;
  padding: 90px 20px 60px;
  color: white;
}
.container { max-width: 1200px; margin: 0 auto; }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  font-size: 0.83rem;
  color: #64748b;
  a { color: #3b82f6; text-decoration: none; &:hover { text-decoration: underline; } }
  .current { color: #94a3b8; }
}

.layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 2rem;
  align-items: start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    .sidebar { order: -1; }
  }
}

/* Nagłówek kursu */
.course-header {
  margin-bottom: 2rem;
  .tags-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .category-tag { font-size: 0.72rem; color: #3b82f6; font-weight: 700; text-transform: uppercase; background: rgba(59,130,246,0.1); padding: 0.2rem 0.6rem; border-radius: 0.4rem; }
  .tag-pill { font-size: 0.72rem; color: #64748b; }
  h1 { font-size: 2rem; font-weight: 800; line-height: 1.25; margin: 0 0 0.75rem; }
  .meta-row { display: flex; gap: 1.25rem; flex-wrap: wrap; margin-bottom: 0.75rem; font-size: 0.88rem; color: #94a3b8; }
  .rating { color: #f59e0b; }
  .author-line { color: #64748b; font-size: 0.87rem; strong { color: #94a3b8; } }
}

.description-card, .curriculum-card {
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 1.25rem;
  padding: 1.75rem;
  margin-bottom: 1.5rem;
  h2 { font-size: 1.2rem; font-weight: 700; margin: 0 0 1rem; }
  p { color: #94a3b8; line-height: 1.7; font-size: 0.93rem; }
}

.curriculum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  .curriculum-meta { color: #64748b; font-size: 0.82rem; }
}

.chapters-list { display: flex; flex-direction: column; gap: 0.5rem; }
.chapter-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 0.75rem;
  overflow: hidden;
}
.chapter-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  background: none;
  border: none;
  color: #f1f5f9;
  cursor: pointer;
  text-align: left;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.15s;
  &:hover { background: rgba(255,255,255,0.03); }
  .chapter-icon { color: #3b82f6; flex-shrink: 0; }
  .chapter-title { flex: 1; }
  .chapter-count { color: #64748b; font-size: 0.78rem; font-weight: 500; white-space: nowrap; }
}
.materials-list { border-top: 1px solid rgba(255,255,255,0.06); }
.material-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1rem;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  &:last-child { border-bottom: none; }
  .mat-icon { color: #3b82f6; flex-shrink: 0; width: 20px; text-align: center; }
  .mat-title { flex: 1; color: #cbd5e1; }
  .mat-type { font-size: 0.72rem; color: #475569; background: rgba(255,255,255,0.05); padding: 0.15rem 0.5rem; border-radius: 0.3rem; }
  .mat-duration { font-size: 0.78rem; color: #64748b; white-space: nowrap; }
}

/* Sidebar CTA */
.cta-card {
  background: #0f172a;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 1.25rem;
  overflow: hidden;
  position: sticky;
  top: 90px;
}
.course-preview-thumb {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: #1e293b;
}
.price-section {
  padding: 1.25rem 1.5rem 0;
  .price-label { display: block; font-size: 0.78rem; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem; }
  .price-free { display: block; font-size: 1.5rem; font-weight: 900; color: #10b981; }
}
.btn-enroll {
  display: block;
  margin: 1rem 1.5rem;
  padding: 0.9rem;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  text-align: center;
  border-radius: 0.85rem;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.2s;
  &:hover { background: #2563eb; transform: translateY(-1px); }
}
.cta-benefits {
  list-style: none;
  margin: 0;
  padding: 0 1.5rem 1.5rem;
  li { font-size: 0.85rem; color: #94a3b8; padding: 0.3rem 0; }
}

.expand-enter-active, .expand-leave-active { transition: all 0.2s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; }
</style>