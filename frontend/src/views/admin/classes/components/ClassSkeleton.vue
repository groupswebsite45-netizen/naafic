<script setup lang="ts">
defineProps<{
  rows?: number;
}>();
</script>

<template>
  <div class="skeleton-container">
    <div
      v-for="i in (rows || 5)"
      :key="i"
      class="skeleton-row"
    >
      <div class="skeleton-avatar"></div>
      <div class="skeleton-col flex-2">
        <div class="skeleton-line line-title"></div>
        <div class="skeleton-line line-subtitle"></div>
      </div>
      <div class="skeleton-col flex-2">
        <div class="skeleton-line line-bar"></div>
      </div>
      <div class="skeleton-col flex-1">
        <div class="skeleton-line line-pill"></div>
      </div>
      <div class="skeleton-col flex-1">
        <div class="skeleton-line line-pill"></div>
      </div>
      <div class="skeleton-col flex-1">
        <div class="skeleton-line line-badge"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.skeleton-row:last-child {
  border-bottom: none;
}

.skeleton-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background-color: #f1f5f9;
  flex-shrink: 0;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.skeleton-line {
  background-color: #f1f5f9;
  border-radius: 0.25rem;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.line-title {
  width: 70%;
  height: 0.875rem;
}

.line-subtitle {
  width: 40%;
  height: 0.6875rem;
}

.line-bar {
  width: 85%;
  height: 0.75rem;
}

.line-pill {
  width: 60%;
  height: 1.25rem;
  border-radius: 9999px;
}

.line-badge {
  width: 4rem;
  height: 1.25rem;
  border-radius: 9999px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
