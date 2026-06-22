<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const router = useRouter()

const users = ref([])

const search = ref('')
const roleFilter = ref('ALL')

const filtered = computed(() => users.value.filter(u => {
  const matchSearch = !search.value || u.name.toLowerCase().includes(search.value.toLowerCase()) || u.email.includes(search.value)
  const matchRole = roleFilter.value === 'ALL' || u.role === roleFilter.value
  return matchSearch && matchRole
}))

const roleColors = { STUDENT: '#3b82f6', CREATOR: '#8b5cf6', ADMIN: '#ef4444' }
const roleColor = (r) => roleColors[r] || '#64748b'

onMounted(async () => {
  try {
    const { data } = await api.get('users/')
    users.value = (data.results ?? []).map(u => ({
      id: u.id,
      name: u.name ?? '—',
      email: u.email ?? '—',
      role: u.role,
      active: u.is_active ?? true,
      joined: u.created_at?.slice(0, 10) ?? '—',
      courses: 0,
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link to="/admin/dashboard" class="back-link">← Panel admina</router-link>
        <div class="header-row">
          <h1>Użytkownicy <span>({{ users.length }})</span></h1>
          <router-link to="/admin/users/new" class="btn-new">+ Nowy użytkownik</router-link>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-bar">
          <span>🔍</span>
          <input v-model="search" type="text" placeholder="Szukaj po nazwie lub e-mail..." />
        </div>
        <div class="role-tabs">
          <button v-for="r in ['ALL', 'STUDENT', 'CREATOR', 'ADMIN']" :key="r"
            class="role-tab" :class="{ active: roleFilter === r }"
            @click="roleFilter = r">
            {{ r === 'ALL' ? 'Wszyscy' : r }}
          </button>
        </div>
      </div>

      <div class="users-table">
        <div class="table-header">
          <span>Użytkownik</span>
          <span>Rola</span>
          <span>Status</span>
          <span>Data dołączenia</span>
          <span>Kursy</span>
          <span>Akcje</span>
        </div>
        <div v-for="u in filtered" :key="u.id" class="user-row">
          <div class="user-info">
            <div class="user-avatar" :style="{ background: `linear-gradient(135deg, ${roleColor(u.role)}, #1e293b)` }">{{ u.name.charAt(0) }}</div>
            <div>
              <strong>{{ u.name }}</strong>
              <small>{{ u.email }}</small>
            </div>
          </div>
          <div><span class="role-chip" :style="{ color: roleColor(u.role), background: roleColor(u.role) + '22' }">{{ u.role }}</span></div>
          <div><span class="status-dot" :class="{ active: u.active }"></span> {{ u.active ? 'Aktywny' : 'Zablokowany' }}</div>
          <div class="date-cell">{{ u.joined }}</div>
          <div class="num-cell">{{ u.courses }}</div>
          <div class="actions-cell">
            <router-link :to="`/admin/users/${u.id}`" class="action-btn">Edytuj</router-link>
          </div>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="empty">Brak użytkowników pasujących do kryteriów</div>

      <!-- TODO: Paginacja → GET /api/admin/users/?page=X -->
      <div class="pagination">
        <button class="page-btn" disabled>← Poprzednia</button>
        <span class="page-info">Strona 1 z 1</span>
        <button class="page-btn" disabled>Następna →</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 1.75rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; justify-content: space-between; align-items: center; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.btn-new { padding: 0.7rem 1.4rem; background: #3b82f6; color: white; border-radius: 0.75rem; text-decoration: none; font-weight: 700; font-size: 0.88rem; transition: 0.2s; &:hover { background: #2563eb; } }

.toolbar { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.25rem; flex-wrap: wrap; }
.search-bar { display: flex; align-items: center; gap: 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.85rem; padding: 0.65rem 1rem; flex: 1; min-width: 200px; span { color: #475569; } input { flex: 1; background: none; border: none; color: white; font-size: 0.88rem; outline: none; &::placeholder { color: #475569; } } }
.role-tabs { display: flex; gap: 0.35rem; }
.role-tab { padding: 0.45rem 0.85rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); color: #64748b; border-radius: 0.6rem; cursor: pointer; font-size: 0.78rem; font-weight: 600; transition: 0.15s; &.active { background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.3); color: #60a5fa; } }

.users-table { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; overflow: hidden; }
.table-header { display: grid; grid-template-columns: 2.5fr 1fr 1fr 1fr 0.7fr 0.8fr; gap: 0.75rem; padding: 0.85rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.user-row { display: grid; grid-template-columns: 2.5fr 1fr 1fr 1fr 0.7fr 0.8fr; gap: 0.75rem; align-items: center; padding: 0.9rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); transition: 0.15s; &:last-child { border-bottom: none; } &:hover { background: rgba(255,255,255,0.02); } }
.user-info { display: flex; align-items: center; gap: 0.75rem; .user-avatar { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; flex-shrink: 0; } strong { display: block; font-size: 0.87rem; } small { color: #64748b; font-size: 0.72rem; } }

.role-chip { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 0.5rem; font-size: 0.7rem; font-weight: 800; }
.status-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #ef4444; margin-right: 0.35rem; &.active { background: #10b981; } }
.date-cell, .num-cell { font-size: 0.82rem; color: #64748b; }
.actions-cell { display: flex; gap: 0.4rem; }
.action-btn { padding: 0.35rem 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.5rem; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: 0.15s; &:hover { background: rgba(59,130,246,0.1); color: #60a5fa; } }

.empty { text-align: center; padding: 3rem; color: #64748b; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1.5rem; margin-top: 1.5rem; .page-info { color: #64748b; font-size: 0.85rem; } }
.page-btn { padding: 0.55rem 1rem; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; border-radius: 0.6rem; cursor: pointer; font-size: 0.82rem; font-weight: 600; &:disabled { opacity: 0.4; cursor: not-allowed; } }
</style>