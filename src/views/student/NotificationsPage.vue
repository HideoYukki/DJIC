<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const notifications = ref([])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const markAllRead = async () => {
  notifications.value.forEach(n => (n.read = true))
  try { await api.patch('/notifications/read-all/') } catch (_) {}
}

const markRead = async (id) => {
  const n = notifications.value.find(n => n.id === id)
  if (n) n.read = true
  try { await api.patch(`/notifications/${id}/read/`) } catch (_) {}
}

const typeColor = (type) => ({
  achievement: '#f59e0b',
  quiz: '#3b82f6',
  info: '#10b981',
  system: '#8b5cf6',
  reminder: '#64748b',
}[type] || '#64748b')

onMounted(async () => {
  try {
    const { data } = await api.get('/notifications/')
    notifications.value = (data.results ?? []).map(n => ({
      id: n.id,
      type: n.type ?? 'info',
      icon: n.icon ?? '📢',
      title: n.title ?? '',
      message: n.message ?? '',
      time: n.created_at ? new Date(n.created_at).toLocaleDateString('pl-PL') : '',
      read: n.is_read ?? false,
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <div>
          <h1>Powiadomienia</h1>
          <p class="subtitle" v-if="unreadCount > 0">{{ unreadCount }} nieprzeczytanych</p>
        </div>
        <button v-if="unreadCount > 0" class="btn-mark-all" @click="markAllRead">Oznacz wszystkie jako przeczytane</button>
      </header>

      <div class="notif-list">
        <div
          v-for="n in notifications"
          :key="n.id"
          class="notif-item"
          :class="{ unread: !n.read }"
          @click="markRead(n.id)"
        >
          <div class="notif-icon-wrap" :style="{ background: typeColor(n.type) + '20', borderColor: typeColor(n.type) + '40' }">
            <span class="notif-icon">{{ n.icon }}</span>
          </div>
          <div class="notif-body">
            <strong>{{ n.title }}</strong>
            <p>{{ n.message }}</p>
            <span class="notif-time">{{ n.time }}</span>
          </div>
          <div class="notif-indicator" v-if="!n.read"></div>
        </div>
      </div>

      <div v-if="notifications.length === 0" class="empty-state">
        <span>🔔</span>
        <p>Brak powiadomień</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 760px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; h1 { font-size: 2rem; font-weight: 800; margin: 0 0 0.25rem; } .subtitle { color: #3b82f6; font-size: 0.88rem; margin: 0; } }
.btn-mark-all { padding: 0.55rem 1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 0.65rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; white-space: nowrap; transition: 0.2s; &:hover { background: rgba(255,255,255,0.09); } }

.notif-list { display: flex; flex-direction: column; gap: 0.5rem; }
.notif-item {
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.06); border-radius: 1rem;
  cursor: pointer; transition: 0.2s; position: relative;
  &.unread { background: rgba(15,23,42,0.7); border-color: rgba(59,130,246,0.18); }
  &:hover { border-color: rgba(255,255,255,0.12); }
}
.notif-icon-wrap { width: 44px; height: 44px; border-radius: 12px; border: 1px solid; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.notif-icon { font-size: 1.3rem; }
.notif-body { flex: 1; strong { display: block; font-size: 0.9rem; color: #f1f5f9; font-weight: 700; margin-bottom: 0.2rem; } p { color: #64748b; font-size: 0.83rem; line-height: 1.4; margin-bottom: 0.4rem; } .notif-time { font-size: 0.72rem; color: #475569; } }
.notif-indicator { position: absolute; top: 1.1rem; right: 1.25rem; width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; }

.empty-state { text-align: center; padding: 4rem; span { font-size: 3rem; display: block; margin-bottom: 1rem; } p { color: #64748b; } }
</style>