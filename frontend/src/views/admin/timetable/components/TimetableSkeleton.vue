<script setup lang="ts">
defineProps<{
  daysCount?: number;
}>();
</script>

<template>
  <div class="skeleton-grid-card">
    <div class="skeleton-header-row">
      <div v-for="i in (daysCount || 6)" :key="i" class="skeleton-day-header">
        <div class="skeleton-bar" style="width: 50%; height: 0.875rem"></div>
        <div class="skeleton-circle"></div>
      </div>
    </div>
    <div class="skeleton-body-grid">
      <div v-for="i in (daysCount || 6)" :key="i" class="skeleton-column">
        <div class="skeleton-slot-card">
          <div class="skeleton-bar" style="width: 70%; height: 0.875rem"></div>
          <div class="skeleton-bar" style="width: 50%; height: 0.75rem"></div>
          <div class="skeleton-bar" style="width: 40%; height: 0.625rem"></div>
        </div>
        <div class="skeleton-slot-card">
          <div class="skeleton-bar" style="width: 60%; height: 0.875rem"></div>
          <div class="skeleton-bar" style="width: 45%; height: 0.75rem"></div>
          <div class="skeleton-bar" style="width: 35%; height: 0.625rem"></div>
        </div>
        <div class="skeleton-empty-box"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-grid-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.skeleton-header-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.75rem 0.5rem;
  gap: 0.5rem;
}

.skeleton-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.5rem;
}

.skeleton-body-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  padding: 0.75rem 0.5rem;
  gap: 0.5rem;
  min-height: 420px;
}

.skeleton-column {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.skeleton-slot-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.skeleton-empty-box {
  flex: 1;
  min-height: 100px;
  border: 1px dashed #e2e8f0;
  border-radius: 0.5rem;
  background: #ffffff;
}

.skeleton-bar {
  background: #e2e8f0;
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

.skeleton-circle {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: #e2e8f0;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

@media (max-width: 992px) {
  .skeleton-header-row,
  .skeleton-body-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .skeleton-header-row,
  .skeleton-body-grid {
    grid-template-columns: 1fr;
  }
}
</style>
