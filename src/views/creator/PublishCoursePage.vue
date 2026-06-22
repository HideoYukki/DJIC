<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()

const checklist = ref([
  { label: 'Tytuł kursu', status: false, note: '' },
  { label: 'Opis kursu', status: false, note: '' },
  { label: 'Kategoria i poziom', status: false, note: '' },
  { label: 'Minimum 1 materiał', status: false, note: '' },
])

const canPublish = computed(() => checklist.value.every(c => c.status))
const passedCount = computed(() => checklist.value.filter(c => c.status).length)
const isPublishing = ref(false)
const published = ref(false)
const serverError = ref('')

onMounted(async () => {
  try {
    const [courseRes, matsRes] = await Promise.all([
      api.get(`/courses/${route.params.id}/`),
      api.get(`/courses/${route.params.id}/materials/`),
    ])
    const c    = courseRes.data
    const mats = matsRes.data.results ?? matsRes.data ?? []
    checklist.value[0] = { label: 'Tytuł kursu',       status: !!(c.title?.trim()),       note: c.title || '—' }
    checklist.value[1] = { label: 'Opis kursu',         status: (c.description?.length ?? 0) >= 20, note: c.description?.length >= 20 ? '✓' : 'Za krótki' }
    checklist.value[2] = { label: 'Kategoria i poziom', status: !!(c.category && c.level), note: `${c.category ?? '—'} · ${c.level ?? '—'}` }
    checklist.value[3] = { label: 'Minimum 1 materiał', status: mats.length > 0,           note: `${mats.length} materiałów` }
  } catch (_) {}
})

const publish = async () => {
  isPublishing.value = true
  serverError.value = ''
  try {
    await api.post(`/courses/${route.params.id}/publish/`)
    published.value = true
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd publikacji kursu.'
  } finally {
    isPublishing.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <router-link :to="`/creator/courses/${route.params.id}/edit`" class="back-link">← Edycja kursu</router-link>

      <template v-if="!published">
        <h1>Publikacja <span>kursu</span></h1>
        <p class="subtitle">Sprawdź wymagania przed wysłaniem kursu do recenzji.</p>

        <!-- Checklist -->
        <div class="checklist-card">
          <div class="checklist-header">
            <span>Spełnione wymagania: {{ passedCount }}/{{ checklist.length }}</span>
            <div class="checklist-bar">
              <div class="bar-fill" :style="{ width: (passedCount / checklist.length * 100) + '%' }"></div>
            </div>
          </div>
          <div class="check-list">
            <div v-for="(c, i) in checklist" :key="i" class="check-item" :class="{ pass: c.status, fail: !c.status }">
              <span class="check-icon">{{ c.status ? '✅' : '❌' }}</span>
              <div class="check-info">
                <strong>{{ c.label }}</strong>
                <small>{{ c.note }}</small>
              </div>
              <router-link v-if="!c.status" :to="`/creator/courses/${route.params.id}/edit`" class="fix-link">Uzupełnij →</router-link>
            </div>
          </div>
        </div>

        <!-- Info o procesie -->
        <div class="process-info">
          <div class="proc-step">
            <div class="proc-num">1</div>
            <div><strong>Wyślij do recenzji</strong><p>Kurs trafia do weryfikacji przez administratora (1–2 dni robocze).</p></div>
          </div>
          <div class="proc-step">
            <div class="proc-num">2</div>
            <div><strong>Recenzja</strong><p>Admin sprawdza kompletność, jakość i zgodność z regulaminem platformy.</p></div>
          </div>
          <div class="proc-step">
            <div class="proc-num">3</div>
            <div><strong>Publikacja</strong><p>Po zatwierdzeniu kurs staje się dostępny w katalogu dla uczniów.</p></div>
          </div>
        </div>

        <div class="publish-actions">
          <router-link to="/creator/courses" class="btn-cancel">Anuluj</router-link>
          <button class="btn-publish" :disabled="!canPublish || isPublishing" @click="publish">
            {{ isPublishing ? 'Wysyłanie...' : '🚀 Wyślij do recenzji' }}
          </button>
        </div>
        <p v-if="!canPublish" class="not-ready">Uzupełnij brakujące wymagania, aby opublikować kurs.</p>
      </template>

      <template v-else>
        <div class="success-state">
          <div class="success-icon">🎉</div>
          <h2>Kurs wysłany do recenzji!</h2>
          <p>Administrator platformy sprawdzi Twój kurs w ciągu 1–2 dni roboczych. Otrzymasz powiadomienie po zatwierdzeniu.</p>
          <div class="success-actions">
            <router-link to="/creator/courses" class="btn-primary">Wróć do moich kursów</router-link>
            <router-link to="/creator/dashboard" class="btn-ghost">Panel twórcy</router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 720px; margin: 0 auto; }
.back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 1.5rem; }
h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.4rem; span { color: #3b82f6; } }
.subtitle { color: #64748b; margin-bottom: 2rem; }

.checklist-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1.5rem; padding: 2rem; margin-bottom: 2rem; }
.checklist-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #94a3b8; flex-wrap: wrap; }
.checklist-bar { height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; width: 200px; flex-shrink: 0; }
.bar-fill { height: 100%; background: #10b981; border-radius: 3px; transition: width 0.5s ease; }
.check-list { display: flex; flex-direction: column; gap: 0.75rem; }
.check-item { display: flex; align-items: center; gap: 0.85rem; padding: 0.85rem; border-radius: 0.85rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); .check-icon { font-size: 1.1rem; flex-shrink: 0; } .check-info { flex: 1; strong { display: block; font-size: 0.88rem; margin-bottom: 0.15rem; } small { color: #64748b; font-size: 0.75rem; } } .fix-link { color: #f59e0b; text-decoration: none; font-size: 0.78rem; font-weight: 700; white-space: nowrap; &:hover { text-decoration: underline; } } &.fail { border-color: rgba(239,68,68,0.15); background: rgba(239,68,68,0.04); } }

.process-info { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
.proc-step { display: flex; align-items: flex-start; gap: 1rem; padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 0.85rem; .proc-num { width: 30px; height: 30px; background: rgba(59,130,246,0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 800; color: #60a5fa; flex-shrink: 0; } strong { display: block; font-size: 0.9rem; margin-bottom: 0.2rem; } p { color: #64748b; font-size: 0.82rem; margin: 0; } }

.publish-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.btn-cancel { padding: 0.75rem 1.4rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #64748b; border-radius: 0.75rem; text-decoration: none; font-weight: 600; font-size: 0.88rem; }
.btn-publish { padding: 0.75rem 1.6rem; background: #10b981; color: white; border: none; border-radius: 0.75rem; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: 0.2s; &:hover:not(:disabled) { background: #059669; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.not-ready { text-align: right; color: #ef4444; font-size: 0.8rem; margin-top: 0.75rem; }

.success-state { text-align: center; padding: 3rem 1rem; .success-icon { font-size: 4rem; display: block; margin-bottom: 1rem; } h2 { font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; } p { color: #94a3b8; max-width: 450px; margin: 0 auto 2.5rem; line-height: 1.6; } }
.success-actions { display: flex; gap: 0.75rem; justify-content: center; }
.btn-primary { display: inline-block; padding: 0.8rem 1.6rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; transition: 0.2s; &:hover { background: #2563eb; } }
.btn-ghost { display: inline-block; padding: 0.8rem 1.4rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 0.75rem; text-decoration: none; font-weight: 600; transition: 0.2s; &:hover { border-color: rgba(255,255,255,0.18); } }
</style>