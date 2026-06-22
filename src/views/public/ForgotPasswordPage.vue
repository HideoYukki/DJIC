<script setup>
import { ref } from 'vue'
import { api } from '@/api'

const email = ref('')
const sent = ref(false)
const loading = ref(false)
const serverError = ref('')

const handleSubmit = async () => {
  if (!email.value) return
  loading.value = true
  serverError.value = ''
  try {
    await api.post('auth/forgot-password/', { email: email.value })
    sent.value = true
  } catch (err) {
    serverError.value = err.response?.data?.error ?? 'Błąd wysyłania. Spróbuj ponownie.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="card">
      <router-link to="/login" class="back-link">← Powrót do logowania</router-link>

      <template v-if="!sent">
        <div class="card-icon">🔑</div>
        <h1>Resetowanie hasła</h1>
        <p class="desc">Podaj swój adres e-mail, a wyślemy Ci link do zresetowania hasła.</p>

        <form @submit.prevent="handleSubmit">
          <div class="field">
            <label>Adres e-mail</label>
            <input v-model="email" type="email" placeholder="twój@email.com" required />
          </div>
          <p v-if="serverError" class="server-error">{{ serverError }}</p>
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? 'Wysyłanie…' : 'Wyślij link resetujący' }}
          </button>
        </form>
      </template>

      <template v-else>
        <div class="success-state">
          <div class="success-icon">✉️</div>
          <h2>Sprawdź skrzynkę!</h2>
          <p>Wysłaliśmy link do resetowania hasła na adres <strong>{{ email }}</strong>. Sprawdź folder spam, jeśli wiadomość nie dotarła.</p>
          <router-link to="/login" class="btn-submit">Wróć do logowania</router-link>
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

  .back-link {
    display: inline-block;
    color: #64748b;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 2rem;
    transition: color 0.2s;
    &:hover { color: #94a3b8; }
  }
  .card-icon { font-size: 2.5rem; margin-bottom: 1rem; }
  h1 { font-size: 1.6rem; font-weight: 800; color: white; margin: 0 0 0.5rem; }
  .desc { color: #64748b; font-size: 0.9rem; line-height: 1.6; margin-bottom: 2rem; }
}

.field {
  margin-bottom: 1.25rem;
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
  p { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 2rem; strong { color: #f1f5f9; } }
}
</style>