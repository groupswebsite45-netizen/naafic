<script setup lang="ts">
defineProps<{
  rows?: number;
}>();
</script>

<template>
  <div class="skeleton-table-card">
    <div class="skeleton-header">
      <div class="skeleton-col" style="width: 25%"></div>
      <div class="skeleton-col" style="width: 20%"></div>
      <div class="skeleton-col" style="width: 15%"></div>
      <div class="skeleton-col" style="width: 15%"></div>
      <div class="skeleton-col" style="width: 15%"></div>
      <div class="skeleton-col" style="width: 10%"></div>
    </div>
    <div
      v-for="i in (rows || 6)"
      :key="i"
      class="skeleton-row"
    >
      <div class="skeleton-cell" style="width: 25%">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-text-group">
          <div class="skeleton-bar" style="width: 75%; height: 0.875rem"></div>
          <div class="skeleton-bar" style="width: 45%; height: 0.625rem"></div>
        </div>
      </div>
      <div class="skeleton-cell" style="width: 20%">
        <div class="skeleton-bar" style="width: 60%; height: 0.75rem"></div>
      </div>
      <div class="skeleton-cell" style="width: 15%">
        <div class="skeleton-bar" style="width: 50%; height: 0.75rem"></div>
      </div>
      <div class="skeleton-cell" style="width: 15%">
        <div class="skeleton-bar" style="width: 50%; height: 0.75rem"></div>
      </div>
      <div class="skeleton-cell" style="width: 15%">
        <div class="skeleton-badge"></div>
      </div>
      <div class="skeleton-cell" style="width: 10%">
        <div class="skeleton-btn"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-table-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.skeleton-header {
  display: flex;
  align-items: center;
  padding: 0.875rem 1rem;
  background: var(--bg-main, #f8fafc);
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.skeleton-col {
  height: 0.75rem;
  background: #e2e8f0;
  border-radius: 0.25rem;
}

.skeleton-row {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color, #f1f5f9);
}

.skeleton-row:last-child {
  border-bottom: none;
}

.skeleton-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.skeleton-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md, 0.5rem);
  background: #e2e8f0;
  flex-shrink: 0;
  animation: pulse 1.5s infinite;
}

.skeleton-text-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
}

.skeleton-bar {
  background: #e2e8f0;
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

.skeleton-badge {
  width: 4rem;
  height: 1.25rem;
  background: #e2e8f0;
  border-radius: 9999px;
  animation: pulse 1.5s infinite;
}

.skeleton-btn {
  width: 1.75rem;
  height: 1.75rem;
  background: #e2e8f0;
  border-radius: var(--radius-md, 0.5rem);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}
</style>
