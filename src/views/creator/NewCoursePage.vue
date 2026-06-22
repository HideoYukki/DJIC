<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const router = useRouter()

const step = ref(1)
const form = reactive({
  title: '',
  description: '',
  category: '',
  level: 'Początkujący',
  tags: '',
})

const errors = reactive({ title: '', description: '' })
const serverError = ref('')
const submitting = ref(false)

const thumbFile       = ref(null)
const thumbPreview    = ref(null)
const thumbInput      = ref(null)
const thumbError      = ref('')

const onThumbSelected = (e) => {
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
  thumbFile.value = file
  thumbPreview.value = URL.createObjectURL(file)
}

const categories = ['Frontend', 'Backend', 'Bazy danych', 'DevOps', 'Mobile', 'Bezpieczeństwo', 'UI/UX', 'Data Science']
const levels = ['Początkujący', 'Średniozaawansowany', 'Zaawansowany']

const validateStep1 = () => {
  errors.title = form.title.trim() ? '' : 'Tytuł jest wymagany'
  errors.description = form.description.trim().length >= 20 ? '' : 'Opis musi mieć minimum 20 znaków'
  return !errors.title && !errors.description
}

const nextStep = () => { if (step.value === 1 && !validateStep1()) return; step.value++ }
const prevStep = () => { if (step.value > 1) step.value-- }

const levelKey = (l) => ({ 'Początkujący': 'BEGINNER', 'Średniozaawansowany': 'INTERMEDIATE', 'Zaawansowany': 'ADVANCED' }[l] ?? 'BEGINNER')

const handleSubmit = async () => {
  submitting.value = true
  serverError.value = ''
  try {
    const { data } = await api.post('courses/new/', {
      title: form.title,
      description: form.description,
      category: form.category,
      level: levelKey(form.level),
      tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
    })
    if (thumbFile.value) {
      const fd = new FormData()
      fd.append('file', thumbFile.value)
      await api.post(`/courses/${data.id}/thumbnail/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }).catch(() => {})
    }
    router.push(`/creator/courses/${data.id}/materials`)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd tworzenia kursu.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/creator/courses" class="back-link">← Moje kursy</router-link>
        <h1>Nowy <span>kurs</span></h1>
      </div>

      <!-- Stepper -->
      <div class="stepper">
        <div v-for="i in 3" :key="i" class="step" :class="{ active: step === i, done: step > i }">
          <div class="step-num">{{ step > i ? '✓' : i }}</div>
          <span>{{ ['Podstawy', 'Okładka', 'Podsumowanie'][i - 1] }}</span>
        </div>
      </div>

      <div class="form-card">
        <!-- Krok 1: Podstawowe informacje -->
        <div v-if="step === 1">
          <h2>Podstawowe informacje</h2>
          <div class="field" :class="{ error: errors.title }">
            <label>Tytuł kursu *</label>
            <input v-model="form.title" type="text" placeholder="np. Podstawy Vue.js 3 dla programistów React" />
            <span class="error-msg">{{ errors.title }}</span>
          </div>
          <div class="field" :class="{ error: errors.description }">
            <label>Opis kursu *</label>
            <textarea v-model="form.description" rows="5" placeholder="Opisz, czego nauczą się uczestnicy kursu (minimum 20 znaków)..."></textarea>
            <span class="error-msg">{{ errors.description }}</span>
            <span class="char-count">{{ form.description.length }} znaków</span>
          </div>
          <div class="fields-row">
            <div class="field">
              <label>Kategoria</label>
              <select v-model="form.category">
                <option value="">Wybierz kategorię</option>
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
            <input v-model="form.tags" type="text" placeholder="np. Vue.js, JavaScript, Frontend" />
          </div>
        </div>

        <!-- Krok 2: Okładka -->
        <div v-if="step === 2">
          <h2>Okładka kursu</h2>
          <input ref="thumbInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onThumbSelected" />
          <div class="upload-area" :class="{ 'has-preview': thumbPreview }" @click="thumbInput?.click()">
            <img v-if="thumbPreview" :src="thumbPreview" class="thumb-preview-img" alt="Podgląd okładki" />
            <template v-else>
              <span class="upload-icon">🖼️</span>
              <p>Kliknij, aby wybrać okładkę</p>
              <small>Rekomendowany format: 1280×720px, JPG lub PNG, max 5MB</small>
            </template>
          </div>
          <p v-if="thumbError" class="thumb-error">{{ thumbError }}</p>
          <p v-if="thumbPreview" class="upload-note upload-note-success">✓ Okładka zostanie zapisana po utworzeniu kursu.</p>
          <p v-else class="upload-note">Możesz dodać okładkę później — przejdź do sekcji "Edytuj kurs".</p>
        </div>

        <!-- Krok 3: Podsumowanie -->
        <div v-if="step === 3">
          <h2>Podsumowanie</h2>
          <div class="summary-card">
            <div class="summary-row"><span>Tytuł:</span><strong>{{ form.title || '—' }}</strong></div>
            <div class="summary-row"><span>Kategoria:</span><strong>{{ form.category || '—' }}</strong></div>
            <div class="summary-row"><span>Poziom:</span><strong>{{ form.level }}</strong></div>
            <div class="summary-row"><span>Tagi:</span><strong>{{ form.tags || '—' }}</strong></div>
          </div>
          <p class="summary-note">Po kliknięciu "Utwórz kurs" zostaniesz przekierowany do edytora, gdzie dodasz rozdziały i materiały.</p>
        </div>

        <!-- Nawigacja kroku -->
        <div class="step-nav">
          <button v-if="step > 1" class="btn-prev" @click="prevStep">← Wróć</button>
          <div class="step-spacer"></div>
          <button v-if="step < 3" class="btn-next" @click="nextStep">Dalej →</button>
          <button v-if="step === 3" class="btn-submit" @click="handleSubmit">🚀 Utwórz kurs</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 760px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 1rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }

.stepper { display: flex; gap: 0.5rem; margin-bottom: 2rem; }
.step { display: flex; align-items: center; gap: 0.5rem; flex: 1; opacity: 0.5; transition: 0.2s; &.active, &.done { opacity: 1; } &.active .step-num { background: #3b82f6; } &.done .step-num { background: #10b981; } }
.step-num { width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 800; flex-shrink: 0; }
.step span { font-size: 0.82rem; color: #94a3b8; }

.form-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 2.5rem; h2 { font-size: 1.2rem; font-weight: 700; margin: 0 0 2rem; } }

.field { margin-bottom: 1.25rem; &.error input, &.error textarea { border-color: #ef4444; } }
label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; .hint { color: #475569; font-weight: 400; font-size: 0.75rem; } }
input, textarea, select {
  width: 100%; padding: 0.8rem 1rem;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem;
  color: white; font-size: 0.9rem; box-sizing: border-box;
  &::placeholder { color: #475569; }
  &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
  option { background: #0f172a; }
}
textarea { resize: vertical; }
.error-msg { display: block; color: #ef4444; font-size: 0.72rem; margin-top: 0.3rem; }
.char-count { display: block; text-align: right; color: #475569; font-size: 0.72rem; margin-top: 0.2rem; }
.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

.upload-area {
  border: 2px dashed rgba(255,255,255,0.12); border-radius: 1rem; padding: 3rem 2rem; text-align: center; margin-bottom: 1rem; cursor: pointer; transition: border-color 0.2s;
  &:hover { border-color: rgba(59,130,246,0.4); }
  &.has-preview { padding: 0; overflow: hidden; }
  .upload-icon { font-size: 3rem; display: block; margin-bottom: 1rem; }
  p { color: #64748b; margin-bottom: 0.5rem; }
  small { color: #475569; font-size: 0.78rem; display: block; }
}
.thumb-preview-img { width: 100%; height: 220px; object-fit: cover; border-radius: inherit; display: block; }
.thumb-error { color: #ef4444; font-size: 0.78rem; margin: 0 0 0.5rem; }
.upload-note { color: #475569; font-size: 0.82rem; &.upload-note-success { color: #10b981; } }

.summary-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 1rem; padding: 1.5rem; margin-bottom: 1.5rem; }
.summary-row { display: flex; gap: 1rem; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); &:last-child { border-bottom: none; } span { color: #64748b; font-size: 0.87rem; width: 100px; flex-shrink: 0; } strong { color: #f1f5f9; font-size: 0.87rem; } }
.summary-note { color: #64748b; font-size: 0.85rem; line-height: 1.5; }

.step-nav { display: flex; align-items: center; margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1.5rem; }
.step-spacer { flex: 1; }
.btn-prev { padding: 0.7rem 1.4rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.7rem; color: #94a3b8; cursor: pointer; font-weight: 600; font-size: 0.88rem; transition: 0.2s; &:hover { background: rgba(255,255,255,0.09); } }
.btn-next, .btn-submit { padding: 0.7rem 1.6rem; background: #3b82f6; border: none; border-radius: 0.7rem; color: white; cursor: pointer; font-weight: 700; font-size: 0.9rem; transition: 0.2s; &:hover { background: #2563eb; transform: translateY(-1px); } }
</style>