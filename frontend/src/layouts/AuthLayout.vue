<script setup lang="ts">
// AuthLayout shell
</script>

<template>
  <div class="auth-layout">
    <router-view />
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  width: 100%;
  display: flex;
  background-color: var(--bg-app);
}
</style>
