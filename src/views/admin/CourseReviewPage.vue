<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()

const course = ref({
  id: route.params.id,
  title: '',
  creator: '',
  description: '',
  category: '',
  level: '',
  duration: '',
  materials: 0,
  submitted: '',
  status: 'REVIEW',
})

const checks = ref([])
const comment = ref('')
const submitting = ref(false)
const decision = ref('')
const serverError = ref('')

onMounted(async () => {
  try {
    const [courseRes, matsRes] = await Promise.all([
      api.get(`/courses/${route.params.id}/`),
      api.get(`/courses/${route.params.id}/materials/`),
    ])
    const c    = courseRes.data
    const mats = matsRes.data.results ?? matsRes.data ?? []
    course.value = {
      id: c.id,
      title: c.title ?? '',
      creator: c.creator_name ?? '—',
      description: c.description ?? '',
      category: c.category ?? '',
      level: c.level ?? '',
      duration: c.duration_minutes ? `${c.duration_minutes} min` : '—',
      materials: mats.length,
      submitted: c.created_at?.slice(0, 10) ?? '',
      status: c.status,
    }
    checks.value = [
      { label: 'Tytuł kursu',          ok: !!(c.title?.trim()) },
      { label: 'Opis kursu',           ok: (c.description?.length ?? 0) >= 20 },
      { label: 'Kategoria i poziom',   ok: !!(c.category && c.level) },
      { label: 'Minimum 1 materiał',   ok: mats.length >= 1 },
    ]
  } catch (_) {}
})

async function approve() {
  submitting.value = true
  serverError.value = ''
  decision.value = 'approved'
  try {
    await api.post(`/courses/${route.params.id}/approve/`)
    router.push('/admin/courses')
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zatwierdzania.'
    decision.value = ''
  } finally {
    submitting.value = false
  }
}

async function reject() {
  submitting.value = true
  serverError.value = ''
  decision.value = 'rejected'
  try {
    await api.post(`/courses/${route.params.id}/reject/`, { reason: comment.value })
    router.push('/admin/courses')
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd odrzucania.'
    decision.value = ''
  } finally {
    submitting.value = false
  }
}

const failedChecks = () => checks.value.filter(c => !c.ok).length
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/courses" class="back-link">← Przeglądaj kursy</router-link>
        <div class="review-badge">RECENZJA</div>
        <h1>{{ course.title }}</h1>
        <p class="meta">Autor: <strong>{{ course.creator }}</strong> · Przesłano: {{ course.submitted }}</p>
      </div>

      <div class="two-col">
        <!-- Informacje o kursie -->
        <div class="panel">
          <h2 class="panel-title">Szczegóły kursu</h2>
          <p class="course-desc">{{ course.description }}</p>
          <div class="info-grid">
            <div class="info-item"><label>Kategoria</label><span>{{ course.category }}</span></div>
            <div class="info-item"><label>Poziom</label><span>{{ course.level }}</span></div>
            <div class="info-item"><label>Czas trwania</label><span>{{ course.duration }}</span></div>
            <div class="info-item"><label>Materiały</label><span>{{ course.materials }}</span></div>
          </div>
          <a href="#" class="preview-link">👁 Podgląd kursu jako student →</a>
        </div>

        <!-- Checklista walidacji -->
        <div class="panel">
          <h2 class="panel-title">
            Checklista jakości
            <span v-if="failedChecks() > 0" class="warn-chip">{{ failedChecks() }} problem{{ failedChecks() > 1 ? 'y' : '' }}</span>
          </h2>
          <div class="checklist">
            <div v-for="(c, i) in checks" :key="i" class="check-item" :class="{ fail: !c.ok }">
              <span class="check-icon">{{ c.ok ? '✓' : '✗' }}</span>
              <span>{{ c.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Komentarz recenzenta -->
      <div class="panel comment-panel">
        <h2 class="panel-title">Komentarz recenzenta</h2>
        <p class="comment-hint">Opcjonalnie — wypełnij przy odrzuceniu, aby twórca wiedział co poprawić.</p>
        <textarea
          v-model="comment"
          rows="4"
          placeholder="Opisz uwagi do kursu…"
        ></textarea>
      </div>

      <!-- Decyzja -->
      <div class="decision-panel">
        <div class="decision-info">
          <span class="decision-label">Twoja decyzja wpłynie na status kursu</span>
          <span class="decision-sub">Akceptacja → kurs staje się aktywny · Odrzucenie → wraca do Szkicu z komentarzem</span>
        </div>
        <div class="decision-btns">
          <button class="btn-reject" :disabled="submitting" @click="reject">
            ✗ Odrzuć kurs
          </button>
          <button class="btn-approve" :disabled="submitting" @click="approve">
            {{ submitting && decision === 'approved' ? 'Zatwierdzanie…' : '✓ Zatwierdź i opublikuj' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 1.9rem; font-weight: 800; margin: 0 0 0.4rem; } .meta { color: #64748b; font-size: 0.85rem; margin: 0; strong { color: #94a3b8; } } }
.review-badge { display: inline-block; background: rgba(245,158,11,0.12); color: #fbbf24; font-size: 0.65rem; font-weight: 800; letter-spacing: 2px; padding: 0.25rem 0.75rem; border-radius: 999px; border: 1px solid rgba(245,158,11,0.25); margin-bottom: 0.75rem; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; @media (max-width: 768px) { grid-template-columns: 1fr; } }
.panel { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; }
.panel-title { display: flex; align-items: center; gap: 0.75rem; font-size: 0.95rem; font-weight: 700; margin: 0 0 1.25rem; }
.warn-chip { background: rgba(239,68,68,0.1); color: #f87171; font-size: 0.68rem; font-weight: 800; padding: 0.15rem 0.6rem; border-radius: 999px; }

.course-desc { color: #94a3b8; font-size: 0.87rem; line-height: 1.65; margin: 0 0 1.25rem; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; margin-bottom: 1.25rem; }
.info-item { label { display: block; font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 0.2rem; } span { font-size: 0.87rem; } }
.preview-link { color: #3b82f6; font-size: 0.85rem; font-weight: 600; text-decoration: none; &:hover { text-decoration: underline; } }

.checklist { display: flex; flex-direction: column; gap: 0.55rem; }
.check-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.6rem 0.85rem; background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.12); border-radius: 0.65rem; font-size: 0.87rem; .check-icon { font-weight: 800; color: #10b981; font-size: 0.9rem; width: 20px; text-align: center; } &.fail { background: rgba(239,68,68,0.05); border-color: rgba(239,68,68,0.12); .check-icon { color: #f87171; } } }

.comment-panel { margin-bottom: 1.25rem; }
.comment-hint { color: #64748b; font-size: 0.8rem; margin: -0.75rem 0 0.85rem; }
textarea { width: 100%; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; padding: 0.85rem 1rem; color: #e2e8f0; font-size: 0.87rem; resize: vertical; outline: none; font-family: inherit; &:focus { border-color: rgba(59,130,246,0.35); } }

.decision-panel { display: flex; justify-content: space-between; align-items: center; background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.25rem 1.5rem; gap: 1rem; flex-wrap: wrap; }
.decision-info { .decision-label { display: block; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.25rem; } .decision-sub { font-size: 0.75rem; color: #64748b; } }
.decision-btns { display: flex; gap: 0.75rem; }
.btn-reject { padding: 0.7rem 1.4rem; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: #f87171; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: rgba(239,68,68,0.14); } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.btn-approve { padding: 0.7rem 1.6rem; background: #10b981; color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: #059669; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
</style>