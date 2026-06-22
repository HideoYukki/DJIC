<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const uid = () => (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2)

const route = useRoute()
const courseId = route.params.id
const quizId   = route.params.quizId

const questions = ref([])
const newQuestion = reactive({ text: '', options: ['', '', '', ''], correct: 0 })
const showAddForm = ref(false)
const isSaving = ref(false)
const serverError = ref('')

const saveQuestion = () => {
  if (!newQuestion.text.trim()) return
  questions.value.push({
    id: uid(),
    text: newQuestion.text,
    options: [...newQuestion.options],
    correct: newQuestion.correct,
    isOpen: false,
    _new: true,
  })
  Object.assign(newQuestion, { text: '', options: ['', '', '', ''], correct: 0 })
  showAddForm.value = false
}

const deleteQuestion = (id) => {
  questions.value = questions.value.filter(q => q.id !== id)
}

const saveAll = async () => {
  isSaving.value = true
  serverError.value = ''
  try {
    const payload = {
      questions: questions.value.map((q, idx) => {
        const opts = q.options.map(o => ({ id: uid(), text: o }))
        return {
          id: q.id,
          text: q.text,
          options: opts,
          correct_option_id: opts[q.correct]?.id ?? opts[0]?.id,
          points: 1,
        }
      }),
    }
    if (quizId) {
      await api.put(`/courses/${courseId}/quizzes/${quizId}/edit/`, payload)
    } else {
      await api.post(`/courses/${courseId}/quizzes/`, { title: 'Quiz', ...payload })
    }
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania quizu.'
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  if (!quizId) return
  try {
    const { data } = await api.get(`/courses/${courseId}/quizzes/${quizId}/`)
    questions.value = (data.questions ?? []).map(q => ({
      id: q.id,
      text: q.text,
      options: q.options.map(o => o.text),
      correct: Math.max(0, q.options.findIndex(o => o.id === q.correct_option_id)),
      isOpen: false,
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${route.params.id}/materials`" class="back-link">← Materiały kursu</router-link>
        <div class="header-row">
          <h1>Edytor <span>quizu</span></h1>
          <button class="btn-save" :disabled="isSaving" @click="saveAll">
            {{ isSaving ? 'Zapisywanie...' : '💾 Zapisz quiz' }}
          </button>
        </div>
        <p class="subtitle">{{ questions.length }} pytań · Próg zaliczenia: 70%</p>
      </div>

      <!-- Lista pytań -->
      <div class="questions-list">
        <div v-for="(q, qi) in questions" :key="q.id" class="question-card">
          <div class="q-header" @click="q.isOpen = !q.isOpen">
            <span class="q-num">{{ qi + 1 }}</span>
            <p class="q-text">{{ q.text }}</p>
            <span class="q-toggle">{{ q.isOpen ? '▾' : '▸' }}</span>
            <button class="btn-del" @click.stop="deleteQuestion(q.id)">🗑️</button>
          </div>
          <div v-if="q.isOpen" class="q-options">
            <div v-for="(opt, oi) in q.options" :key="oi" class="option-row" :class="{ correct: oi === q.correct }">
              <span class="opt-letter">{{ ['A','B','C','D'][oi] }}</span>
              <span class="opt-text">{{ opt }}</span>
              <span v-if="oi === q.correct" class="correct-mark">✓ Poprawna</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Dodaj pytanie -->
      <div v-if="!showAddForm" class="add-btn" @click="showAddForm = true">+ Dodaj pytanie</div>
      <div v-else class="add-form">
        <h3>Nowe pytanie</h3>
        <div class="field">
          <label>Treść pytania</label>
          <textarea v-model="newQuestion.text" rows="3" placeholder="Wpisz treść pytania..."></textarea>
        </div>
        <div class="options-form">
          <div v-for="(opt, oi) in newQuestion.options" :key="oi" class="option-input-row">
            <button class="correct-radio" :class="{ active: newQuestion.correct === oi }" @click="newQuestion.correct = oi" type="button">
              {{ newQuestion.correct === oi ? '●' : '○' }}
            </button>
            <span class="opt-letter-sm">{{ ['A','B','C','D'][oi] }}</span>
            <input v-model="newQuestion.options[oi]" type="text" :placeholder="`Odpowiedź ${['A','B','C','D'][oi]}`" />
          </div>
          <p class="radio-hint">Kliknij ● aby oznaczyć poprawną odpowiedź</p>
        </div>
        <div class="add-form-footer">
          <button class="btn-cancel" @click="showAddForm = false">Anuluj</button>
          <button class="btn-confirm" @click="saveQuestion">Dodaj pytanie</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 820px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 0; } }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.btn-save { padding: 0.7rem 1.4rem; background: #10b981; color: white; border: none; border-radius: 0.7rem; font-weight: 700; cursor: pointer; transition: 0.2s; &:hover:not(:disabled) { background: #059669; } &:disabled { opacity: 0.6; } }

.questions-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.25rem; }
.question-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1rem; overflow: hidden; }
.q-header { display: flex; align-items: center; gap: 0.75rem; padding: 1rem 1.25rem; cursor: pointer; transition: 0.15s; &:hover { background: rgba(255,255,255,0.02); } }
.q-num { width: 28px; height: 28px; background: rgba(59,130,246,0.15); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 800; color: #60a5fa; flex-shrink: 0; }
.q-text { flex: 1; font-size: 0.9rem; color: #e2e8f0; margin: 0; }
.q-toggle { color: #64748b; font-size: 0.8rem; }
.btn-del { background: none; border: none; cursor: pointer; color: #475569; font-size: 0.85rem; padding: 0.2rem 0.3rem; border-radius: 0.4rem; &:hover { color: #ef4444; } }

.q-options { padding: 0.5rem 1.25rem 1rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 0.4rem; }
.option-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.55rem 0.75rem; border-radius: 0.6rem; background: rgba(255,255,255,0.02); font-size: 0.85rem; .opt-letter { width: 22px; height: 22px; border-radius: 6px; background: rgba(255,255,255,0.07); display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 800; flex-shrink: 0; } .opt-text { flex: 1; color: #cbd5e1; } .correct-mark { font-size: 0.72rem; color: #10b981; font-weight: 700; } &.correct { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); } }

.add-btn { padding: 1rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 1rem; text-align: center; color: #64748b; cursor: pointer; font-size: 0.9rem; font-weight: 600; transition: 0.2s; &:hover { border-color: rgba(59,130,246,0.3); color: #3b82f6; } }

.add-form { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 1.25rem; padding: 2rem; h3 { font-size: 1rem; font-weight: 700; margin: 0 0 1.25rem; } }
.field { margin-bottom: 1.25rem; label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; } }
textarea, input { width: 100%; padding: 0.75rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem; color: white; font-size: 0.88rem; box-sizing: border-box; resize: vertical; &::placeholder { color: #475569; } &:focus { outline: none; border-color: #3b82f6; } }
.options-form { margin-bottom: 1rem; }
.option-input-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; .correct-radio { background: none; border: 2px solid rgba(255,255,255,0.15); border-radius: 50%; width: 26px; height: 26px; color: #64748b; cursor: pointer; font-size: 0.85rem; flex-shrink: 0; transition: 0.15s; &.active { border-color: #10b981; color: #10b981; } } .opt-letter-sm { color: #64748b; font-weight: 700; font-size: 0.8rem; width: 16px; flex-shrink: 0; } }
.radio-hint { color: #475569; font-size: 0.75rem; margin-top: 0.5rem; }
.add-form-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1rem; }
.btn-cancel { padding: 0.65rem 1.25rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #64748b; border-radius: 0.65rem; cursor: pointer; font-size: 0.85rem; }
.btn-confirm { padding: 0.65rem 1.4rem; background: #3b82f6; color: white; border: none; border-radius: 0.65rem; font-weight: 700; cursor: pointer; font-size: 0.85rem; transition: 0.2s; &:hover { background: #2563eb; } }
</style>