<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './stores/auth';

const authStore = useAuthStore();

onMounted(async () => {
  // If access token is stored, verify and refresh user profile
  if (authStore.accessToken) {
    await authStore.fetchCurrentUser();
  }
});
</script>

<template>
  <router-view />
</template>

<style>
/* Global styles loaded via main.ts */
</style>
