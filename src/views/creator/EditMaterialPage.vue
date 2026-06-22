<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route    = useRoute()
const router   = useRouter()
const courseId   = route.params.id
const materialId = route.params.materialId

const loading      = ref(true)
const isSubmitting = ref(false)
const serverError  = ref('')
const uploadError  = ref('')
const uploading    = ref(false)
const uploadPct    = ref(0)

const form = reactive({
  title:       '',
  type:        'VIDEO',
  videoUrl:    '',
  textContent: '',
  quizId:      '',
  duration:    0,
})

const typeIcon  = (t) => ({ VIDEO: '▶', QUIZ: '❓', TEXT: '📄' }[t] || '📄')
const typeColor = (t) => ({ VIDEO: '#3b82f6', QUIZ: '#f59e0b', TEXT: '#10b981' }[t] || '#64748b')

const isHostedVideo = computed(() =>
  form.videoUrl && (
    form.videoUrl.includes('localhost') ||
    form.videoUrl.includes('/media/videos/')
  )
)

onMounted(async () => {
  try {
    const { data } = await api.get(`/courses/${courseId}/materials/${materialId}/`)
    form.title    = data.title   ?? ''
    form.type     = data.type    ?? 'VIDEO'
    form.duration = data.duration_seconds ?? 0
    if (data.type === 'VIDEO') form.videoUrl    = data.content ?? ''
    if (data.type === 'TEXT')  form.textContent = data.content ?? ''
    if (data.type === 'QUIZ')  form.quizId      = data.content ?? ''
  } catch (_) {
    serverError.value = 'Nie udało się wczytać materiału.'
  } finally {
    loading.value = false
  }
})

async function onVideoFileSelected(event) {
  const file = event.target.files[0]
  if (!file) return
  uploadError.value = ''

  const ext  = file.name.split('.').pop().toLowerCase()
  const allowed = ['mp4', 'webm']
  if (!allowed.includes(ext) && !['video/mp4', 'video/webm'].includes(file.type)) {
    uploadError.value = 'Dozwolone formaty: MP4, WebM. Inne mogą nie działać w Firefox.'
    return
  }

  uploading.value = true
  uploadPct.value = 0
  try {
    const fd = new FormData()
    fd.append('video', file)
    const { data } = await api.post(
      `/courses/${courseId}/materials/upload-video/`,
      fd,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) uploadPct.value = Math.round((e.loaded / e.total) * 100)
        },
      }
    )
    form.videoUrl = data.url
    // Auto-detect duration from the file (approximate from size — backend can't do it without ffprobe)
    if (!form.duration) form.duration = Math.round(file.size / (500 * 1024))
  } catch (err) {
    uploadError.value = err.response?.data?.error ?? 'Błąd przesyłania pliku.'
  } finally {
    uploading.value = false
  }
}

async function submit() {
  if (!form.title.trim()) return
  isSubmitting.value = true
  serverError.value  = ''
  try {
    const content = form.type === 'VIDEO' ? form.videoUrl
                  : form.type === 'TEXT'  ? form.textContent
                  : form.quizId
    await api.patch(`/courses/${courseId}/materials/${materialId}/`, {
      title:            form.title,
      content:          content,
      duration_seconds: form.duration,
    })
    router.push(`/creator/courses/${courseId}/materials`)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania materiału.'
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${courseId}/materials`" class="back-link">← Materiały kursu</router-link>
        <h1>Edytuj <span>materiał</span></h1>
      </div>

      <div v-if="loading" class="loading-state">Wczytywanie…</div>

      <div v-else-if="serverError && loading" class="error-state">{{ serverError }}</div>

      <div v-else class="form-card">
        <!-- Typ materiału (tylko info, nie można zmienić) -->
        <div class="type-badge-row">
          <span class="type-badge" :style="{ color: typeColor(form.type) }">
            {{ typeIcon(form.type) }} {{ form.type }}
          </span>
          <span class="type-hint">Typ materiału nie może zostać zmieniony po utworzeniu.</span>
        </div>

        <div class="field">
          <label>Tytuł materiału</label>
          <input v-model="form.title" type="text" placeholder="np. Wprowadzenie do reaktywności" />
        </div>

        <!-- VIDEO -->
        <template v-if="form.type === 'VIDEO'">
          <div class="field">
            <label>Aktualny URL wideo</label>
            <input v-model="form.videoUrl" type="url" placeholder="https://... lub prześlij nowy plik poniżej" />
            <small class="hint" v-if="isHostedVideo">
              ✅ Plik hostowany lokalnie ({{ form.videoUrl.split('/').pop() }})
            </small>
          </div>

          <div class="upload-section">
            <p class="upload-label">Zastąp wideo nowym plikiem (MP4 lub WebM):</p>
            <p class="upload-hint">Firefox obsługuje MP4 (H.264) i WebM (VP8/VP9). Nie używaj innych formatów.</p>

            <label class="upload-zone" :class="{ uploading }">
              <input
                type="file"
                accept="video/mp4,video/webm,.mp4,.webm"
                style="display:none"
                @change="onVideoFileSelected"
                :disabled="uploading"
              />
              <template v-if="!uploading">
                <span class="upload-icon">📁</span>
                <p>Kliknij lub przeciągnij plik MP4 / WebM</p>
                <small>Maks. 500 MB</small>
              </template>
              <template v-else>
                <span class="upload-icon spin">⏳</span>
                <p>Przesyłanie… {{ uploadPct }}%</p>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: uploadPct + '%' }"></div>
                </div>
              </template>
            </label>
            <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>
          </div>

          <div class="field">
            <label>Czas trwania (sekundy)</label>
            <input v-model.number="form.duration" type="number" min="0" placeholder="np. 300" />
          </div>
        </template>

        <!-- TEXT -->
        <template v-if="form.type === 'TEXT'">
          <div class="field">
            <label>Treść (Markdown / HTML)</label>
            <textarea v-model="form.textContent" rows="16" placeholder="# Tytuł&#10;&#10;Treść materiału..."></textarea>
            <small class="hint">Obsługiwany Markdown: nagłówki, pogrubienie, listy, kod, linki.</small>
          </div>
        </template>

        <!-- QUIZ -->
        <template v-if="form.type === 'QUIZ'">
          <div class="quiz-info">
            <span class="qi-icon">❓</span>
            <div>
              <strong>Quiz</strong>
              <p>Pytania i odpowiedzi edytujesz w edytorze quizów.</p>
              <router-link :to="`/creator/courses/${courseId}/quiz/${form.quizId ?? ''}/builder`" class="btn-quiz-link">
                Przejdź do edytora quizów →
              </router-link>
            </div>
          </div>
        </template>

        <p v-if="serverError" class="server-error">{{ serverError }}</p>

        <div class="form-footer">
          <button class="btn-cancel" @click="$router.back()">Anuluj</button>
          <button class="btn-submit" :disabled="isSubmitting || uploading" @click="submit">
            {{ isSubmitting ? 'Zapisywanie…' : 'Zapisz zmiany' }}
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

.loading-state, .error-state { text-align: center; padding: 4rem; color: #64748b; }
.error-state { color: #ef4444; }

.form-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 2rem; }

.type-badge-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.type-badge { font-size: 0.85rem; font-weight: 800; }
.type-hint { color: #475569; font-size: 0.78rem; }

.field { margin-bottom: 1.25rem; label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; } }
input[type="text"], input[type="url"], input[type="number"], textarea {
  width: 100%; padding: 0.8rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem; color: white; font-size: 0.9rem; box-sizing: border-box; resize: vertical;
  &::placeholder { color: #475569; }
  &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
}
.hint { display: block; color: #475569; font-size: 0.75rem; margin-top: 0.4rem; }

.upload-section { margin-bottom: 1.25rem; }
.upload-label { font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin: 0 0 0.3rem; }
.upload-hint { font-size: 0.75rem; color: #475569; margin: 0 0 0.75rem; }

.upload-zone {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  border: 2px dashed rgba(255,255,255,0.12); border-radius: 0.85rem; padding: 1.75rem; text-align: center; cursor: pointer; transition: 0.2s;
  &:hover:not(.uploading) { border-color: #3b82f6; background: rgba(59,130,246,0.04); }
  &.uploading { cursor: not-allowed; opacity: 0.8; }
  .upload-icon { font-size: 1.8rem; display: block; }
  p { color: #64748b; font-size: 0.87rem; margin: 0; }
  small { color: #475569; font-size: 0.75rem; }
}
.spin { animation: spin 1.5s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.progress-bar { width: 100%; height: 4px; background: rgba(255,255,255,0.07); border-radius: 2px; overflow: hidden; margin-top: 0.5rem; }
.progress-fill { height: 100%; background: #3b82f6; border-radius: 2px; transition: width 0.2s; }

.upload-error { color: #ef4444; font-size: 0.78rem; margin-top: 0.5rem; }
.server-error { color: #ef4444; font-size: 0.82rem; margin-top: 0.5rem; }

.quiz-info { display: flex; gap: 1rem; padding: 1.25rem; background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); border-radius: 0.85rem; margin-bottom: 1rem; .qi-icon { font-size: 1.8rem; flex-shrink: 0; } strong { display: block; color: #f59e0b; margin-bottom: 0.3rem; } p { color: #94a3b8; font-size: 0.85rem; line-height: 1.4; margin: 0 0 0.75rem; } }
.btn-quiz-link { display: inline-block; padding: 0.5rem 1rem; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); color: #f59e0b; border-radius: 0.55rem; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: 0.2s; &:hover { background: rgba(245,158,11,0.25); } }

.form-footer { display: flex; justify-content: flex-end; gap: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; margin-top: 1.5rem; }
.btn-cancel { padding: 0.7rem 1.25rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #64748b; border-radius: 0.7rem; cursor: pointer; font-size: 0.88rem; font-weight: 600; }
.btn-submit { padding: 0.7rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.7rem; font-weight: 700; cursor: pointer; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.6; cursor: not-allowed; } }
</style>
