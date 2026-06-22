<!-- Widok: LessonPage -->
<!-- Rola: STUDENT -->
<!-- Trasa: /courses/:id/learn/:materialId -->
<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const db     = useDbStore()

const courseId   = route.params.id
const materialId = route.params.materialId
const userId     = auth.user?.id

const material = computed(() => db.getMaterialById(courseId, materialId))
const allMats  = computed(() => db.getCourseMaterials(courseId))
const idx      = computed(() => allMats.value.findIndex(m => m.id === materialId))
const prev     = computed(() => allMats.value[idx.value - 1] ?? null)
const next     = computed(() => allMats.value[idx.value + 1] ?? null)
const isDone   = computed(() => db.isMaterialCompleted(userId, materialId))

onMounted(async () => {
  await Promise.all([
    db.fetchMaterials(courseId),
    db.fetchProgress(userId),
  ])
})

function markDone() {
  db.completeMaterial(userId, courseId, materialId)
}

function goTo(mat) {
  if (mat) router.push(`/courses/${courseId}/learn/${mat.id}`)
}
</script>

<template>
  <div class="lesson-wrapper">
    <div class="lesson-topbar">
      <router-link :to="`/courses/${courseId}/learn`" class="back-link">← Wróć do kursu</router-link>
      <span class="lesson-title">{{ material?.title }}</span>
      <span class="lesson-meta" v-if="material">{{ material.type }} · {{ material.duration }}</span>
    </div>

    <div class="lesson-body" v-if="material">

      <!-- VIDEO -->
      <template v-if="material.type === 'VIDEO'">
        <div class="video-wrap">
          <!-- TODO: zastąpić playerem HLS.js / Plyr gdy backend dostarczy stream -->
          <video
            :key="material.id"
            :src="material.videoUrl"
            class="video-player"
            controls
            preload="auto"
            :poster="`https://picsum.photos/seed/${material.id}/1280/720`"
          ></video>
          <h2>{{ material.title }}</h2>
        </div>
      </template>

      <!-- TEXT -->
      <template v-else-if="material.type === 'TEXT'">
        <article class="text-content" v-html="material.content"></article>
      </template>

      <!-- QUIZ -->
      <template v-else-if="material.type === 'QUIZ'">
        <div class="quiz-card">
          <div class="quiz-icon">❓</div>
          <h2>{{ material.title }}</h2>
          <p>Sprawdź swoją wiedzę — quiz składa się z kilku pytań z limitem czasu.</p>
          <router-link :to="`/courses/${courseId}/quiz/${material.quizId}`" class="btn-quiz">
            Rozpocznij quiz →
          </router-link>
        </div>
      </template>

      <!-- Brak materiału -->
      <template v-else>
        <div class="not-found">Materiał nie istnieje lub nie jest dostępny.</div>
      </template>

    </div>

    <div class="lesson-footer">
      <button class="btn-nav" :disabled="!prev" @click="goTo(prev)">← Poprzedni</button>
      <button v-if="!isDone" class="btn-done" @click="markDone">✓ Oznacz jako ukończone</button>
      <span v-else class="done-label">✅ Ukończono</span>
      <button class="btn-nav" :disabled="!next" @click="goTo(next)">Następny →</button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.lesson-wrapper { background: #020617; min-height: 100vh; display: flex; flex-direction: column; padding-top: 64px; color: white; }
.lesson-topbar { height: 52px; background: #0f172a; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; padding: 0 2rem; gap: 1.5rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; white-space: nowrap; } .lesson-title { color: #94a3b8; font-size: 0.88rem; font-weight: 600; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } .lesson-meta { color: #475569; font-size: 0.78rem; white-space: nowrap; } }

.lesson-body { flex: 1; padding: 2rem; overflow-y: auto; }

.video-wrap { max-width: 960px; margin: 0 auto; }
.video-player { width: 100%; aspect-ratio: 16/9; border-radius: 1rem; background: #000; display: block; }
.video-wrap h2 { font-size: 1.3rem; font-weight: 700; margin: 1.25rem 0 0; }

.text-content {
  max-width: 760px; margin: 0 auto; color: #cbd5e1; line-height: 1.75; font-size: 0.95rem;
  h2 { font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin: 0 0 1rem; }
  h3 { font-size: 1.05rem; font-weight: 700; color: #e2e8f0; margin: 1.75rem 0 0.65rem; }
  p { margin: 0 0 1rem; }
  ul, ol { padding-left: 1.5rem; margin: 0 0 1rem; li { margin-bottom: 0.4rem; } }
  strong { color: #f1f5f9; }
  code { background: rgba(59,130,246,0.12); color: #93c5fd; padding: 0.15em 0.45em; border-radius: 0.35rem; font-family: monospace; font-size: 0.88em; }
  pre { background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem; overflow-x: auto; margin: 1rem 0 1.25rem; code { background: none; padding: 0; } }
  table { width: 100%; border-collapse: collapse; margin: 1rem 0 1.25rem; th, td { padding: 0.65rem 1rem; border: 1px solid rgba(255,255,255,0.08); text-align: left; } th { background: rgba(59,130,246,0.1); color: #60a5fa; font-size: 0.82rem; text-transform: uppercase; } tr:nth-child(even) { background: rgba(255,255,255,0.02); } }
}

.quiz-card { max-width: 560px; margin: 4rem auto; text-align: center; background: rgba(15,23,42,0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 3rem; .quiz-icon { font-size: 3rem; margin-bottom: 1rem; } h2 { font-size: 1.3rem; font-weight: 700; margin: 0 0 0.75rem; } p { color: #64748b; font-size: 0.9rem; margin-bottom: 1.75rem; } }
.btn-quiz { display: inline-block; padding: 0.75rem 2rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; font-size: 0.95rem; transition: 0.2s; &:hover { background: #2563eb; } }

.not-found { text-align: center; padding: 4rem; color: #64748b; }

.lesson-footer { padding: 1rem 2rem; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; }
.btn-nav { padding: 0.6rem 1.25rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.65rem; color: #94a3b8; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: 0.2s; &:hover:not(:disabled) { background: rgba(255,255,255,0.09); color: white; } &:disabled { opacity: 0.3; cursor: not-allowed; } }
.btn-done { padding: 0.6rem 1.5rem; background: #10b981; border: none; border-radius: 0.65rem; color: white; cursor: pointer; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover { background: #059669; } }
.done-label { color: #10b981; font-weight: 700; font-size: 0.88rem; }
</style>
