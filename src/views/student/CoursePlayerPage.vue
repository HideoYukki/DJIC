<!-- Widok: CoursePlayerPage -->
<!-- Rola: STUDENT -->
<!-- Trasa: /courses/:id/learn -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const db     = useDbStore()

const courseId = route.params.id
const userId   = auth.user?.id

const course   = computed(() => db.getCourseById(courseId))
const chapters = computed(() => db.getCourseChapters(courseId))
const progress = computed(() => db.getCourseProgress(userId, courseId))
const completed = computed(() => db.getCompletedMaterials(userId, courseId))

const allMaterials = computed(() => chapters.value.flatMap(ch => ch.materials))
const activeMaterial = ref(null)
const sidebarOpen    = ref(true)

onMounted(async () => {
  await Promise.all([
    db.fetchCourseDetail(courseId),
    db.fetchMaterials(courseId),
    db.fetchProgress(userId),
  ])
  if (!activeMaterial.value && allMaterials.value.length) {
    activeMaterial.value = allMaterials.value[0]
  }
})

const typeIcon = (t) => ({ VIDEO: '▶', QUIZ: '❓', TEXT: '📄' }[t] || '📄')

function selectMaterial(mat) {
  activeMaterial.value = mat
}

function markDone() {
  db.completeMaterial(userId, courseId, activeMaterial.value.id)
  const idx  = allMaterials.value.findIndex(m => m.id === activeMaterial.value.id)
  if (idx + 1 < allMaterials.value.length) activeMaterial.value = allMaterials.value[idx + 1]
}

function prevMaterial() {
  const idx = allMaterials.value.findIndex(m => m.id === activeMaterial.value?.id)
  if (idx > 0) activeMaterial.value = allMaterials.value[idx - 1]
}

function nextMaterial() {
  const idx = allMaterials.value.findIndex(m => m.id === activeMaterial.value?.id)
  if (idx < allMaterials.value.length - 1) activeMaterial.value = allMaterials.value[idx + 1]
}

const isCompleted = (matId) => completed.value.includes(matId)
const isActive    = (matId) => activeMaterial.value?.id === matId
</script>

<template>
  <div class="player-wrapper">
    <!-- Topbar -->
    <div class="player-topbar">
      <router-link to="/my-courses" class="back-link">← Moje kursy</router-link>
      <span class="course-title-short">{{ course?.title ?? 'Kurs' }}</span>
      <div class="progress-chip">{{ progress }}% ukończono</div>
    </div>

    <div class="player-layout">
      <!-- Sidebar -->
      <aside class="sidebar" :class="{ collapsed: !sidebarOpen }">
        <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen">
          {{ sidebarOpen ? '◀' : '▶' }}
        </button>
        <div v-if="sidebarOpen" class="sidebar-content">
          <div class="sidebar-progress">
            <div class="prog-track"><div class="prog-fill" :style="{ width: progress + '%' }"></div></div>
            <span>{{ completed.length }}/{{ allMaterials.length }} lekcji</span>
          </div>
          <div v-for="ch in chapters" :key="ch.id" class="chapter-group">
            <div class="chapter-heading">{{ ch.title }}</div>
            <button
              v-for="mat in ch.materials" :key="mat.id"
              class="material-btn"
              :class="{ active: isActive(mat.id), done: isCompleted(mat.id) }"
              @click="selectMaterial(mat)"
            >
              <span class="mat-icon">{{ isCompleted(mat.id) ? '✓' : typeIcon(mat.type) }}</span>
              <span class="mat-name">{{ mat.title }}</span>
              <span class="mat-dur">{{ mat.duration }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- Główny obszar -->
      <main class="player-main">
        <div class="material-header">
          <span class="type-badge">{{ activeMaterial?.type }}</span>
          <h1>{{ activeMaterial?.title }}</h1>
          <span class="duration">{{ activeMaterial?.duration }}</span>
        </div>

        <div class="content-area">
          <!-- VIDEO — działający odtwarzacz HTML5 -->
          <template v-if="activeMaterial?.type === 'VIDEO'">
            <div class="video-player-wrap">
              <!-- TODO: zastąpić playerem HLS.js / Plyr gdy backend dostarczy stream -->
              <video
                :key="activeMaterial.id"
                :src="activeMaterial.videoUrl"
                class="video-player"
                controls
                preload="auto"
                :poster="`https://picsum.photos/seed/${activeMaterial.id}/1280/720`"
              ></video>
            </div>
          </template>

          <!-- TEXT — treść HTML z bazy -->
          <template v-else-if="activeMaterial?.type === 'TEXT'">
            <article class="text-content" v-html="activeMaterial.content"></article>
          </template>

          <!-- QUIZ — przycisk start -->
          <template v-else-if="activeMaterial?.type === 'QUIZ'">
            <div class="quiz-card">
              <div class="quiz-icon">❓</div>
              <h2>{{ activeMaterial.title }}</h2>
              <p>Sprawdź swoją wiedzę z przerobionego materiału.</p>
              <router-link
                :to="`/courses/${courseId}/quiz/${activeMaterial.quizId}`"
                class="btn-start-quiz">
                Rozpocznij quiz →
              </router-link>
            </div>
          </template>
        </div>

        <!-- Nawigacja -->
        <div class="material-nav">
          <button class="btn-nav" :disabled="allMaterials[0]?.id === activeMaterial?.id" @click="prevMaterial">← Poprzednia</button>
          <button v-if="!isCompleted(activeMaterial?.id)" class="btn-done" @click="markDone">
            ✓ Oznacz jako ukończone
          </button>
          <span v-else class="done-badge">✅ Ukończono</span>
          <button class="btn-nav" :disabled="allMaterials.at(-1)?.id === activeMaterial?.id" @click="nextMaterial">Następna →</button>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.player-wrapper { background: #020617; min-height: 100vh; display: flex; flex-direction: column; padding-top: 64px; color: white; }

.player-topbar {
  height: 52px; background: #0f172a; border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center; padding: 0 1.5rem; gap: 1.5rem;
  .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; white-space: nowrap; transition: 0.2s; &:hover { color: #94a3b8; } }
  .course-title-short { color: #94a3b8; font-size: 0.88rem; font-weight: 600; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .progress-chip { background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.25); color: #60a5fa; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.78rem; font-weight: 700; white-space: nowrap; }
}

.player-layout { display: flex; flex: 1; height: calc(100vh - 116px); }

.sidebar {
  width: 300px; background: #0f172a; border-right: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0; position: relative; overflow-y: auto; transition: width 0.25s ease;
  &.collapsed { width: 40px; overflow: hidden; }
}
.sidebar-toggle { position: absolute; top: 1rem; right: 0.5rem; background: rgba(255,255,255,0.06); border: none; color: #64748b; width: 28px; height: 28px; border-radius: 6px; cursor: pointer; font-size: 0.7rem; z-index: 1; &:hover { background: rgba(255,255,255,0.1); } }
.sidebar-content { padding: 1rem; }
.sidebar-progress { margin-bottom: 1.25rem; .prog-track { height: 4px; background: rgba(255,255,255,0.07); border-radius: 2px; overflow: hidden; margin-bottom: 0.4rem; } .prog-fill { height: 100%; background: #3b82f6; border-radius: 2px; transition: width 0.4s; } span { font-size: 0.72rem; color: #64748b; } }
.chapter-group { margin-bottom: 1rem; }
.chapter-heading { font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; padding: 0.25rem 0.5rem; margin-bottom: 0.35rem; }
.material-btn { width: 100%; display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.7rem; background: none; border: none; border-radius: 0.6rem; color: #94a3b8; cursor: pointer; font-size: 0.82rem; transition: 0.15s; text-align: left;
  &:hover { background: rgba(255,255,255,0.04); color: #f1f5f9; }
  &.active { background: rgba(59,130,246,0.15); color: #60a5fa; }
  &.done { color: #64748b; .mat-icon { color: #10b981; } }
  .mat-icon { flex-shrink: 0; width: 16px; text-align: center; font-size: 0.8rem; }
  .mat-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .mat-dur { font-size: 0.7rem; color: #475569; white-space: nowrap; }
}

.player-main { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }
.material-header { padding: 1.25rem 2rem 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.06); .type-badge { font-size: 0.68rem; color: #3b82f6; font-weight: 800; text-transform: uppercase; display: block; margin-bottom: 0.35rem; } h1 { font-size: 1.3rem; font-weight: 700; margin: 0 0 0.3rem; } .duration { font-size: 0.78rem; color: #64748b; } }

.content-area { flex: 1; padding: 1.5rem 2rem; overflow-y: auto; }

.video-player-wrap { width: 100%; max-width: 960px; }
.video-player { width: 100%; aspect-ratio: 16/9; border-radius: 1rem; background: #000; display: block; outline: none; }

.text-content {
  max-width: 760px; color: #cbd5e1; line-height: 1.75; font-size: 0.95rem;
  h2 { font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin: 0 0 1rem; }
  h3 { font-size: 1.05rem; font-weight: 700; color: #e2e8f0; margin: 1.75rem 0 0.65rem; }
  p { margin: 0 0 1rem; }
  ul, ol { padding-left: 1.5rem; margin: 0 0 1rem; li { margin-bottom: 0.4rem; } }
  strong { color: #f1f5f9; }
  em { color: #60a5fa; font-style: normal; }
  code { background: rgba(59,130,246,0.12); color: #93c5fd; padding: 0.15em 0.45em; border-radius: 0.35rem; font-family: 'JetBrains Mono', monospace; font-size: 0.88em; }
  pre { background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem; overflow-x: auto; margin: 1rem 0 1.25rem; code { background: none; padding: 0; color: #93c5fd; } }
  table { width: 100%; border-collapse: collapse; margin: 1rem 0 1.25rem; th, td { padding: 0.65rem 1rem; border: 1px solid rgba(255,255,255,0.08); text-align: left; } th { background: rgba(59,130,246,0.1); color: #60a5fa; font-size: 0.82rem; text-transform: uppercase; } tr:nth-child(even) { background: rgba(255,255,255,0.02); } }
}

.quiz-card { max-width: 600px; text-align: center; background: rgba(15,23,42,0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 3rem; margin: 0 auto; .quiz-icon { font-size: 3.5rem; margin-bottom: 1rem; } h2 { font-size: 1.3rem; font-weight: 700; margin: 0 0 0.75rem; } p { color: #64748b; font-size: 0.9rem; margin-bottom: 1.75rem; } }
.btn-start-quiz { display: inline-block; padding: 0.75rem 2rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; font-size: 0.95rem; transition: 0.2s; &:hover { background: #2563eb; } }

.material-nav { padding: 1rem 2rem; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-shrink: 0; }
.btn-nav { padding: 0.6rem 1.2rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.65rem; color: #94a3b8; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: 0.2s; &:hover:not(:disabled) { background: rgba(255,255,255,0.09); color: white; } &:disabled { opacity: 0.3; cursor: not-allowed; } }
.btn-done { padding: 0.6rem 1.5rem; background: #10b981; border: none; border-radius: 0.65rem; color: white; cursor: pointer; font-size: 0.88rem; font-weight: 700; transition: 0.2s; &:hover { background: #059669; } }
.done-badge { color: #10b981; font-size: 0.88rem; font-weight: 700; }
</style>
