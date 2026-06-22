<script setup>
import NavBar from '@/components/common/NavBar.vue'
import ServiceBanner from '@/components/common/ServiceBanner.vue'
</script>

<template>
  <div class="app-layout">
    <NavBar />
    <ServiceBanner />
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-content {
  flex: 1;
  width: 100%;
}
</style>
