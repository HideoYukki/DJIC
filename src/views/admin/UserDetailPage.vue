<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()

const user = ref({
  id: route.params.id,
  name: '',
  email: '',
  role: 'STUDENT',
  active: true,
  joined: '',
  lastLogin: '',
  courses: 0,
  bio: '',
})

const roleOptions = ['STUDENT', 'CREATOR', 'ADMIN']
const selectedRole = ref('STUDENT')
const saving = ref(false)
const saved = ref(false)
const serverError = ref('')

const roleColors = { STUDENT: '#3b82f6', CREATOR: '#8b5cf6', ADMIN: '#ef4444' }
const roleColor = computed(() => roleColors[selectedRole.value] || '#64748b')

const activity    = ref([])
const deleting    = ref(false)
const deleteError = ref('')
const showConfirm = ref(false)

async function deleteUser() {
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/users/${route.params.id}/`)
    router.push('/admin/users')
  } catch (err) {
    deleteError.value = err.response?.data?.error ?? 'Błąd usuwania konta.'
    showConfirm.value = false
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/users/${route.params.id}/`)
    user.value = {
      id: data.id,
      name: data.name ?? '—',
      email: data.email ?? '—',
      role: data.role,
      active: data.is_active ?? true,
      joined: data.created_at?.slice(0, 10) ?? '—',
      lastLogin: data.last_login ? new Date(data.last_login).toLocaleString('pl-PL') : '—',
      courses: data.courses_count ?? 0,
      bio: data.bio ?? '',
    }
    selectedRole.value = data.role
  } catch (_) {}
})

async function saveChanges() {
  saving.value = true
  serverError.value = ''
  try {
    await api.patch(`/users/${route.params.id}/`, { role: selectedRole.value, is_active: user.value.active })
    user.value.role = selectedRole.value
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania.'
  } finally {
    saving.value = false
  }
}

async function toggleActive() {
  const newActive = !user.value.active
  try {
    await api.patch(`/users/${route.params.id}/`, { is_active: newActive })
    user.value.active = newActive
  } catch (_) { user.value.active = !newActive }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/users" class="back-link">← Zarządzanie użytkownikami</router-link>
        <div class="header-row">
          <h1>Szczegóły konta</h1>
          <span class="status-badge" :class="{ blocked: !user.active }">
            {{ user.active ? '✓ Aktywny' : '✗ Zablokowany' }}
          </span>
        </div>
      </div>

      <div class="two-col">
        <!-- Profil -->
        <div class="panel">
          <h2 class="panel-title">Profil użytkownika</h2>
          <div class="user-card">
            <div class="avatar" :style="{ background: `linear-gradient(135deg, ${roleColor}, #1e293b)` }">
              {{ user.name.charAt(0) }}
            </div>
            <div class="user-meta">
              <strong>{{ user.name }}</strong>
              <span>{{ user.email }}</span>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <label>Data rejestracji</label>
              <span>{{ user.joined }}</span>
            </div>
            <div class="info-item">
              <label>Ostatnie logowanie</label>
              <span>{{ user.lastLogin }}</span>
            </div>
            <div class="info-item">
              <label>Liczba kursów</label>
              <span>{{ user.courses }}</span>
            </div>
            <div class="info-item">
              <label>ID użytkownika</label>
              <span class="mono">#{{ user.id }}</span>
            </div>
          </div>

          <div v-if="user.bio" class="bio-block">
            <label>Bio</label>
            <p>{{ user.bio }}</p>
          </div>
        </div>

        <!-- Zarządzanie -->
        <div class="panel">
          <h2 class="panel-title">Zarządzanie kontem</h2>

          <div class="field-group">
            <label class="field-label">Rola użytkownika</label>
            <div class="role-buttons">
              <button
                v-for="r in roleOptions" :key="r"
                class="role-btn"
                :class="{ active: selectedRole === r }"
                :style="selectedRole === r ? { borderColor: roleColors[r], color: roleColors[r], background: roleColors[r] + '18' } : {}"
                @click="selectedRole = r">
                {{ r }}
              </button>
            </div>
          </div>

          <div class="field-group">
            <label class="field-label">Status konta</label>
            <div class="toggle-row">
              <span>{{ user.active ? 'Konto aktywne' : 'Konto zablokowane' }}</span>
              <button class="toggle-btn" :class="{ danger: user.active }" @click="toggleActive">
                {{ user.active ? 'Zablokuj konto' : 'Odblokuj konto' }}
              </button>
            </div>
          </div>

          <div class="action-row">
            <button class="btn-save" :disabled="saving" @click="saveChanges">
              {{ saving ? 'Zapisywanie…' : 'Zapisz zmiany' }}
            </button>
            <span v-if="saved" class="saved-msg">✓ Zapisano</span>
          </div>

          <div class="danger-zone">
            <h3>Strefa niebezpieczna</h3>
            <p v-if="deleteError" class="delete-error">{{ deleteError }}</p>
            <template v-if="!showConfirm">
              <button class="btn-delete" @click="showConfirm = true">Usuń konto permanentnie</button>
            </template>
            <template v-else>
              <p class="confirm-msg">Tej operacji nie można cofnąć. Czy na pewno usunąć konto <strong>{{ user.name }}</strong>?</p>
              <div class="confirm-btns">
                <button class="btn-cancel-sm" @click="showConfirm = false">Anuluj</button>
                <button class="btn-delete-confirm" :disabled="deleting" @click="deleteUser">
                  {{ deleting ? 'Usuwanie…' : 'Tak, usuń konto' }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Historia aktywności -->
      <div class="panel full-panel">
        <h2 class="panel-title">Historia aktywności</h2>
        <div class="activity-table">
          <div class="act-header">
            <span>Akcja</span>
            <span>Szczegóły</span>
            <span>Data i czas</span>
          </div>
          <div v-for="(a, i) in activity" :key="i" class="act-row">
            <span>{{ a.action }}</span>
            <span class="detail-cell">{{ a.detail }}</span>
            <span class="time-cell">{{ a.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; align-items: center; gap: 1rem; h1 { font-size: 2rem; font-weight: 800; margin: 0; } }
.status-badge { padding: 0.3rem 0.85rem; background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); border-radius: 999px; font-size: 0.75rem; font-weight: 700; &.blocked { background: rgba(239,68,68,0.1); color: #ef4444; border-color: rgba(239,68,68,0.25); } }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; @media (max-width: 768px) { grid-template-columns: 1fr; } }
.panel { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.5rem; }
.full-panel { margin-bottom: 0; }
.panel-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 1.25rem; color: #e2e8f0; }

.user-card { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; .avatar { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 900; flex-shrink: 0; } .user-meta { display: flex; flex-direction: column; strong { font-size: 1.05rem; font-weight: 800; } span { color: #64748b; font-size: 0.82rem; } } }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; margin-bottom: 1.25rem; }
.info-item { label { display: block; font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; } span { font-size: 0.87rem; } .mono { font-family: monospace; color: #94a3b8; } }

.bio-block { background: rgba(255,255,255,0.02); border-radius: 0.75rem; padding: 0.85rem; label { font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 0.4rem; } p { margin: 0; font-size: 0.85rem; color: #94a3b8; line-height: 1.6; } }

.field-group { margin-bottom: 1.5rem; }
.field-label { display: block; font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 0.65rem; }
.role-buttons { display: flex; gap: 0.5rem; }
.role-btn { padding: 0.5rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); color: #64748b; border-radius: 0.65rem; cursor: pointer; font-size: 0.82rem; font-weight: 700; transition: 0.15s; }

.toggle-row { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); border-radius: 0.75rem; padding: 0.75rem 1rem; span { font-size: 0.87rem; color: #94a3b8; } }
.toggle-btn { padding: 0.4rem 0.85rem; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: #f87171; border-radius: 0.55rem; cursor: pointer; font-size: 0.78rem; font-weight: 700; transition: 0.15s; &:hover { background: rgba(239,68,68,0.14); } &:not(.danger) { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.2); color: #34d399; } }

.action-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.75rem; }
.btn-save { padding: 0.7rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.saved-msg { color: #10b981; font-size: 0.85rem; font-weight: 600; }

.danger-zone { border-top: 1px solid rgba(239,68,68,0.15); padding-top: 1.25rem; h3 { font-size: 0.75rem; color: #ef4444; font-weight: 700; text-transform: uppercase; margin: 0 0 0.75rem; } }
.btn-delete { padding: 0.55rem 1.1rem; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: #f87171; border-radius: 0.65rem; cursor: pointer; font-size: 0.82rem; font-weight: 700; transition: 0.15s; &:hover { background: rgba(239,68,68,0.14); } }

.activity-table { }
.act-header { display: grid; grid-template-columns: 2fr 2fr 1.5fr; gap: 1rem; padding: 0.7rem 1rem; background: rgba(255,255,255,0.02); border-radius: 0.65rem; font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem; }
.act-row { display: grid; grid-template-columns: 2fr 2fr 1.5fr; gap: 1rem; padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.85rem; &:last-child { border-bottom: none; } .detail-cell { color: #94a3b8; } .time-cell { color: #64748b; font-size: 0.78rem; font-family: monospace; } }
</style>