<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

const router = useRouter()
const route = useRoute()

const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const done = ref(false)
const loading = ref(false)

const handleSubmit = async () => {
  error.value = ''
  if (password.value.length < 8) { error.value = 'Hasło musi mieć minimum 8 znaków.'; return }
  if (password.value !== confirmPassword.value) { error.value = 'Hasła muszą być identyczne.'; return }
  loading.value = true
  try {
    await api.post('/auth/reset-password/', { token: route.params.token, password: password.value })
    done.value = true
  } catch (err) {
    error.value = err.response?.data?.error ?? 'Nieprawidłowy lub wygasły link resetowania hasła.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="card">
      <div class="card-icon">🔐</div>

      <template v-if="!done">
        <h1>Nowe hasło</h1>
        <p class="desc">Wprowadź nowe hasło dla swojego konta.</p>

        <form @submit.prevent="handleSubmit">
          <div class="field">
            <label>Nowe hasło</label>
            <input v-model="password" type="password" placeholder="Minimum 8 znaków" required />
          </div>
          <div class="field">
            <label>Powtórz hasło</label>
            <input v-model="confirmPassword" type="password" placeholder="••••••••" required />
          </div>
          <div v-if="error" class="error-box">{{ error }}</div>
          <button type="submit" class="btn-submit">Ustaw nowe hasło</button>
        </form>
      </template>

      <template v-else>
        <div class="success-state">
          <div class="success-icon">✅</div>
          <h2>Hasło zmienione!</h2>
          <p>Możesz teraz zalogować się przy użyciu nowego hasła.</p>
          <router-link to="/login" class="btn-submit">Przejdź do logowania</router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper {
  min-height: 100vh;
  background: #020617;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.card {
  width: 100%;
  max-width: 420px;
  background: #0f172a;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 1.5rem;
  padding: 2.5rem;
  .card-icon { font-size: 2.5rem; margin-bottom: 1rem; }
  h1 { font-size: 1.6rem; font-weight: 800; color: white; margin: 0 0 0.5rem; }
  .desc { color: #64748b; font-size: 0.9rem; line-height: 1.6; margin-bottom: 2rem; }
}
.field {
  margin-bottom: 1.1rem;
  label { display: block; font-size: 0.82rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.45rem; }
  input {
    width: 100%; padding: 0.82rem 1rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 0.7rem;
    color: white; font-size: 0.93rem; box-sizing: border-box;
    &::placeholder { color: #475569; }
    &:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
  }
}
.error-box {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  color: #ef4444;
  padding: 0.75rem 1rem;
  border-radius: 0.6rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.btn-submit {
  display: block;
  width: 100%;
  padding: 0.9rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s;
  &:hover { background: #2563eb; transform: translateY(-1px); }
}
.success-state {
  text-align: center;
  .success-icon { font-size: 3rem; margin-bottom: 1rem; }
  h2 { font-size: 1.5rem; font-weight: 800; color: white; margin-bottom: 1rem; }
  p { color: #94a3b8; font-size: 0.9rem; margin-bottom: 2rem; }
}
</style>