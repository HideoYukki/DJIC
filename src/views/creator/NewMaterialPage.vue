<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()

const selectedType = ref('VIDEO')
const types = [
  { value: 'VIDEO', icon: '▶', label: 'Wideo', desc: 'Plik MP4 lub link YouTube/Vimeo' },
  { value: 'TEXT', icon: '📄', label: 'Tekst', desc: 'Treść w formacie Markdown' },
  { value: 'QUIZ', icon: '❓', label: 'Quiz', desc: 'Zestaw pytań wielokrotnego wyboru' },
]

const form = reactive({
  title: '',
  chapterId: 1,
  videoUrl: '',
  textContent: '',
})

const isSubmitting = ref(false)
const serverError = ref('')

const submit = async () => {
  if (!form.title.trim()) return
  isSubmitting.value = true
  serverError.value = ''
  try {
    const content = selectedType.value === 'VIDEO' ? form.videoUrl : form.textContent
    const { data: mat } = await api.post(`/courses/${route.params.id}/materials/new/`, {
      title:   form.title,
      type:    selectedType.value,
      content: content,
      order:   0,
    })
    if (selectedType.value === 'QUIZ') {
      const { data: quiz } = await api.post(`/courses/${route.params.id}/quizzes/`, {
        title: form.title,
        material_id: mat.id,
      })
      await api.patch(`/courses/${route.params.id}/materials/${mat.id}/`, { content: quiz.id })
      router.push(`/creator/courses/${route.params.id}/quiz/${quiz.id}/builder`)
    } else {
      router.push(`/creator/courses/${route.params.id}/materials`)
    }
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd dodawania materiału.'
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${route.params.id}/materials`" class="back-link">← Materiały kursu</router-link>
        <h1>Dodaj <span>materiał</span></h1>
      </div>

      <!-- Wybór typu -->
      <div class="type-grid">
        <button v-for="t in types" :key="t.value" class="type-card" :class="{ active: selectedType === t.value }" @click="selectedType = t.value">
          <span class="type-icon">{{ t.icon }}</span>
          <strong>{{ t.label }}</strong>
          <small>{{ t.desc }}</small>
        </button>
      </div>

      <div class="form-card">
        <div class="field">
          <label>Tytuł materiału</label>
          <input v-model="form.title" type="text" placeholder="np. Wprowadzenie do reaktywności" />
        </div>

        <!-- Pola specyficzne dla typu -->
        <template v-if="selectedType === 'VIDEO'">
          <div class="field">
            <label>URL wideo lub prześlij plik</label>
            <!-- TODO: Obsługa uploadu pliku wideo → POST /api/creator/upload/video/ (multipart, max 2GB) -->
            <!-- TODO: Alternatywnie: YouTube/Vimeo embed URL -->
            <input v-model="form.videoUrl" type="url" placeholder="https://youtube.com/watch?v=... lub prześlij plik" />
          </div>
          <div class="upload-zone">
            <span>📁</span>
            <p>Lub przeciągnij plik MP4 tutaj (max 2GB)</p>
            <small>Po przesłaniu wideo zostanie zoptymalizowane dla różnych rozdzielczości (720p, 1080p).</small>
          </div>
        </template>

        <template v-if="selectedType === 'TEXT'">
          <div class="field">
            <label>Treść (Markdown)</label>
            <!-- TODO: Zastąp textarea edytorem Markdown (np. vue-easymde lub TipTap) -->
            <textarea v-model="form.textContent" rows="12" placeholder="# Tytuł rozdziału&#10;&#10;Treść materiału w formacie **Markdown**..."></textarea>
            <small class="hint">Obsługuje: nagłówki, pogrubienie, listy, kod, linki, obrazy.</small>
          </div>
        </template>

        <template v-if="selectedType === 'QUIZ'">
          <div class="quiz-redirect-info">
            <span class="qi-icon">❓</span>
            <div>
              <strong>Quiz — Edytor pytań</strong>
              <p>Pytania i odpowiedzi tworzysz w dedykowanym edytorze quizów. Po zapisaniu materiału zostaniesz tam przekierowany.</p>
            </div>
          </div>
        </template>

        <div class="form-footer">
          <button class="btn-cancel" @click="$router.back()">Anuluj</button>
          <button class="btn-submit" :disabled="isSubmitting" @click="submit">
            {{ isSubmitting ? 'Zapisywanie...' : (selectedType === 'QUIZ' ? 'Zapisz i przejdź do edytora quizów →' : 'Zapisz materiał') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 760px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }

.type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1.75rem; }
.type-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 1rem; padding: 1.25rem; cursor: pointer; transition: all 0.15s; text-align: center; .type-icon { font-size: 1.8rem; display: block; margin-bottom: 0.5rem; } strong { display: block; font-size: 0.92rem; color: #f1f5f9; margin-bottom: 0.3rem; } small { font-size: 0.75rem; color: #64748b; } &.active { border-color: #3b82f6; background: rgba(59,130,246,0.1); strong { color: #60a5fa; } } &:hover:not(.active) { border-color: rgba(255,255,255,0.15); } }

.form-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 2rem; }
.field { margin-bottom: 1.25rem; label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; } }
input, textarea { width: 100%; padding: 0.8rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem; color: white; font-size: 0.9rem; box-sizing: border-box; resize: vertical; &::placeholder { color: #475569; } &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); } }
.hint { display: block; color: #475569; font-size: 0.75rem; margin-top: 0.4rem; }

.upload-zone { border: 2px dashed rgba(255,255,255,0.1); border-radius: 0.85rem; padding: 2rem; text-align: center; margin-bottom: 1rem; span { font-size: 2rem; display: block; margin-bottom: 0.5rem; } p { color: #64748b; font-size: 0.87rem; margin-bottom: 0.4rem; } small { color: #475569; font-size: 0.75rem; } }

.quiz-redirect-info { display: flex; gap: 1rem; padding: 1.25rem; background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); border-radius: 0.85rem; margin-bottom: 1rem; .qi-icon { font-size: 1.8rem; flex-shrink: 0; } strong { display: block; color: #f59e0b; margin-bottom: 0.3rem; } p { color: #94a3b8; font-size: 0.85rem; line-height: 1.4; margin: 0; } }

.form-footer { display: flex; justify-content: flex-end; gap: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; margin-top: 0.5rem; }
.btn-cancel { padding: 0.7rem 1.25rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #64748b; border-radius: 0.7rem; cursor: pointer; font-size: 0.88rem; font-weight: 600; }
.btn-submit { padding: 0.7rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.7rem; font-weight: 700; cursor: pointer; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.6; cursor: not-allowed; } }
</style>