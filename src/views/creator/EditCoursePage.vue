<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()

const isSaving = ref(false)
const saved = ref(false)
const serverError = ref('')

const form = reactive({
  title: '',
  description: '',
  category: '',
  level: 'Początkujący',
  tags: '',
})

const thumbFile        = ref(null)
const thumbPreview     = ref(null)
const thumbInput       = ref(null)
const thumbError       = ref('')
const uploadingThumb   = ref(false)
const thumbSaved       = ref(false)

const onThumbSelected = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    thumbError.value = 'Dozwolone formaty: JPG, PNG, WebP.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    thumbError.value = 'Maksymalny rozmiar pliku to 5 MB.'
    return
  }
  thumbError.value = ''
  thumbPreview.value = URL.createObjectURL(file)
  uploadingThumb.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post(`/courses/${route.params.id}/thumbnail/`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    thumbPreview.value = data.thumbnail_url
    thumbSaved.value = true
    setTimeout(() => (thumbSaved.value = false), 3000)
  } catch (err) {
    thumbError.value = err.response?.data?.error ?? 'Błąd uploadu okładki.'
  } finally {
    uploadingThumb.value = false
    e.target.value = ''
  }
}

const categories = ['Frontend', 'Backend', 'Bazy danych', 'DevOps', 'Mobile', 'Bezpieczeństwo', 'UI/UX', 'Data Science']
const levels = ['Początkujący', 'Średniozaawansowany', 'Zaawansowany']

const levelLabel = (l) => ({ BEGINNER: 'Początkujący', INTERMEDIATE: 'Średniozaawansowany', ADVANCED: 'Zaawansowany' }[l] ?? l ?? 'Początkujący')
const levelKey   = (l) => ({ 'Początkujący': 'BEGINNER', 'Średniozaawansowany': 'INTERMEDIATE', 'Zaawansowany': 'ADVANCED' }[l] ?? 'BEGINNER')

onMounted(async () => {
  try {
    const { data } = await api.get(`/courses/${route.params.id}/`)
    form.title       = data.title ?? ''
    form.description = data.description ?? ''
    form.category    = data.category ?? ''
    form.level       = levelLabel(data.level)
    form.tags        = (data.tags ?? []).join(', ')
    if (data.thumbnail_url) thumbPreview.value = data.thumbnail_url
  } catch (_) {}
})

const saveChanges = async () => {
  isSaving.value = true
  serverError.value = ''
  try {
    await api.patch(`/courses/${route.params.id}/edit/`, {
      title:       form.title,
      description: form.description,
      category:    form.category,
      level:       levelKey(form.level),
      tags:        form.tags.split(',').map(t => t.trim()).filter(Boolean),
    })
    saved.value = true
    setTimeout(() => (saved.value = false), 3000)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania.'
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/creator/courses" class="back-link">← Moje kursy</router-link>
        <div class="header-row">
          <h1>Edycja <span>kursu</span></h1>
          <div class="quick-links">
            <router-link :to="`/creator/courses/${route.params.id}/materials`" class="quick-link">📎 Materiały</router-link>
            <router-link :to="`/creator/courses/${route.params.id}/analytics`" class="quick-link">📊 Analityka</router-link>
            <router-link :to="`/creator/courses/${route.params.id}/publish`" class="quick-link publish">🚀 Publikacja</router-link>
          </div>
        </div>
      </div>

      <div class="form-card">
        <div class="field">
          <label>Tytuł kursu</label>
          <input v-model="form.title" type="text" />
        </div>
        <div class="field">
          <label>Opis kursu</label>
          <textarea v-model="form.description" rows="6"></textarea>
        </div>
        <div class="fields-row">
          <div class="field">
            <label>Kategoria</label>
            <select v-model="form.category">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="field">
            <label>Poziom trudności</label>
            <select v-model="form.level">
              <option v-for="l in levels" :key="l" :value="l">{{ l }}</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label>Tagi <span class="hint">(oddziel przecinkami)</span></label>
          <input v-model="form.tags" type="text" />
        </div>

        <!-- Okładka kursu -->
        <div class="field">
          <label>Okładka kursu</label>
          <input ref="thumbInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onThumbSelected" />
          <div class="thumbnail-row">
            <div class="thumbnail-preview" :style="thumbPreview ? { backgroundImage: `url(${thumbPreview})`, backgroundSize: 'cover', backgroundPosition: 'center', fontSize: 0 } : {}">
              <template v-if="!thumbPreview">📚</template>
            </div>
            <div class="thumbnail-actions">
              <button class="btn-upload" type="button" :disabled="uploadingThumb" @click="thumbInput?.click()">
                {{ uploadingThumb ? '⏳ Przesyłanie…' : '📷 Zmień okładkę' }}
              </button>
              <small>JPG/PNG/WebP, max 5MB, zalecane 1280×720px</small>
              <p v-if="thumbError" class="thumb-error">{{ thumbError }}</p>
              <p v-if="thumbSaved" class="thumb-saved">✓ Okładka zapisana</p>
            </div>
          </div>
        </div>

        <div class="form-footer">
          <span v-if="saved" class="saved-msg">✓ Zmiany zapisane</span>
          <button class="btn-save" :disabled="isSaving" @click="saveChanges">
            {{ isSaving ? 'Zapisywanie...' : 'Zapisz zmiany' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 760px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.quick-links { display: flex; gap: 0.5rem; }
.quick-link { padding: 0.45rem 0.85rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.55rem; color: #94a3b8; text-decoration: none; font-size: 0.78rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(255,255,255,0.08); } &.publish { color: #10b981; border-color: rgba(16,185,129,0.25); background: rgba(16,185,129,0.07); } }

.form-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 2.5rem; }
.field { margin-bottom: 1.25rem; }
label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; .hint { color: #475569; font-weight: 400; font-size: 0.75rem; } }
input, textarea, select { width: 100%; padding: 0.8rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem; color: white; font-size: 0.9rem; box-sizing: border-box; &::placeholder { color: #475569; } &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); } option { background: #0f172a; } }
textarea { resize: vertical; }
.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

.thumbnail-row { display: flex; gap: 1.25rem; align-items: flex-start; }
.thumbnail-preview { width: 140px; height: 90px; background: rgba(30,41,59,0.7); border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; flex-shrink: 0; overflow: hidden; }
.thumbnail-actions { display: flex; flex-direction: column; gap: 0.45rem; .btn-upload { padding: 0.5rem 1rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 0.6rem; color: #94a3b8; cursor: pointer; font-size: 0.82rem; font-weight: 600; display: block; transition: 0.2s; &:hover:not(:disabled) { background: rgba(255,255,255,0.1); } &:disabled { opacity: 0.5; cursor: not-allowed; } } small { color: #475569; font-size: 0.75rem; } .thumb-error { color: #ef4444; font-size: 0.75rem; margin: 0; } .thumb-saved { color: #10b981; font-size: 0.75rem; margin: 0; } }

.form-footer { display: flex; justify-content: flex-end; align-items: center; gap: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; margin-top: 1.5rem; }
.saved-msg { color: #10b981; font-size: 0.85rem; font-weight: 600; }
.btn-save { padding: 0.75rem 1.75rem; background: #3b82f6; color: white; border: none; border-radius: 0.7rem; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.6; cursor: not-allowed; } }
</style>