<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import draggable from 'vuedraggable'

const route = useRoute()
const courseId = route.params.id

const materials = ref([])
const saving = ref(false)

const deleteMaterial = async (materialId) => {
  if (!confirm('Usunąć ten materiał?')) return
  try {
    await api.delete(`/courses/${courseId}/materials/${materialId}/`)
    materials.value = materials.value.filter(m => m.id !== materialId)
  } catch (_) {}
}

const onReorderEnd = async () => {
  saving.value = true
  try {
    await api.patch(
      `/courses/${courseId}/materials/reorder/`,
      materials.value.map((m, i) => ({ id: m.id, order: i + 1 })),
    )
  } catch (_) {} finally {
    saving.value = false
  }
}

const typeIcon  = (t) => ({ VIDEO: '▶', QUIZ: '❓', TEXT: '📄' }[t] || '📄')
const typeColor = (t) => ({ VIDEO: '#3b82f6', QUIZ: '#f59e0b', TEXT: '#10b981' }[t] || '#64748b')

onMounted(async () => {
  try {
    const { data } = await api.get(`/courses/${courseId}/materials/`)
    materials.value = (Array.isArray(data) ? data : data.results ?? []).map(m => ({
      id: m.id,
      title: m.title,
      type: m.type,
      duration: m.duration_seconds ? `${Math.round(m.duration_seconds / 60)}min` : '—',
    }))
  } catch (_) {}
})
</script>

<template>
  <div class="page-wrapper">
    <div class="container">
      <div class="page-header">
        <router-link :to="`/creator/courses/${route.params.id}/edit`" class="back-link">← Edycja kursu</router-link>
        <div class="header-row">
          <h1>Materiały <span>kursu</span></h1>
          <router-link :to="`/creator/courses/${route.params.id}/materials/new`" class="btn-primary">+ Dodaj materiał</router-link>
        </div>
      </div>

      <!-- Lista materiałów z drag-and-drop -->
      <div class="chapter-card">
        <div class="chapter-header-static">
          <h3>Materiały kursu</h3>
          <span class="chapter-count">{{ materials.length }} mat.</span>
          <span v-if="saving" class="saving-indicator">💾 Zapisywanie…</span>
        </div>

        <div class="materials-list">
          <draggable
            v-model="materials"
            item-key="id"
            handle=".mat-drag"
            ghost-class="ghost-row"
            animation="150"
            @end="onReorderEnd"
          >
            <template #item="{ element: mat }">
              <div class="material-row">
                <div class="mat-drag" title="Przeciągnij, aby zmienić kolejność">⠿</div>
                <span class="mat-type-icon" :style="{ color: typeColor(mat.type) }">{{ typeIcon(mat.type) }}</span>
                <span class="mat-title">{{ mat.title }}</span>
                <span class="mat-badge" :style="{ color: typeColor(mat.type) }">{{ mat.type }}</span>
                <span class="mat-duration">{{ mat.duration }}</span>
                <div class="mat-actions">
                  <router-link :to="`/creator/courses/${route.params.id}/materials/${mat.id}/edit`" class="btn-edit-sm">✏️</router-link>
                  <button class="btn-delete-sm" @click="deleteMaterial(mat.id)">🗑️</button>
                </div>
              </div>
            </template>
          </draggable>

          <div v-if="materials.length === 0" class="empty-chapter">
            Brak materiałów — <router-link :to="`/creator/courses/${route.params.id}/materials/new`">Dodaj pierwszy</router-link>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper { background: #020617; min-height: 100vh; padding: 90px 20px 60px; color: white; }
.container { max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; .back-link { color: #64748b; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; } }
.header-row { display: flex; justify-content: space-between; align-items: center; h1 { font-size: 2rem; font-weight: 800; margin: 0; span { color: #3b82f6; } } }
.btn-primary { padding: 0.7rem 1.4rem; background: #3b82f6; color: white; border-radius: 0.7rem; text-decoration: none; font-weight: 700; font-size: 0.88rem; box-shadow: 0 4px 12px rgba(59,130,246,0.3); transition: 0.2s; &:hover { background: #2563eb; } display: inline-block; }

.chapter-card { background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 1rem; overflow: hidden; margin-bottom: 1.25rem; }
.chapter-header-static { display: flex; align-items: center; gap: 0.75rem; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.05);
  h3 { flex: 1; font-size: 0.95rem; font-weight: 700; margin: 0; }
  .chapter-count { font-size: 0.75rem; color: #64748b; }
  .saving-indicator { font-size: 0.72rem; color: #64748b; animation: pulse 1.2s ease-in-out infinite; }
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.ghost-row { opacity: 0.35; background: rgba(59,130,246,0.08); border-radius: 0.6rem; }
.btn-delete-sm { background: none; border: none; cursor: pointer; color: #475569; padding: 0.2rem 0.3rem; border-radius: 0.4rem; transition: 0.15s; &:hover { color: #ef4444; background: rgba(239,68,68,0.1); } }
.btn-edit-sm { color: #64748b; text-decoration: none; padding: 0.2rem 0.3rem; border-radius: 0.4rem; font-size: 0.85rem; transition: 0.15s; &:hover { color: #3b82f6; } }

.materials-list { padding: 0.5rem 1rem 1rem; }
.material-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.5rem; border-radius: 0.6rem; transition: 0.15s; cursor: default; &:hover { background: rgba(255,255,255,0.03); }
  .mat-drag { color: #475569; cursor: grab; font-size: 1rem; user-select: none; &:active { cursor: grabbing; } }
  .mat-type-icon { width: 20px; text-align: center; font-size: 0.9rem; flex-shrink: 0; }
  .mat-title { flex: 1; font-size: 0.87rem; color: #e2e8f0; }
  .mat-badge { font-size: 0.68rem; font-weight: 700; padding: 0.12rem 0.45rem; background: rgba(255,255,255,0.05); border-radius: 0.3rem; }
  .mat-duration { font-size: 0.75rem; color: #475569; white-space: nowrap; }
  .mat-actions { display: flex; gap: 0.3rem; }
}
.empty-chapter { color: #475569; font-size: 0.82rem; padding: 1rem 0.5rem; text-align: center; a { color: #3b82f6; } }
</style>