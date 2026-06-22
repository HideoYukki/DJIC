<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  role: 'STUDENT',
})

const errors = reactive({ firstName: '', lastName: '', email: '', password: '' })
const serverError = ref('')
const successMessage = ref('')

const roles = [
  { value: 'STUDENT', label: 'Uczeń', icon: '📖', desc: 'Chcę się uczyć i rozwijać' },
  { value: 'CREATOR', label: 'Twórca', icon: '🛠️', desc: 'Chcę tworzyć i sprzedawać kursy' },
]

const validate = () => {
  let ok = true
  Object.keys(errors).forEach(k => (errors[k] = ''))
  if (!form.firstName.trim()) { errors.firstName = 'Imię jest wymagane'; ok = false }
  if (!form.lastName.trim())  { errors.lastName  = 'Nazwisko jest wymagane'; ok = false }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'Niepoprawny format e-mail'; ok = false }
  if (form.password.length < 8) { errors.password = 'Minimum 8 znaków'; ok = false }
  return ok
}

const handleRegister = async () => {
  if (!validate()) return
  serverError.value = ''
  const result = await auth.register({
    name: `${form.firstName.trim()} ${form.lastName.trim()}`,
    email: form.email,
    password: form.password,
    role: form.role,
  })
  if (!result.ok) {
    serverError.value = result.error
    return
  }
  successMessage.value = 'Konto zostało utworzone! Możesz się teraz zalogować.'
  setTimeout(() => router.push('/login'), 2000)
}
</script>

<template>
  <div class="register-wrapper">

    <!-- Panel lewy: formularz -->
    <div class="form-panel">
      <div class="form-inner">
        <div class="form-brand">
          <router-link to="/" class="brand-link">
            <span>🎓</span>
            <span class="brand-text">DJIC<span>Platform</span></span>
          </router-link>
        </div>

        <h1>Załóż konto</h1>
        <p class="subtitle">Dołącz do tysięcy uczniów i twórców na platformie DJIC.</p>

        <!-- Wybór roli -->
        <div class="role-selector">
          <button
            v-for="r in roles"
            :key="r.value"
            type="button"
            class="role-btn"
            :class="{ active: form.role === r.value }"
            @click="form.role = r.value"
          >
            <span class="role-icon">{{ r.icon }}</span>
            <div>
              <strong>{{ r.label }}</strong>
              <small>{{ r.desc }}</small>
            </div>
          </button>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="fields-row">
            <div class="field" :class="{ error: errors.firstName }">
              <label>Imię</label>
              <input v-model="form.firstName" type="text" placeholder="Jan" />
              <span class="error-msg">{{ errors.firstName }}</span>
            </div>
            <div class="field" :class="{ error: errors.lastName }">
              <label>Nazwisko</label>
              <input v-model="form.lastName" type="text" placeholder="Kowalski" />
              <span class="error-msg">{{ errors.lastName }}</span>
            </div>
          </div>

          <div class="field" :class="{ error: errors.email }">
            <label>Adres e-mail</label>
            <input v-model="form.email" type="email" placeholder="twój@email.com" />
            <span class="error-msg">{{ errors.email }}</span>
          </div>

          <div class="field" :class="{ error: errors.password }">
            <label>Hasło</label>
            <input v-model="form.password" type="password" placeholder="Minimum 8 znaków" />
            <span class="error-msg">{{ errors.password }}</span>
          </div>

          <p v-if="serverError" class="server-error">{{ serverError }}</p>
          <p v-if="successMessage" class="server-success">{{ successMessage }}</p>

          <button type="submit" class="btn-submit" :disabled="auth.loading">
            <span v-if="auth.loading" class="spinner"></span>
            {{ auth.loading ? 'Tworzenie konta...' : 'Zarejestruj się →' }}
          </button>
        </form>

        <p class="form-footer">
          Masz już konto?
          <router-link to="/login">Zaloguj się</router-link>
        </p>
      </div>
    </div>

    <!-- Panel prawy: wizualny -->
    <div class="visual-panel">
      <div class="visual-content">
        <h2>Tysiące twórców już buduje swoją przyszłość</h2>
        <p>Dołącz do społeczności ekspertów, którzy dzielą się wiedzą i zarabiają na tym, co kochają robić.</p>
        <div class="benefit-list">
          <div class="benefit"><span class="check">✓</span><span>Darmowe konto na zawsze</span></div>
          <div class="benefit"><span class="check">✓</span><span>Nielimitowana liczba kursów</span></div>
          <div class="benefit"><span class="check">✓</span><span>Analityka w czasie rzeczywistym</span></div>
          <div class="benefit"><span class="check">✓</span><span>System certyfikatów i odznak</span></div>
          <div class="benefit"><span class="check">✓</span><span>Wsparcie techniczne 24/7</span></div>
        </div>
        <div class="social-proof">
          <div class="avatars">
            <div class="av" style="background: #3b82f6">A</div>
            <div class="av" style="background: #10b981">M</div>
            <div class="av" style="background: #f59e0b">K</div>
            <div class="av" style="background: #ef4444">P</div>
          </div>
          <p><strong>+12 000</strong> uczniów i twórców nam zaufało</p>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped lang="scss">
.register-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    .visual-panel { display: none; }
  }
}

/* PANEL FORMULARZ */
.form-panel {
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow-y: auto;
}

.form-inner {
  width: 100%;
  max-width: 460px;
  padding: 2rem 0;
}

.form-brand {
  margin-bottom: 2rem;
  .brand-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    font-size: 1.2rem;
  }
  .brand-text { font-weight: 850; color: white; span { color: #3b82f6; } }
}

h1 { font-size: 1.8rem; font-weight: 800; color: white; margin: 0 0 0.4rem; }
.subtitle { color: #64748b; font-size: 0.9rem; margin: 0 0 2rem; }

/* Wybór roli */
.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}
.role-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;

  .role-icon { font-size: 1.3rem; flex-shrink: 0; }
  strong { display: block; color: #f1f5f9; font-size: 0.85rem; font-weight: 700; }
  small { color: #64748b; font-size: 0.72rem; }

  &.active {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.08);
    strong { color: #60a5fa; }
  }
  &:hover:not(.active) { border-color: rgba(255,255,255,0.15); }
}

/* Pola formularza */
.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

.field {
  margin-bottom: 1.1rem;

  label {
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.45rem;
  }

  input {
    width: 100%;
    padding: 0.8rem 0.9rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 0.7rem;
    color: white;
    font-size: 0.92rem;
    box-sizing: border-box;
    transition: all 0.2s;
    &::placeholder { color: #475569; }
    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
      background: rgba(59,130,246,0.04);
    }
  }

  &.error input { border-color: #ef4444; }
  .error-msg { display: block; color: #ef4444; font-size: 0.72rem; margin-top: 0.3rem; font-weight: 500; }
}

.btn-submit {
  width: 100%;
  padding: 0.9rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 0.25rem;
  transition: all 0.2s;
  &:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); box-shadow: 0 8px 20px rgba(59,130,246,0.35); }
  &:disabled { background: #334155; cursor: not-allowed; }
}

.form-footer {
  margin-top: 1.75rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
  a { color: #3b82f6; text-decoration: none; font-weight: 700; &:hover { text-decoration: underline; } }
}

/* PANEL WIZUALNY */
.visual-panel {
  background: linear-gradient(150deg, #020617, #0f172a 50%, #1e3a5f);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  position: relative;
  overflow: hidden;
  &::before {
    content: '';
    position: absolute;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
  }
}
.visual-content {
  position: relative;
  max-width: 420px;
  h2 { font-size: 2rem; font-weight: 800; color: #f1f5f9; line-height: 1.3; margin-bottom: 1rem; }
  p { color: #94a3b8; font-size: 0.95rem; line-height: 1.7; margin-bottom: 2.5rem; }
}
.benefit-list { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 2.5rem; }
.benefit {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #cbd5e1;
  font-size: 0.9rem;
  .check { color: #10b981; font-weight: 800; font-size: 1rem; }
}
.social-proof {
  display: flex;
  align-items: center;
  gap: 1rem;
  .avatars { display: flex; }
  .av {
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: white; font-size: 0.85rem;
    margin-left: -8px;
    border: 2px solid #0f172a;
    &:first-child { margin-left: 0; }
  }
  p { color: #94a3b8; font-size: 0.85rem; strong { color: white; } }
}
</style>