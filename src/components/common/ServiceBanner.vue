<script setup>
import { isServerOffline } from '@/api'
</script>

<template>
  <transition name="slide-down">
    <div v-if="isServerOffline" class="service-banner" role="alert">
      <span class="pulse"></span>
      <span>Serwis chwilowo niedostępny — część funkcji może być ograniczona</span>
    </div>
  </transition>
</template>

<style scoped>
.service-banner {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  z-index: 99;
  background: rgba(245, 158, 11, 0.1);
  border-bottom: 1px solid rgba(245, 158, 11, 0.22);
  backdrop-filter: blur(8px);
  padding: 0.45rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  font-size: 0.82rem;
  color: #fbbf24;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f59e0b;
  flex-shrink: 0;
  animation: pulse 1.6s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.35; transform: scale(0.75); }
}

.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from,
.slide-down-leave-to     { transform: translateY(-100%); opacity: 0; }
</style>
