<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'

const auth = useAuthStore()

const nameParts = computed(() => {
  const name = auth.user?.name ?? ''
  const [first = '', ...rest] = name.split(' ')
  return { first, last: rest.join(' ') }
})

const avatarUrl      = ref(auth.user?.avatar_url ?? null)
const avatarInput    = ref(null)
const uploadingAvatar = ref(false)
const avatarError    = ref('')

const triggerAvatarPick = () => avatarInput.value?.click()

const onAvatarSelected = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  uploadingAvatar.value = true
  avatarError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/users/me/avatar/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    avatarUrl.value = data.avatar_url
    await auth.fetchMe()
  } catch (err) {
    avatarError.value = err.response?.data?.error ?? 'Błąd uploadu.'
  } finally {
    uploadingAvatar.value = false
    e.target.value = ''
  }
}

const profile = reactive({ firstName: '', lastName: '', email: '', bio: '', role: '' })
const passwordForm = reactive({ current: '', newPass: '', confirm: '' })
const isSaving = ref(false)
const passwordError = ref('')
const passwordSaved = ref(false)
const saved = ref(false)
const serverError = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/users/me/')
    const [first = '', ...rest] = (data.name ?? '').split(' ')
    profile.firstName = first
    profile.lastName  = rest.join(' ')
    profile.email     = data.email ?? ''
    profile.bio       = data.bio ?? ''
    profile.role      = data.role ?? ''
  } catch (_) {
    profile.firstName = nameParts.value.first
    profile.lastName  = nameParts.value.last
    profile.email     = auth.user?.email ?? ''
    profile.role      = auth.user?.role ?? ''
  }
})

const saveProfile = async () => {
  isSaving.value = true
  serverError.value = ''
  try {
    await api.patch('/users/me/', {
      name: `${profile.firstName.trim()} ${profile.lastName.trim()}`.trim(),
      bio: profile.bio,
    })
    await auth.fetchMe()
    saved.value = true
    setTimeout(() => (saved.value = false), 3000)
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd zapisywania.'
  } finally {
    isSaving.value = false
  }
}

const changePassword = async () => {
  passwordError.value = ''
  if (passwordForm.newPass.length < 8) { passwordError.value = 'Minimum 8 znaków.'; return }
  if (passwordForm.newPass !== passwordForm.confirm) { passwordError.value = 'Hasła nie są identyczne.'; return }
  try {
    await api.post('/users/me/password/', { old_password: passwordForm.current, new_password: passwordForm.newPass })
    passwordSaved.value = true
    Object.assign(passwordForm, { current: '', newPass: '', confirm: '' })
    setTimeout(() => (passwordSaved.value = false), 3000)
  } catch (err) {
    passwordError.value = err.response?.data?.error ?? 'Błąd zmiany hasła.'
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <h1 class="page-title">Mój <span>profil</span></h1>

      <div class="profile-grid">
        <!-- Karta główna -->
        <div class="card avatar-card">
          <div class="avatar-large" :style="avatarUrl ? { backgroundImage: `url(${avatarUrl})`, backgroundSize: 'cover', fontSize: 0 } : {}">
            <template v-if="!avatarUrl">{{ profile.firstName.charAt(0) }}{{ profile.lastName.charAt(0) }}</template>
          </div>
          <h2>{{ profile.firstName }} {{ profile.lastName }}</h2>
          <span class="role-chip">{{ profile.role }}</span>
          <p class="bio">{{ profile.bio }}</p>
          <p v-if="avatarError" class="avatar-error">{{ avatarError }}</p>
          <input ref="avatarInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onAvatarSelected" />
          <button class="btn-avatar" :disabled="uploadingAvatar" @click="triggerAvatarPick">
            {{ uploadingAvatar ? 'Przesyłanie…' : '📷 Zmień avatar' }}
          </button>
        </div>

        <!-- Edycja danych -->
        <div class="card form-card">
          <h2 class="card-title">Dane osobowe</h2>
          <form @submit.prevent="saveProfile">
            <div class="fields-row">
              <div class="field"><label>Imię</label><input v-model="profile.firstName" type="text" /></div>
              <div class="field"><label>Nazwisko</label><input v-model="profile.lastName" type="text" /></div>
            </div>
            <div class="field"><label>E-mail <span class="readonly">(tylko do odczytu)</span></label><input v-model="profile.email" type="email" disabled /></div>
            <div class="field"><label>O sobie</label><textarea v-model="profile.bio" rows="3" placeholder="Napisz coś o sobie..."></textarea></div>
            <div class="form-footer-row">
              <span v-if="saved" class="saved-msg">✓ Zapisano pomyślnie</span>
              <button type="submit" class="btn-save" :disabled="isSaving">{{ isSaving ? 'Zapisywanie...' : 'Zapisz zmiany' }}</button>
            </div>
          </form>

          <!-- Zmiana hasła -->
          <div class="divider"></div>
          <h2 class="card-title">Zmiana hasła</h2>
          <form @submit.prevent="changePassword">
            <div class="field"><label>Aktualne hasło</label><input v-model="passwordForm.current" type="password" placeholder="••••••••" /></div>
            <div class="fields-row">
              <div class="field"><label>Nowe hasło</label><input v-model="passwordForm.newPass" type="password" placeholder="Min. 8 znaków" /></div>
              <div class="field"><label>Powtórz hasło</label><input v-model="passwordForm.confirm" type="password" placeholder="••••••••" /></div>
            </div>
            <p v-if="passwordError" class="error-msg">{{ passwordError }}</p>
            <button type="submit" class="btn-save secondary">Zmień hasło</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1000px; margin: 0 auto; }
.page-title { font-size: 2rem; font-weight: 800; margin-bottom: 2rem; span { color: #3b82f6; } }
.profile-grid { display: grid; grid-template-columns: 280px 1fr; gap: 1.5rem; @media (max-width: 768px) { grid-template-columns: 1fr; } }
.card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 2rem; }
.avatar-card { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
.avatar-large { width: 90px; height: 90px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 22px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 900; }
h2 { font-size: 1.1rem; font-weight: 700; margin: 0; }
.role-chip { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.2); color: #60a5fa; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.72rem; font-weight: 700; }
.bio { color: #64748b; font-size: 0.85rem; line-height: 1.5; text-align: center; }
.btn-avatar { padding: 0.55rem 1.1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 0.6rem; cursor: pointer; font-size: 0.82rem; font-weight: 600; transition: 0.2s; &:hover:not(:disabled) { background: rgba(255,255,255,0.09); } &:disabled { opacity: 0.5; cursor: not-allowed; } }
.avatar-error { color: #ef4444; font-size: 0.75rem; margin: 0; }

.card-title { font-size: 1rem; font-weight: 700; margin: 0 0 1.25rem; color: #f1f5f9; }
.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.field { margin-bottom: 1rem; label { display: block; font-size: 0.8rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.4rem; .readonly { color: #475569; font-weight: 400; } } }
input, textarea {
  width: 100%; padding: 0.75rem 0.9rem;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.7rem;
  color: white; font-size: 0.88rem; box-sizing: border-box; resize: vertical;
  &::placeholder { color: #475569; }
  &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.form-footer-row { display: flex; justify-content: flex-end; align-items: center; gap: 1rem; }
.saved-msg { color: #10b981; font-size: 0.85rem; font-weight: 600; }
.btn-save { padding: 0.7rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 0.7rem; font-weight: 700; font-size: 0.88rem; cursor: pointer; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.6; cursor: not-allowed; } &.secondary { width: 100%; margin-top: 0.25rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); &:hover { background: rgba(255,255,255,0.1); } } }
.divider { height: 1px; background: rgba(255,255,255,0.06); margin: 1.75rem 0; }
.error-msg { color: #ef4444; font-size: 0.8rem; margin-bottom: 0.5rem; }
</style>