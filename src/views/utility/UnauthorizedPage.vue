<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="page-wrapper">
    <div class="content">
      <div class="icon">🔒</div>
      <div class="code">403</div>
      <h1>Brak uprawnień</h1>
      <p>Nie masz dostępu do tej strony. Zaloguj się na konto z odpowiednią rolą lub skontaktuj się z administratorem.</p>
      <div class="actions">
        <button class="btn-back" @click="router.go(-1)">← Wróć</button>
        <router-link to="/login" class="btn-login">Zaloguj się</router-link>
        <router-link to="/" class="btn-home">Strona główna</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper {
  background: #020617;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 2rem;
}
.content {
  text-align: center;
  max-width: 480px;
}
.icon {
  font-size: 3.5rem;
  margin-bottom: 0.5rem;
}
.code {
  font-size: 5rem;
  font-weight: 900;
  line-height: 1;
  color: #ef4444;
  opacity: 0.7;
  margin-bottom: 0.75rem;
}
h1 {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
}
p {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 2rem;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.btn-back {
  padding: 0.7rem 1.25rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #94a3b8;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.88rem;
  transition: 0.15s;
  &:hover { background: rgba(255,255,255,0.07); }
}
.btn-login {
  padding: 0.7rem 1.5rem;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  color: #f87171;
  border-radius: 0.75rem;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.88rem;
  transition: 0.15s;
  &:hover { background: rgba(239,68,68,0.16); }
}
.btn-home {
  padding: 0.7rem 1.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.75rem;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.88rem;
  transition: 0.2s;
  &:hover { background: #2563eb; }
}
</style>