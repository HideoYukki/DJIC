<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="page-wrapper">
    <div class="content">
      <div class="code">404</div>
      <h1>Strony nie znaleziono</h1>
      <p>Adres, którego szukasz, nie istnieje lub został przeniesiony.</p>
      <div class="actions">
        <button class="btn-back" @click="router.go(-1)">← Wróć</button>
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
.code {
  font-size: 7rem;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
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
}
.btn-back {
  padding: 0.7rem 1.5rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #94a3b8;
  border-radius: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: 0.15s;
  &:hover { background: rgba(255,255,255,0.07); }
}
.btn-home {
  padding: 0.7rem 1.75rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.75rem;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
  transition: 0.2s;
  &:hover { background: #2563eb; }
}
</style>