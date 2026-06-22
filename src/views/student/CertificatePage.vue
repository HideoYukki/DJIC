<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const route = useRoute()
const auth  = useAuthStore()
const db    = useDbStore()

const courseId = route.params.id

const certificate = ref({
  studentName:    auth.userName || '',
  courseTitle:    db.getCourseById(courseId)?.title ?? '',
  completionDate: new Date().toISOString().slice(0, 10),
  grade:          'Zaliczono',
  certificateId:  `DJIC-${courseId}-${Date.now().toString(36).toUpperCase()}`,
  instructor:     '',
})

onMounted(async () => {
  const course = await db.fetchCourseDetail(courseId)
  if (course) {
    certificate.value.courseTitle = course.title
    certificate.value.instructor  = course.author ?? ''
  }
})

const print = () => window.print()
</script>

<template>
  <div class="cert-page">
    <div class="container">
      <div class="actions-bar no-print">
        <router-link :to="`/courses/${route.params.id}/learn`" class="btn-back">← Wróć do kursu</router-link>
        <button class="btn-download" @click="print">🖨️ Pobierz / Drukuj</button>
      </div>

      <!-- Certyfikat -->
      <div class="certificate">
        <div class="cert-border">
          <div class="cert-header">
            <div class="cert-logo">🎓 DJIC<span>Platform</span></div>
            <h2 class="cert-subtitle">Certyfikat Ukończenia</h2>
          </div>

          <div class="cert-body">
            <p class="cert-text-intro">Niniejszym zaświadcza się, że</p>
            <h1 class="cert-student-name">{{ certificate.studentName }}</h1>
            <p class="cert-text-mid">ukończył(a) z sukcesem kurs</p>
            <h2 class="cert-course-title">{{ certificate.courseTitle }}</h2>

            <div class="cert-grade">
              <span class="grade-label">Ocena końcowa</span>
              <span class="grade-value">{{ certificate.grade }}</span>
            </div>
          </div>

          <div class="cert-footer">
            <div class="cert-sig">
              <div class="sig-line"></div>
              <p>{{ certificate.instructor }}</p>
              <small>Instruktor kursu</small>
            </div>
            <div class="cert-meta">
              <p>Data ukończenia: <strong>{{ certificate.completionDate }}</strong></p>
              <p class="cert-id">ID: {{ certificate.certificateId }}</p>
            </div>
            <div class="cert-seal">🏅</div>
          </div>
        </div>
      </div>

      <!-- Info o udostępnieniu -->
      <!-- TODO: Integracja z zewnętrznym serwisem certyfikatów lub wygenerowanie PDF przez backend -->
      <div class="share-section no-print">
        <h3>Udostępnij swój certyfikat</h3>
        <div class="share-btns">
          <button class="share-btn linkedin">🔗 Dodaj do LinkedIn</button>
          <button class="share-btn copy">📋 Kopiuj link</button>
        </div>
        <p class="share-note">Certyfikat możesz zweryfikować pod adresem: <code>djic.edu.pl/verify/{{ certificate.certificateId }}</code></p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.cert-page { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 900px; margin: 0 auto; }

.actions-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.btn-back { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; transition: 0.2s; &:hover { color: #94a3b8; } }
.btn-download { padding: 0.65rem 1.4rem; background: #3b82f6; color: white; border: none; border-radius: 0.7rem; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: 0.2s; &:hover { background: #2563eb; } }

.certificate {
  background: white;
  border-radius: 1.5rem;
  padding: 0.75rem;
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
  margin-bottom: 2.5rem;
}
.cert-border {
  border: 3px solid #c7a04a;
  border-radius: 1rem;
  padding: 3.5rem;
  background: linear-gradient(135deg, #fefef8, #fff);
}
.cert-header {
  text-align: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e8d5a3;
  padding-bottom: 1.5rem;
  .cert-logo { font-size: 1.4rem; font-weight: 900; color: #1e293b; span { color: #3b82f6; } margin-bottom: 0.5rem; }
  .cert-subtitle { font-size: 0.85rem; color: #64748b; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; margin: 0; }
}
.cert-body { text-align: center; margin-bottom: 3rem; }
.cert-text-intro { color: #64748b; font-size: 1rem; margin-bottom: 0.75rem; }
.cert-student-name { font-size: 3rem; font-weight: 900; color: #0f172a; margin: 0 0 1rem; font-family: Georgia, serif; }
.cert-text-mid { color: #64748b; font-size: 1rem; margin-bottom: 0.75rem; }
.cert-course-title { font-size: 1.6rem; font-weight: 800; color: #1e3a5f; margin: 0 0 2rem; line-height: 1.3; }
.cert-grade {
  display: inline-flex; flex-direction: column; align-items: center;
  background: linear-gradient(135deg, #c7a04a, #e8c96d);
  padding: 0.75rem 2.5rem; border-radius: 0.75rem;
  .grade-label { font-size: 0.7rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; }
  .grade-value { font-size: 1.1rem; font-weight: 800; color: white; }
}
.cert-footer {
  display: flex; justify-content: space-between; align-items: flex-end;
  border-top: 2px solid #e8d5a3; padding-top: 1.5rem;
}
.cert-sig {
  text-align: center;
  .sig-line { width: 160px; height: 1px; background: #0f172a; margin-bottom: 0.5rem; }
  p { color: #1e293b; font-weight: 700; margin: 0; font-size: 0.9rem; }
  small { color: #64748b; font-size: 0.75rem; }
}
.cert-meta { text-align: center; p { color: #64748b; font-size: 0.82rem; margin: 0 0 0.25rem; strong { color: #1e293b; } } .cert-id { font-size: 0.72rem; font-family: monospace; } }
.cert-seal { font-size: 3.5rem; }

.share-section {
  text-align: center;
  h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; }
  .share-btns { display: flex; gap: 0.75rem; justify-content: center; margin-bottom: 1rem; }
  .share-btn { padding: 0.65rem 1.4rem; border-radius: 0.65rem; font-weight: 700; font-size: 0.85rem; cursor: pointer; border: none; transition: 0.2s; &.linkedin { background: #0077b5; color: white; &:hover { background: #005885; } } &.copy { background: rgba(255,255,255,0.07); color: #94a3b8; border: 1px solid rgba(255,255,255,0.1); &:hover { background: rgba(255,255,255,0.12); } } }
  .share-note { color: #475569; font-size: 0.8rem; code { color: #3b82f6; background: rgba(59,130,246,0.1); padding: 0.15rem 0.4rem; border-radius: 0.3rem; } }
}

@media print {
  .no-print { display: none !important; }
  .cert-page { padding: 0; background: white; }
  .certificate { box-shadow: none; }
}
</style>