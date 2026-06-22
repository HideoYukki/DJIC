<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDbStore } from '@/stores/db'

const auth = useAuthStore()
const db   = useDbStore()

const userId = computed(() => auth.user?.id)

const achievements = computed(() => db.getUserAchievements(userId.value))
const xp      = computed(() => db.getTotalXP(userId.value))
const level   = computed(() => Math.floor(xp.value / 500) + 1)
const xpToNext = computed(() => level.value * 500)

const badges = computed(() => achievements.value.map(a => ({
  id: a.id,
  icon: a.icon,
  name: a.name,
  desc: a.description,
  earned: a.unlocked,
  earnedAt: null,
  condition: a.unlocked ? null : a.description,
})))

const xpHistory = ref([])

onMounted(() => db.fetchAchievements(userId.value))
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <header class="page-header">
        <h1>Odznaki <span>& XP</span></h1>
        <p class="subtitle">Grywalizacja — śledź swoje osiągnięcia</p>
      </header>

      <!-- Level widget -->
      <div class="level-widget">
        <div class="level-badge">Poz. {{ level }}</div>
        <div class="level-info">
          <div class="level-label">{{ xp }} / {{ xpToNext }} XP</div>
          <div class="xp-track"><div class="xp-fill" :style="{ width: (xp / xpToNext * 100) + '%' }"></div></div>
        </div>
        <div class="level-next">Poziom {{ level + 1 }}: {{ xpToNext - xp }} XP</div>
      </div>

      <!-- Odznaki -->
      <div class="section-card">
        <h2>Odznaki ({{ badges.filter(b => b.earned).length }}/{{ badges.length }})</h2>
        <div class="badges-grid">
          <div v-for="b in badges" :key="b.id" class="badge-card" :class="{ earned: b.earned, locked: !b.earned }">
            <span class="badge-icon">{{ b.earned ? b.icon : '🔒' }}</span>
            <strong>{{ b.name }}</strong>
            <p>{{ b.earned ? b.desc : b.condition }}</p>
            <span v-if="b.earned" class="earned-date">{{ b.earnedAt }}</span>
          </div>
        </div>
      </div>

      <!-- Historia XP -->
      <div class="section-card">
        <h2>Historia XP</h2>
        <!-- TODO: GET /api/user/xp-history/?limit=20 → chronologiczna lista zdobytego XP -->
        <div class="xp-list">
          <div v-for="(entry, i) in xpHistory" :key="i" class="xp-row">
            <span class="xp-action">{{ entry.action }}</span>
            <span class="xp-date">{{ entry.date }}</span>
            <span class="xp-amount">+{{ entry.xp }} XP</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 1000px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; h1 { font-size: 2rem; font-weight: 800; span { color: #3b82f6; } } .subtitle { color: #64748b; margin-top: 0.4rem; } }

.level-widget {
  display: flex; align-items: center; gap: 1.5rem;
  background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); border-radius: 1.25rem; padding: 1.5rem 2rem; margin-bottom: 2rem; flex-wrap: wrap;
  .level-badge { width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 900; flex-shrink: 0; }
  .level-info { flex: 1; min-width: 200px; }
  .level-label { font-size: 0.88rem; font-weight: 700; color: #60a5fa; margin-bottom: 0.5rem; }
  .xp-track { height: 10px; background: rgba(255,255,255,0.08); border-radius: 5px; overflow: hidden; }
  .xp-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #6366f1); border-radius: 5px; }
  .level-next { font-size: 0.82rem; color: #64748b; white-space: nowrap; }
}

.section-card { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.07); border-radius: 1.25rem; padding: 1.75rem; margin-bottom: 1.5rem; h2 { font-size: 1.05rem; font-weight: 700; margin: 0 0 1.5rem; } }

.badges-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
.badge-card {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 1rem; padding: 1.25rem; text-align: center;
  .badge-icon { font-size: 2.5rem; display: block; margin-bottom: 0.5rem; }
  strong { display: block; font-size: 0.88rem; font-weight: 700; margin-bottom: 0.3rem; }
  p { color: #64748b; font-size: 0.75rem; line-height: 1.4; margin-bottom: 0.5rem; }
  .earned-date { font-size: 0.68rem; color: #475569; }
  &.earned { border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.05); strong { color: #f59e0b; } }
  &.locked { opacity: 0.5; }
}

.xp-list { display: flex; flex-direction: column; }
.xp-row {
  display: flex; align-items: center; padding: 0.7rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
  &:last-child { border-bottom: none; }
  .xp-action { flex: 1; font-size: 0.87rem; color: #e2e8f0; }
  .xp-date { font-size: 0.75rem; color: #475569; margin: 0 1rem; }
  .xp-amount { color: #f59e0b; font-weight: 700; font-size: 0.88rem; white-space: nowrap; }
}
</style>