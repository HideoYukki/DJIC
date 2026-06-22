<script setup>
// Strona konserwacji — wyświetlana gdy settings.maintenanceMode = true
// Nie wymaga logowania ani autoryzacji
const estimatedTime = '2026-06-08 18:00'
</script>

<template>
  <div class="page-wrapper">
    <div class="content">
      <div class="icon">🔧</div>
      <h1>Trwa konserwacja</h1>
      <p class="lead">Platforma DJIC jest chwilowo niedostępna z powodu prac technicznych.</p>
      <div class="eta-box">
        <span class="eta-label">Szacowany czas przywrócenia</span>
        <span class="eta-value">{{ estimatedTime }}</span>
      </div>
      <p class="hint">Przepraszamy za utrudnienia. Sprawdź ponownie za kilka minut.</p>
      <div class="status-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
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
  max-width: 500px;
}
.icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: block;
  animation: spin 4s linear infinite;
}
@keyframes spin {
  0%   { transform: rotate(0deg); }
  25%  { transform: rotate(-15deg); }
  75%  { transform: rotate(15deg); }
  100% { transform: rotate(0deg); }
}
h1 {
  font-size: 2.2rem;
  font-weight: 900;
  margin: 0 0 0.75rem;
}
.lead {
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 1.75rem;
}
.eta-box {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  background: rgba(59,130,246,0.07);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 1rem;
  padding: 1rem 2rem;
  margin-bottom: 1.5rem;
  .eta-label {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
  }
  .eta-value {
    font-size: 1.15rem;
    font-weight: 800;
    color: #60a5fa;
    font-family: monospace;
  }
}
.hint {
  color: #475569;
  font-size: 0.85rem;
  margin: 0 0 2rem;
}
.status-dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  animation: pulse 1.4s ease-in-out infinite;
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}
@keyframes pulse {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40%            { opacity: 1;   transform: scale(1.2); }
}
</style>