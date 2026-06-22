<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const serverError = ref('')
const errors = ref({ email: '', password: '' })

function validate() {
  errors.value = { email: '', password: '' }
  if (!email.value.includes('@')) errors.value.email = 'Podaj poprawny adres e-mail'
  if (password.value.length < 1)  errors.value.password = 'Hasło jest wymagane'
  return !errors.value.email && !errors.value.password
}

async function handleLogin() {
  if (!validate()) return
  serverError.value = ''
  const result = await auth.login(email.value, password.value)
  if (!result.ok) {
    serverError.value = result.error
    return
  }
  const redirectMap = { ADMIN: '/admin/dashboard', CREATOR: '/creator/dashboard', STUDENT: '/dashboard' }
  router.push(redirectMap[result.role] ?? '/dashboard')
}
</script>

<template>
  <div class="login-wrapper">

    <!-- Panel lewy: wizualny -->
    <div class="visual-panel">
      <div class="visual-inner">
        <router-link to="/" class="back-link">← Powrót do strony głównej</router-link>
        <div class="visual-content">
          <div class="quote-block">
            <p class="quote-text">"Edukacja to najpotężniejsza broń, jaką możesz użyć, by zmienić świat."</p>
            <p class="quote-author">— Nelson Mandela</p>
          </div>
          <div class="platform-features">
            <div class="feat-item"><span class="feat-icon">📊</span><span>Analityka postępów w czasie rzeczywistym</span></div>
            <div class="feat-item"><span class="feat-icon">🏆</span><span>System odznak i punktów XP</span></div>
            <div class="feat-item"><span class="feat-icon">📱</span><span>Dostęp z każdego urządzenia</span></div>
            <div class="feat-item"><span class="feat-icon">🔒</span><span>Szyfrowanie danych 128-bit AES</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Panel prawy: formularz -->
    <div class="form-panel">
      <div class="form-inner">
        <div class="form-brand">
          <span class="brand-icon">🎓</span>
          <span class="brand-text">DJIC<span>Platform</span></span>
        </div>

        <h1>Witaj ponownie</h1>
        <p class="subtitle">Zaloguj się, aby kontynuować pracę nad kursami.</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field" :class="{ 'has-error': errors.email }">
            <label for="email">Adres e-mail</label>
            <input
              v-model="email"
              id="email"
              type="email"
              placeholder="twój@email.com"
              autocomplete="email"
            />
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
          </div>

          <div class="field" :class="{ 'has-error': errors.password }">
            <label for="password">
              Hasło
              <router-link to="/forgot-password" class="forgot-link">Zapomniałeś?</router-link>
            </label>
            <input
              v-model="password"
              id="password"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
            />
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>

          <p v-if="serverError" class="server-error">{{ serverError }}</p>

          <button type="submit" class="btn-submit" :disabled="auth.loading">
            <span v-if="auth.loading" class="spinner"></span>
            {{ auth.loading ? 'Logowanie…' : 'Zaloguj się →' }}
          </button>
        </form>

        <p class="form-footer">
          Nie masz konta?
          <router-link to="/register">Zarejestruj się za darmo</router-link>
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped lang="scss">
.login-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    .visual-panel { display: none; }
  }
}

/* Panel lewy */
.visual-panel {
  background: linear-gradient(150deg, #020617 0%, #0f172a 60%, #1e3a5f 100%);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, transparent 70%);
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
  }
}

.visual-inner {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 2rem;
}

.back-link {
  color: #64748b;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: color 0.2s;
  &:hover { color: #94a3b8; }
}

.visual-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem 2rem;
}

.quote-block {
  margin-bottom: 3rem;
  .quote-text {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.5;
    margin-bottom: 1rem;
    font-style: italic;
  }
  .quote-author { color: #3b82f6; font-weight: 700; font-size: 0.95rem; }
}

.platform-features { display: flex; flex-direction: column; gap: 0.85rem; }
.feat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  .feat-icon { font-size: 1.1rem; }
  span:last-child { color: #94a3b8; font-size: 0.9rem; font-weight: 500; }
}

/* Panel prawy */
.form-panel {
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.form-inner {
  width: 100%;
  max-width: 420px;
}

.form-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 3rem;
  .brand-icon { font-size: 1.6rem; }
  .brand-text { font-size: 1.3rem; font-weight: 850; color: white; span { color: #3b82f6; } }
}

h1 { font-size: 2rem; font-weight: 800; color: white; margin: 0 0 0.5rem; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0 0 2.5rem; }

.field {
  margin-bottom: 1.25rem;

  label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.83rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.5rem;
  }

  .forgot-link {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 600;
    &:hover { text-decoration: underline; }
  }

  input {
    width: 100%;
    padding: 0.85rem 1rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 0.75rem;
    color: white;
    font-size: 0.95rem;
    box-sizing: border-box;
    transition: all 0.2s;

    &::placeholder { color: #475569; }
    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
      background: rgba(59, 130, 246, 0.04);
    }
  }

  &.has-error input {
    border-color: rgba(239, 68, 68, 0.5);
  }
}

.server-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #f87171;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.field-error {
  display: block;
  font-size: 0.75rem;
  color: #f87171;
  margin-top: 0.35rem;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.5rem;
  vertical-align: middle;
}

@keyframes spin { to { transform: rotate(360deg); } }

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
  margin-top: 0.5rem;
  transition: all 0.2s;

  &:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
  }
}

.form-footer {
  margin-top: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
  a { color: #3b82f6; text-decoration: none; font-weight: 700; &:hover { text-decoration: underline; } }
}

</style>