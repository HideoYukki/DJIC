import { defineStore } from 'pinia'
import { api } from '@/api'

export const useDbStore = defineStore('db', {
  state: () => ({
    courses:          [],
    materials:        {},
    quizzes:          {},
    enrollments:      [],
    progress:         [],
    achievements:     [],
    userAchievements: [],
  }),

  getters: {
    allCourses: (state) => state.courses,

    getCourseById: (state) => (id) =>
      state.courses.find(c => c.id === String(id)) ?? null,

    getCourseMaterials: (state) => (courseId) =>
      state.materials[String(courseId)] ?? [],

    getMaterialById: (state) => (courseId, materialId) =>
      (state.materials[String(courseId)] ?? []).find(m => m.id === String(materialId)) ?? null,

    getCourseChapters: (state) => (courseId) => {
      const mats = state.materials[String(courseId)] ?? []
      const chapters = {}
      mats.forEach(m => {
        if (!chapters[m.chapterId]) chapters[m.chapterId] = { id: m.chapterId, title: m.chapter, materials: [] }
        chapters[m.chapterId].materials.push(m)
      })
      return Object.values(chapters)
    },

    getQuizById: (state) => (quizId) =>
      state.quizzes[String(quizId)] ?? null,

    getEnrolledCourses: (state) => (userId) => {
      const enrolled = state.enrollments.filter(e => e.userId === userId).map(e => e.courseId)
      return state.courses.filter(c => enrolled.includes(c.id))
    },

    isEnrolled: (state) => (userId, courseId) =>
      state.enrollments.some(e => e.userId === userId && e.courseId === String(courseId)),

    getCompletedMaterials: (state) => (userId, courseId) =>
      state.progress.filter(p => p.userId === userId && p.courseId === String(courseId)).map(p => p.materialId),

    getCourseProgress: (state) => (userId, courseId) => {
      const total = (state.materials[String(courseId)] ?? []).length
      if (total === 0) return 0
      const done = state.progress.filter(p => p.userId === userId && p.courseId === String(courseId)).length
      return Math.round((done / total) * 100)
    },

    isMaterialCompleted: (state) => (userId, materialId) =>
      state.progress.some(p => p.userId === userId && p.materialId === String(materialId)),

    getUserAchievements: (state) => (userId) => {
      const unlocked = state.userAchievements.filter(ua => ua.userId === userId).map(ua => ua.achievementId)
      return state.achievements.map(a => ({ ...a, unlocked: unlocked.includes(a.id) }))
    },

    getTotalXP: (state) => (userId) => {
      const unlocked = state.userAchievements.filter(ua => ua.userId === userId).map(ua => ua.achievementId)
      return state.achievements.filter(a => unlocked.includes(a.id)).reduce((sum, a) => sum + a.xp, 0)
    },
  },

  actions: {
    async fetchCourses(params = {}) {
      try {
        const { data } = await api.get('/courses/', { params })
        if (data.results?.length) this.courses = data.results.map(_normalizeCourse)
      } catch (_) {}
    },

    async fetchCourseDetail(courseId) {
      try {
        const { data } = await api.get(`/courses/${courseId}/`)
        const idx = this.courses.findIndex(c => String(c.id) === String(courseId))
        const normalized = _normalizeCourse(data)
        if (idx >= 0) this.courses[idx] = normalized
        else this.courses.push(normalized)
        if (data.materials?.length) this.materials[String(courseId)] = data.materials.map(_normalizeMaterial)
        return normalized
      } catch (_) {
        return this.getCourseById(courseId)
      }
    },

    async fetchMaterials(courseId) {
      try {
        const { data } = await api.get(`/courses/${courseId}/materials/`)
        this.materials[String(courseId)] = (Array.isArray(data) ? data : data.results ?? []).map(_normalizeMaterial)
      } catch (_) {}
    },

    async fetchEnrollments(userId) {
      try {
        const { data } = await api.get('/enrollments/')
        const results = data.results ?? []
        this.enrollments = results.map(e => ({
          userId,
          courseId: String(e.course_id),
          enrolledAt: e.enrolled_at?.slice(0, 10) ?? '',
        }))
        // Backend embeds full course object in each enrollment — populate courses cache
        const missingMaterialIds = []
        for (const e of results) {
          if (e.course) {
            const normalized = _normalizeCourse(e.course)
            const idx = this.courses.findIndex(c => c.id === normalized.id)
            if (idx >= 0) this.courses[idx] = normalized
            else this.courses.push(normalized)
          }
          // Load materials for courses not yet in cache (needed for progress %)
          if (!this.materials[String(e.course_id)]) {
            missingMaterialIds.push(String(e.course_id))
          }
        }
        if (missingMaterialIds.length) {
          await Promise.all(missingMaterialIds.map(id => this.fetchMaterials(id)))
        }
      } catch (_) {}
    },

    async fetchProgress(userId) {
      try {
        const { data } = await api.get('/progress/')
        const records = data.results ?? []
        this.progress = records.flatMap(p =>
          (p.completed_material_ids ?? []).map(mid => ({
            userId,
            materialId: String(mid),
            courseId: String(p.course_id),
            completedAt: p.last_activity_at ?? '',
          }))
        )
      } catch (_) {}
    },

    async fetchAchievements(userId) {
      try {
        const { data } = await api.get('/achievements/')
        if (data.results?.length) {
          this.achievements = data.results.map(a => ({
            id:          a.badge_id,
            name:        a.badge_name ?? '',
            icon:        '🏆',
            xp:          a.xp_value ?? 0,
            description: a.badge_description ?? '',
          }))
          this.userAchievements = data.results
            .filter(a => a.earned_at)
            .map(a => ({
              userId,
              achievementId: a.badge_id,
              unlockedAt:    a.earned_at?.slice(0, 10) ?? '',
            }))
        }
      } catch (_) {}
    },

    async enroll(userId, courseId) {
      if (this.isEnrolled(userId, courseId)) return
      await api.post('/enrollments/', { course_id: String(courseId) })
      this.enrollments.push({ userId, courseId: String(courseId), enrolledAt: new Date().toISOString().slice(0, 10) })
      const course = this.getCourseById(courseId)
      if (course) course.studentsCount = (course.studentsCount ?? 0) + 1
    },

    async unenroll(userId, courseId) {
      await api.delete(`/enrollments/${courseId}/`)
      this.enrollments = this.enrollments.filter(e => !(e.userId === userId && e.courseId === String(courseId)))
    },

    async completeMaterial(userId, courseId, materialId) {
      if (this.isMaterialCompleted(userId, materialId)) return
      await api.post(`/progress/${courseId}/complete/`, { material_id: String(materialId) })
      this.progress.push({ userId, courseId: String(courseId), materialId: String(materialId), completedAt: new Date().toISOString() })
    },
  },
})

function _normalizeCourse(c) {
  return {
    id:              String(c.id),
    title:           c.title ?? '',
    description:     c.description ?? '',
    longDescription: c.description ?? '',
    author:          c.creator_name ?? c.creator_id ?? '',
    authorId:        String(c.creator_id ?? ''),
    level:           _levelLabel(c.level),
    category:        c.category ?? '',
    tags:            c.tags ?? [],
    chaptersCount:   0,
    studentsCount:   c.students_count ?? 0,
    rating:          c.rating ?? 0,
    duration:        c.duration_minutes ? `${c.duration_minutes}min` : '',
    status:          c.status ?? 'ACTIVE',
    thumbnail:       c.thumbnail_url ?? null,
  }
}

function _normalizeMaterial(m) {
  return {
    id:        String(m.id),
    courseId:  String(m.course_id),
    chapterId: m.chapter_id ? String(m.chapter_id) : 'ch1',
    chapter:   m.chapter_title ?? 'Rozdział 1',
    type:      m.type ?? 'VIDEO',
    title:     m.title ?? '',
    duration:  m.duration_seconds ? `${Math.round(m.duration_seconds / 60)}min` : '',
    order:     m.order ?? 0,
    videoUrl:  m.type === 'VIDEO' ? m.content : undefined,
    content:   m.type === 'TEXT'  ? m.content : undefined,
    quizId:    m.type === 'QUIZ'  ? m.content : undefined,
  }
}

function _levelLabel(level) {
  const map = { BEGINNER: 'Początkujący', INTERMEDIATE: 'Średniozaawansowany', ADVANCED: 'Zaawansowany' }
  return map[level] ?? level ?? 'Początkujący'
}
