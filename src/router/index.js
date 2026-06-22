import { createRouter, createWebHistory } from 'vue-router'

// Widoki publiczne
import LandingPage from '../views/public/LandingPage.vue'
import LoginPage from '../views/public/LoginPage.vue'
import RegisterPage from '../views/public/RegisterPage.vue'
import ForgotPasswordPage from '../views/public/ForgotPasswordPage.vue'
import ResetPasswordPage from '../views/public/ResetPasswordPage.vue'
import CourseCatalogPage from '../views/public/CourseCatalogPage.vue'
import CourseDetailPage from '../views/public/CourseDetailPage.vue'

// Widoki ucznia
import StudentDashboard from '../views/student/StudentDashboard.vue'
import MyCoursesPage from '../views/student/MyCoursesPage.vue'
import CoursePlayerPage from '../views/student/CoursePlayerPage.vue'
import LessonPage from '../views/student/LessonPage.vue'
import QuizPage from '../views/student/QuizPage.vue'
import QuizResultPage from '../views/student/QuizResultPage.vue'
import CertificatePage from '../views/student/CertificatePage.vue'
import ProgressPage from '../views/student/ProgressPage.vue'
import ProfilePage from '../views/student/ProfilePage.vue'
import AchievementsPage from '../views/student/AchievementsPage.vue'
import NotificationsPage from '../views/student/NotificationsPage.vue'

// Widoki twórcy kursu
import CreatorDashboard from '../views/creator/CreatorDashboard.vue'
import CreatorCoursesPage from '../views/creator/CreatorCoursesPage.vue'
import NewCoursePage from '../views/creator/NewCoursePage.vue'
import EditCoursePage from '../views/creator/EditCoursePage.vue'
import CourseMaterialsPage from '../views/creator/CourseMaterialsPage.vue'
import NewMaterialPage from '../views/creator/NewMaterialPage.vue'
import EditMaterialPage from '../views/creator/EditMaterialPage.vue'
import QuizBuilderPage from '../views/creator/QuizBuilderPage.vue'
import PublishCoursePage from '../views/creator/PublishCoursePage.vue'
import CourseAnalyticsPage from '../views/creator/CourseAnalyticsPage.vue'
import CourseStudentsPage from '../views/creator/CourseStudentsPage.vue'
import CreatorReportsPage from '../views/creator/CreatorReportsPage.vue'
import CourseReportPage from '../views/creator/CourseReportPage.vue'

// Widoki administratora
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import UserManagementPage from '../views/admin/UserManagementPage.vue'
import UserDetailPage from '../views/admin/UserDetailPage.vue'
import NewUserPage from '../views/admin/NewUserPage.vue'
import AdminCoursesPage from '../views/admin/AdminCoursesPage.vue'
import CourseReviewPage from '../views/admin/CourseReviewPage.vue'
import AdminSettingsPage from '../views/admin/AdminSettingsPage.vue'
import SystemLogsPage from '../views/admin/SystemLogsPage.vue'

// Widoki pomocnicze
import NotFoundPage from '../views/utility/NotFoundPage.vue'
import UnauthorizedPage from '../views/utility/UnauthorizedPage.vue'
import MaintenancePage from '../views/utility/MaintenancePage.vue'

const routes = [
  // --- PUBLICZNE ---
  { path: '/',                               name: 'Home',           component: LandingPage },
  { path: '/login',                          name: 'Login',          component: LoginPage },
  { path: '/register',                       name: 'Register',       component: RegisterPage },
  { path: '/forgot-password',                name: 'ForgotPassword', component: ForgotPasswordPage },
  { path: '/reset-password/:token',          name: 'ResetPassword',  component: ResetPasswordPage },
  { path: '/courses',                        name: 'Catalog',        component: CourseCatalogPage },
  { path: '/courses/:id',                    name: 'CourseDetail',   component: CourseDetailPage },

  // --- UCZEŃ ---
  { path: '/dashboard',                      name: 'Dashboard',      component: StudentDashboard,  meta: { requiresAuth: true } },
  { path: '/my-courses',                     name: 'MyCourses',      component: MyCoursesPage,     meta: { requiresAuth: true } },
  { path: '/courses/:id/learn',              name: 'CoursePlayer',   component: CoursePlayerPage,  meta: { requiresAuth: true } },
  { path: '/courses/:id/learn/:materialId',  name: 'Lesson',         component: LessonPage,        meta: { requiresAuth: true } },
  { path: '/courses/:id/quiz/:quizId',       name: 'Quiz',           component: QuizPage,          meta: { requiresAuth: true } },
  { path: '/courses/:id/quiz/:quizId/result', name: 'QuizResult',    component: QuizResultPage,    meta: { requiresAuth: true } },
  { path: '/courses/:id/certificate',        name: 'Certificate',    component: CertificatePage,   meta: { requiresAuth: true } },
  { path: '/progress',                       name: 'Progress',       component: ProgressPage,      meta: { requiresAuth: true } },
  { path: '/profile',                        name: 'Profile',        component: ProfilePage,       meta: { requiresAuth: true } },
  { path: '/achievements',                   name: 'Achievements',   component: AchievementsPage,  meta: { requiresAuth: true } },
  { path: '/notifications',                  name: 'Notifications',  component: NotificationsPage, meta: { requiresAuth: true } },

  // --- TWÓRCA ---
  { path: '/creator/dashboard',              name: 'CreatorDashboard',  component: CreatorDashboard,    meta: { requiresCreator: true } },
  { path: '/creator/courses',                name: 'CreatorCourses',    component: CreatorCoursesPage,  meta: { requiresCreator: true } },
  { path: '/creator/courses/new',            name: 'NewCourse',         component: NewCoursePage,       meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/edit',       name: 'EditCourse',        component: EditCoursePage,      meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/materials',  name: 'CourseMaterials',   component: CourseMaterialsPage, meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/materials/new',                name: 'NewMaterial',    component: NewMaterialPage,     meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/materials/:materialId/edit',   name: 'EditMaterial',   component: EditMaterialPage,    meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/quiz/:quizId/builder', name: 'QuizBuilder', component: QuizBuilderPage, meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/publish',    name: 'PublishCourse',     component: PublishCoursePage,   meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/analytics',  name: 'CourseAnalytics',   component: CourseAnalyticsPage, meta: { requiresCreator: true } },
  { path: '/creator/courses/:id/students',   name: 'CourseStudents',    component: CourseStudentsPage,  meta: { requiresCreator: true } },
  { path: '/creator/reports',                name: 'CreatorReports',    component: CreatorReportsPage,  meta: { requiresCreator: true } },
  { path: '/creator/reports/:courseId',      name: 'CourseReport',      component: CourseReportPage,    meta: { requiresCreator: true } },

  // --- ADMINISTRATOR ---
  { path: '/admin/dashboard',                name: 'AdminDashboard',  component: AdminDashboard,     meta: { requiresAdmin: true } },
  { path: '/admin/users',                    name: 'UserManagement',  component: UserManagementPage, meta: { requiresAdmin: true } },
  { path: '/admin/users/new',                name: 'NewUser',         component: NewUserPage,        meta: { requiresAdmin: true } },
  { path: '/admin/users/:id',                name: 'UserDetail',      component: UserDetailPage,     meta: { requiresAdmin: true } },
  { path: '/admin/courses',                  name: 'AdminCourses',    component: AdminCoursesPage,   meta: { requiresAdmin: true } },
  { path: '/admin/courses/:id/review',       name: 'CourseReview',    component: CourseReviewPage,   meta: { requiresAdmin: true } },
  { path: '/admin/settings',                 name: 'AdminSettings',   component: AdminSettingsPage,  meta: { requiresAdmin: true } },
  { path: '/admin/logs',                     name: 'SystemLogs',      component: SystemLogsPage,     meta: { requiresAdmin: true } },

  // --- POMOCNICZE ---
  { path: '/unauthorized',       name: 'Unauthorized', component: UnauthorizedPage },
  { path: '/maintenance',        name: 'Maintenance',  component: MaintenancePage },
  { path: '/:pathMatch(.*)*',    name: 'NotFound',     component: NotFoundPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Guard autentykacji — tymczasowy (sessionStorage), zastąpić JWT gdy backend będzie gotowy
router.beforeEach((to, from, next) => {
  const user = JSON.parse(sessionStorage.getItem('djic_user') || 'null')
  const role = user?.role ?? null

  if (to.meta.requiresAdmin && role !== 'ADMIN') {
    return next(user ? '/unauthorized' : '/login')
  }
  if (to.meta.requiresCreator && role !== 'CREATOR' && role !== 'ADMIN') {
    return next(user ? '/unauthorized' : '/login')
  }
  if (to.meta.requiresAuth && !user) {
    return next('/login')
  }

  next()
})

export default router
