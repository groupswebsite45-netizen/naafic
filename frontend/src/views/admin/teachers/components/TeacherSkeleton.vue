<script setup lang="ts">
defineProps<{
  rows?: number;
}>();
</script>

<template>
  <div class="skeleton-container">
    <div v-for="i in (rows || 6)" :key="i" class="skeleton-row">
      <div class="skeleton-avatar" />
      <div class="skeleton-text-group">
        <div class="skeleton-line w-40" />
        <div class="skeleton-line w-24 sm" />
      </div>
      <div class="skeleton-chip hide-mobile" />
      <div class="skeleton-chip hide-mobile" />
      <div class="skeleton-badge" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-container {
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  box-sizing: border-box;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.skeleton-avatar {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  background: #e2e8f0;
  flex-shrink: 0;
  animation: pulse 1.5s infinite;
}

.skeleton-text-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1 1 auto;
}

.skeleton-line {
  height: 14px;
  background: #e2e8f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.skeleton-line.sm {
  height: 10px;
}

.w-40 { width: 40%; max-width: 160px; }
.w-24 { width: 25%; max-width: 100px; }

.skeleton-chip {
  width: 80px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
  flex-shrink: 0;
}

.skeleton-badge {
  width: 65px;
  height: 22px;
  background: #e2e8f0;
  border-radius: 9999px;
  animation: pulse 1.5s infinite;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .hide-mobile {
    display: none;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
</style>
