<script setup lang="ts">
import AppButton from '../components/common/AppButton.vue';
</script>

<template>
  <div class="not-found-page">
    <div class="card not-found-card">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-desc">
        The page or resource you are attempting to access does not exist or has been moved.
      </p>
      <router-link to="/login">
        <AppButton variant="primary">Return to Portal</AppButton>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: var(--bg-app);
}

.not-found-card {
  max-width: 480px;
  width: 100%;
  text-align: center;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-code {
  font-size: 5rem;
  font-weight: 800;
  color: var(--brand-primary);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.error-desc {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin-bottom: 2rem;
  line-height: 1.5;
}
</style>
