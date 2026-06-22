<!-- Widok: NavBar -->
<!-- Rola: WSZYSTKIE -->
<!-- Trasa: globalna -->
<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileOpen = ref(false)

const roleColor  = computed(() => ({ STUDENT: '#3b82f6', CREATOR: '#8b5cf6', ADMIN: '#ef4444' })[auth.role] ?? '#64748b')
const roleLabel  = computed(() => auth.role ?? '—')

const navLinks = computed(() => {
  if (!auth.isLoggedIn) return [
    { to: '/courses', label: 'Kursy' },
    { to: '/login',   label: 'Zaloguj się' },
    { to: '/register', label: 'Zarejestruj się' },
  ]
  if (auth.isAdmin) return [
    { to: '/admin/dashboard', label: 'Panel admina' },
    { to: '/admin/users',     label: 'Użytkownicy' },
    { to: '/admin/courses',   label: 'Kursy' },
    { to: '/admin/logs',      label: 'Logi' },
  ]
  if (auth.isCreator) return [
    { to: '/creator/dashboard', label: 'Dashboard' },
    { to: '/creator/courses',   label: 'Moje kursy' },
    { to: '/creator/reports',   label: 'Raporty' },
  ]
  return [
    { to: '/dashboard',   label: 'Dashboard' },
    { to: '/my-courses',  label: 'Moje kursy' },
    { to: '/progress',    label: 'Postępy' },
    { to: '/achievements', label: 'Odznaki' },
  ]
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <!-- Logo -->
      <router-link to="/" class="logo">
        <span class="logo-mark">DJ</span>
        <span class="logo-text">IC</span>
      </router-link>

      <!-- Linki nawigacji (desktop) -->
      <div class="nav-links desktop-only">
        <router-link
          v-for="link in navLinks" :key="link.to"
          :to="link.to"
          class="nav-link"
          :class="{ active: route.path.startsWith(link.to) && link.to !== '/' }"
        >{{ link.label }}</router-link>
      </div>

      <!-- Prawa strona -->
      <div class="navbar-right desktop-only">
        <template v-if="auth.isLoggedIn">
          <div class="user-chip">
            <span class="role-dot" :style="{ background: roleColor }"></span>
            <span class="user-name">{{ auth.userName }}</span>
            <span class="role-badge" :style="{ color: roleColor }">{{ roleLabel }}</span>
          </div>
          <button class="btn-logout" @click="logout">Wyloguj</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-login">Zaloguj się</router-link>
        </template>
      </div>

      <!-- Hamburger (mobile) -->
      <button class="hamburger desktop-hide" @click="mobileOpen = !mobileOpen">
        <span></span><span></span><span></span>
      </button>
    </div>

    <!-- Menu mobilne -->
    <div v-if="mobileOpen" class="mobile-menu">
      <router-link
        v-for="link in navLinks" :key="link.to"
        :to="link.to"
        class="mobile-link"
        @click="mobileOpen = false">
        {{ link.label }}
      </router-link>
      <button v-if="auth.isLoggedIn" class="btn-logout mobile-logout" @click="logout; mobileOpen = false">
        Wyloguj
      </button>
    </div>
  </nav>
</template>

<style scoped lang="scss">
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  height: var(--navbar-height, 64px);
}

.navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  flex-shrink: 0;
  .logo-mark { font-size: 1.3rem; font-weight: 900; color: #3b82f6; }
  .logo-text  { font-size: 1.3rem; font-weight: 900; color: #f1f5f9; }
}

.nav-links {
  display: flex;
  gap: 0.25rem;
  flex: 1;
}

.nav-link {
  padding: 0.45rem 0.85rem;
  color: #64748b;
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 600;
  border-radius: 0.6rem;
  transition: 0.15s;
  &:hover  { color: #e2e8f0; background: rgba(255,255,255,0.05); }
  &.active { color: #f1f5f9; background: rgba(59,130,246,0.1); }
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 9999px;
  .role-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
  .user-name { font-size: 0.82rem; color: #e2e8f0; font-weight: 600; }
  .role-badge { font-size: 0.65rem; font-weight: 800; letter-spacing: 0.05em; }
}


.btn-login {
  padding: 0.5rem 1.1rem;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 0.65rem;
  font-size: 0.85rem;
  font-weight: 700;
  transition: 0.15s;
  &:hover { background: #2563eb; }
}

.btn-logout {
  padding: 0.45rem 0.9rem;
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.18);
  color: #f87171;
  border-radius: 0.65rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.15s;
  &:hover { background: rgba(239,68,68,0.14); }
}

.desktop-only { @media (max-width: 768px) { display: none !important; } }
.desktop-hide  { @media (min-width: 769px) { display: none !important; } }

.hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  margin-left: auto;
  span {
    display: block;
    width: 22px;
    height: 2px;
    background: #94a3b8;
    border-radius: 2px;
    transition: 0.2s;
  }
}

.mobile-menu {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 0.75rem 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  background: rgba(2,6,23,0.97);
}
.mobile-link {
  padding: 0.65rem 0.75rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 0.65rem;
  &:hover { background: rgba(255,255,255,0.04); color: white; }
}
.mobile-logout {
  margin-top: 0.5rem;
  text-align: center;
}
</style>
