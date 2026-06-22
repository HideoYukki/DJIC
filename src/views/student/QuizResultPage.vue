<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route  = useRoute()
const router = useRouter()

const score    = computed(() => Number(route.query.score ?? 0))
const total    = computed(() => Number(route.query.total ?? 1))
const percent  = computed(() => total.value > 0 ? Math.round((score.value / total.value) * 100) : 0)
const passed   = computed(() => route.query.passed ? route.query.passed === '1' : percent.value >= 60)
const xpEarned = computed(() => route.query.xp ? Number(route.query.xp) : (passed.value ? score.value * 50 : score.value * 20))

const grade = computed(() => {
  if (percent.value >= 90) return { label: 'Doskonały wynik!', color: '#10b981', icon: '🏆' }
  if (percent.value >= 60) return { label: 'Zaliczono!', color: '#3b82f6', icon: '✅' }
  return { label: 'Nie zaliczono', color: '#ef4444', icon: '❌' }
})

// Dane szczegółowe z history.state (przekazane przez QuizPage po submit)
const historyState   = window.history.state ?? {}
const userAnswers    = historyState.userAnswers ?? []      // [{questionId, selected (idx), optionId}]
const historyQuestions = historyState.questions ?? []     // [{id, text, options, _optionIds}]
const correctAnswers = historyState.correctAnswers ?? {}   // {questionId: correctOptionId}

// Jeśli brak danych w state, próbujemy pobrać z API
const apiQuestions = ref([])
const apiCorrectAnswers = ref({})
const loading = ref(false)

onMounted(async () => {
  if (historyQuestions.length > 0) return
  loading.value = true
  try {
    const [quizRes, resultRes] = await Promise.all([
      api.get(`/courses/${route.params.id}/quizzes/${route.params.quizId}/`),
      api.get(`/courses/${route.params.id}/quizzes/${route.params.quizId}/result/`),
    ])
    apiQuestions.value = (quizRes.data.questions ?? []).map(q => ({
      id: q.id,
      text: q.text,
      options: q.options.map(o => o.text),
      _optionIds: q.options.map(o => o.id),
    }))
    apiCorrectAnswers.value = resultRes.data.correct_answers ?? {}
  } catch (_) {}
  finally { loading.value = false }
})

const questions    = computed(() => historyQuestions.length ? historyQuestions : apiQuestions.value)
const correctMap   = computed(() => Object.keys(correctAnswers).length ? correctAnswers : apiCorrectAnswers.value)
const answerMap    = computed(() => Object.fromEntries(userAnswers.map(a => [a.questionId, a.optionId])))

const detailedAnswers = computed(() =>
  questions.value.map(q => {
    const userOptionId    = answerMap.value[q.id] ?? null
    const correctOptionId = correctMap.value[q.id] ?? null
    const userIdx    = userOptionId    ? q._optionIds?.indexOf(userOptionId)    : -1
    const correctIdx = correctOptionId ? q._optionIds?.indexOf(correctOptionId) : -1
    return {
      text:         q.text,
      options:      q.options,
      userIdx,
      correctIdx,
      isCorrect:    userOptionId !== null && userOptionId === correctOptionId,
      wasSkipped:   userOptionId === null,
    }
  })
)
</script>

<template>
  <div class="page-wrapper">
    <div class="result-card">

      <div class="result-icon">{{ grade.icon }}</div>
      <h1 :style="{ color: grade.color }">{{ grade.label }}</h1>

      <!-- Koło wynik -->
      <div class="score-circle" :style="{ '--pct': percent + '%', '--color': grade.color }">
        <span class="score-number">{{ percent }}%</span>
        <span class="score-label">{{ score }}/{{ total }} poprawnych</span>
      </div>

      <div class="xp-earned">
        <span class="xp-icon">⚡</span>
        <span>+{{ xpEarned }} XP zdobyte</span>
      </div>

      <!-- Szczegółowe odpowiedzi -->
      <div v-if="loading" class="loading-note">Ładowanie szczegółów…</div>

      <div v-else-if="detailedAnswers.length" class="answers-section">
        <h3 class="answers-title">Podsumowanie odpowiedzi</h3>
        <div
          v-for="(a, i) in detailedAnswers"
          :key="i"
          class="answer-card"
          :class="{ correct: a.isCorrect, wrong: !a.isCorrect && !a.wasSkipped, skipped: a.wasSkipped }"
        >
          <div class="answer-header">
            <span class="q-num">{{ i + 1 }}.</span>
            <span class="q-status">
              {{ a.isCorrect ? '✓' : a.wasSkipped ? '—' : '✗' }}
            </span>
          </div>
          <p class="q-text">{{ a.text }}</p>
          <ul class="options-list">
            <li
              v-for="(opt, idx) in a.options"
              :key="idx"
              :class="{
                'opt-correct': idx === a.correctIdx,
                'opt-wrong': idx === a.userIdx && !a.isCorrect && !a.wasSkipped,
                'opt-user': idx === a.userIdx,
              }"
            >
              <span class="opt-letter">{{ ['A','B','C','D'][idx] }}</span>
              {{ opt }}
              <span v-if="idx === a.correctIdx" class="opt-mark correct-mark">✓ poprawna</span>
              <span v-else-if="idx === a.userIdx && !a.isCorrect" class="opt-mark wrong-mark">✗ twoja</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="actions">
        <router-link :to="`/courses/${route.params.id}/learn`" class="btn-primary">
          ← Wróć do kursu
        </router-link>
        <router-link v-if="!passed" :to="`/courses/${route.params.id}/quiz/${route.params.quizId}`" class="btn-ghost">
          🔄 Spróbuj ponownie
        </router-link>
        <router-link v-if="passed" to="/achievements" class="btn-ghost">
          🏆 Moje odznaki
        </router-link>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; display: flex; align-items: flex-start; justify-content: center; padding: 90px 20px 60px; }
.result-card { width: 100%; max-width: 600px; background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 2rem; padding: 3rem 2.5rem; text-align: center; }
.result-icon { font-size: 3.5rem; margin-bottom: 0.75rem; }
h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 2rem; }

.score-circle {
  width: 160px; height: 160px;
  background: conic-gradient(var(--color) var(--pct), rgba(255,255,255,0.07) var(--pct));
  border-radius: 50%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  margin: 0 auto 2rem;
  position: relative;
  &::before { content: ''; position: absolute; inset: 12px; background: #0f172a; border-radius: 50%; }
  .score-number { position: relative; font-size: 2rem; font-weight: 900; color: white; }
  .score-label { position: relative; font-size: 0.72rem; color: #64748b; }
}

.xp-earned {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25);
  color: #f59e0b; padding: 0.5rem 1.25rem; border-radius: 2rem;
  font-weight: 700; font-size: 0.95rem; margin-bottom: 2rem;
  .xp-icon { font-size: 1.1rem; }
}

.loading-note { color: #64748b; font-size: 0.85rem; margin-bottom: 2rem; }

.answers-section { text-align: left; margin-bottom: 2rem; }
.answers-title { font-size: 0.9rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 1rem; }

.answer-card {
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 1rem; padding: 1rem 1.25rem; margin-bottom: 0.75rem;
  &.correct  { border-color: rgba(16,185,129,0.25); background: rgba(16,185,129,0.04); }
  &.wrong    { border-color: rgba(239,68,68,0.25);  background: rgba(239,68,68,0.04); }
  &.skipped  { border-color: rgba(100,116,139,0.2); }
}
.answer-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.q-num    { font-size: 0.75rem; color: #64748b; font-weight: 700; }
.q-status { font-size: 0.9rem; font-weight: 800;
  .correct & { color: #10b981; }
  .wrong &   { color: #ef4444; }
  .skipped & { color: #64748b; }
}
.q-text   { font-size: 0.88rem; color: #e2e8f0; margin: 0 0 0.75rem; line-height: 1.5; }

.options-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.options-list li {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem; color: #94a3b8; padding: 0.35rem 0.6rem; border-radius: 0.5rem;
  &.opt-correct { color: #10b981; background: rgba(16,185,129,0.08); font-weight: 600; }
  &.opt-wrong   { color: #ef4444; background: rgba(239,68,68,0.08); font-weight: 600; }
}
.opt-letter { font-size: 0.7rem; font-weight: 800; color: #475569; min-width: 1rem; }
.opt-mark   { margin-left: auto; font-size: 0.7rem; font-weight: 700; white-space: nowrap; }
.correct-mark { color: #10b981; }
.wrong-mark   { color: #ef4444; }

.actions { display: flex; flex-direction: column; gap: 0.75rem; }
.btn-primary { display: block; padding: 0.9rem; background: #3b82f6; color: white; text-decoration: none; border-radius: 0.8rem; font-weight: 700; transition: 0.2s; &:hover { background: #2563eb; } }
.btn-ghost { display: block; padding: 0.8rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; text-decoration: none; border-radius: 0.8rem; font-weight: 600; font-size: 0.9rem; transition: 0.2s; &:hover { border-color: rgba(255,255,255,0.15); color: white; } }
</style>
