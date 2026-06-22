<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const router = useRouter()

const form = ref({
  name: '',
  email: '',
  role: 'STUDENT',
  password: '',
  passwordConfirm: '',
  sendWelcomeEmail: true,
})

const roleOptions = [
  { value: 'STUDENT', label: 'Uczeń', desc: 'Dostęp do kursów i materiałów' },
  { value: 'CREATOR', label: 'Twórca', desc: 'Może tworzyć i publikować kursy' },
  { value: 'ADMIN', label: 'Administrator', desc: 'Pełny dostęp do systemu' },
]

const errors = ref({})
const saving = ref(false)

const roleColors = { STUDENT: '#3b82f6', CREATOR: '#8b5cf6', ADMIN: '#ef4444' }

function validate() {
  errors.value = {}
  if (!form.value.name.trim()) errors.value.name = 'Imię i nazwisko są wymagane'
  if (!form.value.email.includes('@')) errors.value.email = 'Podaj poprawny adres e-mail'
  if (form.value.password.length < 8) errors.value.password = 'Hasło musi mieć co najmniej 8 znaków'
  if (form.value.password !== form.value.passwordConfirm) errors.value.passwordConfirm = 'Hasła nie są identyczne'
  return Object.keys(errors.value).length === 0
}

const serverError = ref('')

async function submit() {
  if (!validate()) return
  saving.value = true
  serverError.value = ''
  try {
    await api.post('users/', {
      name:     form.value.name,
      email:    form.value.email,
      role:     form.value.role,
      password: form.value.password,
    })
    router.push('/admin/users')
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd tworzenia użytkownika.'
    saving.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/users" class="back-link">← Zarządzanie użytkownikami</router-link>
        <h1>Nowy <span>użytkownik</span></h1>
        <p class="subtitle">Utwórz konto ręcznie z poziomu panelu administratora</p>
      </div>

      <form class="form-card" @submit.prevent="submit">
        <!-- Dane podstawowe -->
        <div class="section-title">Dane konta</div>
        <div class="field-row">
          <div class="field" :class="{ error: errors.name }">
            <label>Imię i nazwisko</label>
            <input v-model="form.name" type="text" placeholder="Jan Kowalski" />
            <span v-if="errors.name" class="err-msg">{{ errors.name }}</span>
          </div>
          <div class="field" :class="{ error: errors.email }">
            <label>Adres e-mail</label>
            <input v-model="form.email" type="email" placeholder="j.kowalski@mail.com" />
            <span v-if="errors.email" class="err-msg">{{ errors.email }}</span>
          </div>
        </div>

        <!-- Rola -->
        <div class="section-title">Rola w systemie</div>
        <div class="role-grid">
          <label
            v-for="r in roleOptions" :key="r.value"
            class="role-card"
            :class="{ selected: form.role === r.value }"
            :style="form.role === r.value ? { borderColor: roleColors[r.value], background: roleColors[r.value] + '10' } : {}"
          >
            <input type="radio" v-model="form.role" :value="r.value" hidden />
            <span class="role-dot" :style="{ background: roleColors[r.value] }"></span>
            <div>
              <strong>{{ r.label }}</strong>
              <small>{{ r.desc }}</small>
            </div>
          </label>
        </div>

        <!-- Hasło -->
        <div class="section-title">Hasło</div>
        <div class="field-row">
          <div class="field" :class="{ error: errors.password }">
            <label>Hasło</label>
            <input v-model="form.password" type="password" placeholder="Min. 8 znaków" />
            <span v-if="errors.password" class="err-msg">{{ errors.password }}</span>
          </div>
          <div class="field" :class="{ error: errors.passwordConfirm }">
            <label>Powtórz hasło</label>
            <input v-model="form.passwordConfirm" type="password" placeholder="Powtórz hasło" />
            <span v-if="errors.passwordConfirm" class="err-msg">{{ errors.passwordConfirm }}</span>
          </div>
        </div>

        <!-- Opcje -->
        <label class="checkbox-row">
          <input type="checkbox" v-model="form.sendWelcomeEmail" />
          <span>Wyślij e-mail powitalny z danymi do logowania</span>
        </label>

        <div class="form-actions">
          <router-link to="/admin/users" class="btn-cancel">Anuluj</router-link>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? 'Tworzenie…' : 'Utwórz konto' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 760px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; span { color: #3b82f6; } } .subtitle { color: #64748b; font-size: 0.85rem; } }

.form-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.5rem; padding: 2rem; }
.section-title { font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin: 0 0 1rem; &:not(:first-child) { margin-top: 2rem; } }

.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; @media (max-width: 600px) { grid-template-columns: 1fr; } }
.field { display: flex; flex-direction: column; gap: 0.4rem; label { font-size: 0.78rem; font-weight: 600; color: #94a3b8; } input { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 0.7rem 1rem; color: white; font-size: 0.9rem; outline: none; transition: 0.15s; &::placeholder { color: #475569; } &:focus { border-color: rgba(59,130,246,0.4); background: rgba(255,255,255,0.06); } } &.error input { border-color: rgba(239,68,68,0.35); } }
.err-msg { font-size: 0.72rem; color: #f87171; }

.role-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; @media (max-width: 600px) { grid-template-columns: 1fr; } }
.role-card { display: flex; align-items: center; gap: 0.85rem; padding: 0.9rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; cursor: pointer; transition: 0.15s; .role-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; } strong { display: block; font-size: 0.87rem; margin-bottom: 0.15rem; } small { color: #64748b; font-size: 0.72rem; } }

.checkbox-row { display: flex; align-items: center; gap: 0.65rem; margin-top: 1.5rem; cursor: pointer; font-size: 0.85rem; color: #94a3b8; input { accent-color: #3b82f6; width: 15px; height: 15px; } }

.form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.06); }
.btn-cancel { padding: 0.7rem 1.4rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.75rem; text-decoration: none; font-weight: 600; font-size: 0.88rem; display: flex; align-items: center; }
.btn-submit { padding: 0.7rem 1.75rem; background: #3b82f6; color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover:not(:disabled) { background: #2563eb; } &:disabled { opacity: 0.5; cursor: not-allowed; } }
</style>