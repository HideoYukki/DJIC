<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const settings = ref({
  platformName: 'DJIC Learning',
  maxCoursesPerCreator: 50,
  allowRegistration: true,
  maintenanceMode: false,
})

const categories = ref([])
const newCategory = ref('')
const saving = ref(false)
const saved = ref(false)
const serverError = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/admin/settings/')
    if (data.max_courses_per_creator) settings.value.maxCoursesPerCreator = Number(data.max_courses_per_creator)
    if (data.registration_enabled !== undefined) settings.value.allowRegistration = data.registration_enabled === 'true'
    if (data.maintenance_mode !== undefined) settings.value.maintenanceMode = data.maintenance_mode === 'true'
  } catch (_) {}
})

async function saveSettings() {
  saving.value = true
  serverError.value = ''
  try {
    await api.patch('/admin/settings/', {
      max_courses_per_creator: String(settings.value.maxCoursesPerCreator),
      registration_enabled: String(settings.value.allowRegistration),
      maintenance_mode: String(settings.value.maintenanceMode),
    })
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania.'
  } finally {
    saving.value = false
  }
}

function addCategory() {
  if (!newCategory.value.trim()) return
  categories.value.push({ id: Date.now(), name: newCategory.value.trim(), courses: 0 })
  newCategory.value = ''
}

function removeCategory(id) {
  categories.value = categories.value.filter(c => c.id !== id)
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/dashboard" class="back-link">← Panel admina</router-link>
        <h1>Ustawienia <span>platformy</span></h1>
        <p class="subtitle">Konfiguracja globalna systemu DJIC</p>
      </div>

      <div class="settings-grid">
        <!-- Ogólne -->
        <div class="panel">
          <h2 class="panel-title">⚙️ Ogólne</h2>

          <div class="field">
            <label>Nazwa platformy</label>
            <input v-model="settings.platformName" type="text" />
          </div>

          <div class="field-row">
            <div class="field">
              <label>Max kursów / twórca</label>
              <input v-model.number="settings.maxCoursesPerCreator" type="number" min="1" />
            </div>
            <div class="field">
              <label>Max uczniów / kurs</label>
              <input v-model.number="settings.maxStudentsPerCourse" type="number" min="1" />
            </div>
          </div>

          <div class="field">
            <label>Domyślny język</label>
            <select v-model="settings.defaultLanguage">
              <option value="pl">Polski</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <!-- Rejestracja i bezpieczeństwo -->
        <div class="panel">
          <h2 class="panel-title">🔒 Rejestracja i dostęp</h2>

          <div class="toggle-item">
            <div>
              <strong>Rejestracja otwarta</strong>
              <small>Nowi użytkownicy mogą zakładać konta</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.allowRegistration" />
              <span class="slider"></span>
            </label>
          </div>

          <div class="toggle-item">
            <div>
              <strong>Potwierdzenie e-mail</strong>
              <small>Wymagane przy rejestracji (DJIC-17)</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.requireEmailConfirmation" />
              <span class="slider"></span>
            </label>
          </div>

          <div class="toggle-item danger-toggle">
            <div>
              <strong>Tryb konserwacji</strong>
              <small>Blokuje dostęp do platformy dla użytkowników</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.maintenanceMode" />
              <span class="slider danger"></span>
            </label>
          </div>

          <div v-if="settings.maintenanceMode" class="maintenance-warn">
            ⚠️ Tryb konserwacji jest włączony — platforma jest niedostępna dla użytkowników
          </div>
        </div>
      </div>

      <!-- Kategorie kursów -->
      <div class="panel categories-panel">
        <h2 class="panel-title">🏷️ Kategorie kursów</h2>
        <div class="categories-list">
          <div v-for="cat in categories" :key="cat.id" class="category-row">
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-count">{{ cat.courses }} kurs{{ cat.courses === 1 ? '' : 'ów' }}</span>
            <button class="btn-remove" @click="removeCategory(cat.id)" :disabled="cat.courses > 0" title="Usuń kategorię">✕</button>
          </div>
        </div>
        <div class="add-category">
          <input v-model="newCategory" type="text" placeholder="Nowa kategoria…" @keydown.enter="addCategory" />
          <button class="btn-add" @click="addCategory">Dodaj</button>
        </div>
      </div>

      <!-- Akcje -->
      <div class="save-bar">
        <span v-if="saved" class="saved-msg">✓ Ustawienia zapisane</span>
        <button class="btn-save" :disabled="saving" @click="saveSettings">
          {{ saving ? 'Zapisywanie…' : 'Zapisz ustawienia' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1000px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } } .subtitle { color: #64748b; font-size: 0.85rem; } }

.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; @media (max-width: 768px) { grid-template-columns: 1fr; } }
.panel { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; }
.panel-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 1.25rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1rem; label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; } input, select { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 0.65rem 1rem; color: white; font-size: 0.88rem; outline: none; &:focus { border-color: rgba(59,130,246,0.4); } } select option { background: #0f172a; } }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }

.toggle-item { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); &:last-of-type { border-bottom: none; } strong { display: block; font-size: 0.87rem; margin-bottom: 0.2rem; } small { color: #64748b; font-size: 0.72rem; } }
.switch { position: relative; display: inline-block; width: 42px; height: 22px; flex-shrink: 0; input { display: none; &:checked + .slider { background: #3b82f6; &::before { transform: translateX(20px); } &.danger { background: #ef4444; } } } }
.slider { position: absolute; cursor: pointer; inset: 0; background: rgba(255,255,255,0.1); border-radius: 999px; transition: 0.2s; &::before { content: ''; position: absolute; width: 16px; height: 16px; left: 3px; top: 3px; background: white; border-radius: 50%; transition: 0.2s; } }
.maintenance-warn { margin-top: 1rem; padding: 0.75rem 1rem; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); border-radius: 0.75rem; color: #fbbf24; font-size: 0.82rem; font-weight: 600; }

.categories-panel { margin-bottom: 1.25rem; }
.categories-list { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1rem; }
.category-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.85rem; background: rgba(255,255,255,0.02); border-radius: 0.65rem; .cat-name { flex: 1; font-size: 0.87rem; } .cat-count { font-size: 0.75rem; color: #64748b; } }
.btn-remove { width: 24px; height: 24px; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15); color: #f87171; border-radius: 6px; cursor: pointer; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; transition: 0.15s; &:hover:not(:disabled) { background: rgba(239,68,68,0.15); } &:disabled { opacity: 0.3; cursor: not-allowed; } }
.add-category { display: flex; gap: 0.75rem; input { flex: 1; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 0.65rem 1rem; color: white; font-size: 0.88rem; outline: none; &::placeholder { color: #475569; } &:focus { border-color: rgba(59,130,246,0.35); } } }
.btn-add { padding: 0.65rem 1.25rem; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.25); color: #60a5fa; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.85rem; white-space: nowrap; transition: 0.15s; &:hover { background: rgba(59,130,246,0.18); } }

.save-bar { display: flex; justify-content: flex-end; align-items: center; gap: 1.25rem; }
.saved-msg { color: #10b981; font-size: 0.85rem; font-weight: 600; }
.btn-save { padding: 0.75rem 1.75rem; background: #3b82f6; color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.9rem; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
</style>