<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDbStore } from '@/stores/db'
import { api } from '@/api'

const route  = useRoute()
const router = useRouter()
const db     = useDbStore()

const courseId = route.params.id
const quizId   = route.params.quizId

// quiz data — will be populated from API, falls back to mock store
const apiQuiz = ref(null)
const mockQuiz = computed(() => db.getQuizById(quizId))

// Normalize API quiz to internal format
function normalizeApiQuiz(data) {
  return {
    id: data.id,
    title: data.title,
    timePerQuestion: data.time_limit_seconds ? Math.ceil(data.time_limit_seconds / (data.questions?.length || 1)) : 30,
    questions: (data.questions ?? []).map(q => ({
      id: q.id,
      text: q.text,
      options: q.options.map(o => o.text),
      _optionIds: q.options.map(o => o.id),
      correct: null,
    })),
  }
}

const quiz = computed(() => apiQuiz.value ?? mockQuiz.value)
const questions = computed(() => quiz.value?.questions ?? [])
const timePerQuestion = computed(() => quiz.value?.timePerQuestion ?? 30)

const currentIndex   = ref(0)
const selectedAnswer = ref(null)
const answers        = ref([])
const answered       = ref(false)
const timeLeft       = ref(timePerQuestion.value)
const submitting     = ref(false)

const current         = computed(() => questions.value[currentIndex.value])
const totalQuestions  = computed(() => questions.value.length)
const progressPercent = computed(() => (currentIndex.value / Math.max(totalQuestions.value, 1)) * 100)

onMounted(async () => {
  try {
    const { data } = await api.get(`/courses/${courseId}/quizzes/${quizId}/`)
    apiQuiz.value = normalizeApiQuiz(data)
    timeLeft.value = apiQuiz.value.timePerQuestion
  } catch (_) {
    timeLeft.value = timePerQuestion.value
  }
})

let timer = setInterval(() => {
  if (timeLeft.value > 0 && !answered.value) timeLeft.value--
  else if (timeLeft.value === 0 && !answered.value) selectAnswer(null)
}, 1000)
onUnmounted(() => clearInterval(timer))

const selectAnswer = (idx) => {
  if (answered.value) return
  selectedAnswer.value = idx
  answered.value = true
  answers.value.push({
    questionId: current.value.id,
    selected: idx,
    correct: current.value.correct,
    optionId: current.value._optionIds?.[idx] ?? null,
  })
}

const next = async () => {
  if (currentIndex.value < totalQuestions.value - 1) {
    currentIndex.value++
    selectedAnswer.value = null
    answered.value = false
    timeLeft.value = timePerQuestion.value
  } else {
    submitting.value = true
    try {
      const payload = {}
      answers.value.forEach(a => {
        if (a.optionId) payload[a.questionId] = a.optionId
      })
      const { data } = await api.post(`/courses/${courseId}/quizzes/${quizId}/submit/`, { answers: payload })
      router.push({
        path: `/courses/${courseId}/quiz/${quizId}/result`,
        query: { score: data.score, total: data.max_score, xp: data.xp_earned, passed: data.passed ? '1' : '0' },
        state: {
          userAnswers: answers.value,
          questions: questions.value,
          correctAnswers: data.correct_answers ?? {},
        },
      })
    } catch (_) {
      const score = answers.value.filter(a => a.selected !== null && a.selected === a.correct).length
      router.push({
        path: `/courses/${courseId}/quiz/${quizId}/result`,
        query: { score, total: totalQuestions.value },
        state: { userAnswers: answers.value, questions: questions.value, correctAnswers: {} },
      })
    } finally {
      submitting.value = false
    }
  }
}

const isCorrect = (idx) => answered.value && current.value.correct !== null && idx === current.value.correct
const isWrong   = (idx) => answered.value && idx === selectedAnswer.value && current.value.correct !== null && idx !== current.value.correct
</script>

<template>
  <div class="quiz-wrapper">
    <div class="quiz-container">

      <!-- Nagłówek quizu -->
      <div class="quiz-header">
        <router-link :to="`/courses/${route.params.id}/learn`" class="exit-link">✕ Wyjdź</router-link>
        <div class="quiz-progress-bar">
          <div class="quiz-progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <div class="timer" :class="{ urgent: timeLeft <= 10 }">
          ⏱ {{ timeLeft }}s
        </div>
      </div>

      <!-- Brak quizu -->
      <div v-if="!quiz" class="not-found-card">
        <p>Nie znaleziono quizu. <router-link :to="`/courses/${route.params.id}/learn`">Wróć do kursu</router-link></p>
      </div>

      <!-- Pytanie -->
      <template v-else-if="current">
        <div class="question-card">
          <div class="question-meta">
            {{ quiz.title }} · Pytanie {{ currentIndex + 1 }} z {{ totalQuestions }}
          </div>
          <h2>{{ current.text }}</h2>

          <!-- Odpowiedzi -->
          <div class="options-grid">
            <button
              v-for="(opt, idx) in current.options"
              :key="idx"
              class="option-btn"
              :class="{
                selected: selectedAnswer === idx && !answered,
                correct: isCorrect(idx),
                wrong: isWrong(idx),
                disabled: answered && idx !== current.correct && idx !== selectedAnswer
              }"
              :disabled="answered"
              @click="selectAnswer(idx)"
            >
              <span class="opt-letter">{{ ['A', 'B', 'C', 'D'][idx] }}</span>
              <span class="opt-text">{{ opt }}</span>
              <span v-if="isCorrect(idx)" class="opt-result">✓</span>
              <span v-if="isWrong(idx)" class="opt-result">✗</span>
            </button>
          </div>

          <!-- Feedback po odpowiedzi — poprawna odpowiedź znana tylko po submisji -->
          <div v-if="answered" class="answer-feedback neutral">
            <strong>Odpowiedź zarejestrowana</strong>
            <p>Wyniki zobaczysz po zakończeniu quizu.</p>
          </div>
        </div>

        <button v-if="answered" class="btn-next" @click="next">
          {{ currentIndex < totalQuestions - 1 ? 'Następne pytanie →' : 'Zakończ quiz →' }}
        </button>
      </template>

    </div>
  </div>
</template>

<style scoped lang="scss">
.quiz-wrapper { background: #020617; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 90px 20px 40px; }
.quiz-container { width: 100%; max-width: 720px; }

.quiz-header {
  display: flex; align-items: center; gap: 1rem; margin-bottom: 2.5rem;
  .exit-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; white-space: nowrap; &:hover { color: #ef4444; } }
  .quiz-progress-bar { flex: 1; height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
  .quiz-progress-fill { height: 100%; background: #3b82f6; border-radius: 3px; transition: width 0.3s ease; }
  .timer { font-size: 0.88rem; font-weight: 800; color: #94a3b8; white-space: nowrap; &.urgent { color: #ef4444; } }
}

.question-card {
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 1.5rem;
  padding: 2.5rem;
  margin-bottom: 1.5rem;
}
.question-meta { font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
h2 { font-size: 1.25rem; font-weight: 700; color: white; line-height: 1.5; margin: 0 0 2rem; }

.options-grid { display: flex; flex-direction: column; gap: 0.75rem; }
.option-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 0.85rem;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
  font-size: 0.93rem;

  &:hover:not(:disabled) { border-color: #3b82f6; background: rgba(59,130,246,0.08); }
  &.correct { border-color: #10b981; background: rgba(16,185,129,0.1); color: #10b981; }
  &.wrong { border-color: #ef4444; background: rgba(239,68,68,0.1); color: #ef4444; }
  &.disabled { opacity: 0.4; cursor: not-allowed; }
  &:disabled { cursor: not-allowed; }

  .opt-letter { width: 28px; height: 28px; background: rgba(255,255,255,0.07); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 800; flex-shrink: 0; }
  .opt-text { flex: 1; }
  .opt-result { flex-shrink: 0; font-weight: 800; }
}

.answer-feedback {
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  border-radius: 0.85rem;
  font-size: 0.9rem;
  &.correct { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); strong { color: #10b981; } p { color: #64748b; margin: 0.3rem 0 0; font-size: 0.85rem; } }
  &.wrong { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); strong { color: #ef4444; } p { color: #64748b; margin: 0.3rem 0 0; font-size: 0.85rem; } }
  &.neutral { background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.18); strong { color: #60a5fa; } p { color: #64748b; margin: 0.3rem 0 0; font-size: 0.85rem; } }
}

.btn-next { width: 100%; padding: 1rem; background: #3b82f6; color: white; border: none; border-radius: 0.9rem; font-size: 1rem; font-weight: 700; cursor: pointer; transition: 0.2s; &:hover { background: #2563eb; transform: translateY(-1px); } }
.not-found-card { text-align: center; padding: 3rem; color: #64748b; a { color: #3b82f6; text-decoration: none; } }
</style>