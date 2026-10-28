<script setup lang="ts">
defineProps<{
  rows?: number;
}>();
</script>

<template>
  <div class="skeleton-wrapper">
    <!-- Desktop Table Skeleton -->
    <div class="table-skeleton hide-mobile">
      <div v-for="i in (rows || 5)" :key="i" class="skeleton-row">
        <div class="skeleton-cell flex-cell">
          <div class="skeleton-circle" />
          <div class="skeleton-lines">
            <div class="skeleton-line line-name" />
            <div class="skeleton-line line-sub" />
          </div>
        </div>
        <div class="skeleton-cell"><div class="skeleton-line line-code" /></div>
        <div class="skeleton-cell"><div class="skeleton-line line-pill" /></div>
        <div class="skeleton-cell"><div class="skeleton-line line-guardian" /></div>
        <div class="skeleton-cell"><div class="skeleton-line line-badge" /></div>
        <div class="skeleton-cell"><div class="skeleton-line line-badge" /></div>
        <div class="skeleton-cell actions-cell"><div class="skeleton-circle sm" /></div>
      </div>
    </div>

    <!-- Mobile Card Skeleton -->
    <div class="card-skeleton hide-desktop">
      <div v-for="i in (rows || 3)" :key="i" class="skeleton-card">
        <div class="card-sk-top">
          <div class="skeleton-circle" />
          <div class="skeleton-lines flex-1">
            <div class="skeleton-line line-name" />
            <div class="skeleton-line line-sub" />
          </div>
        </div>
        <div class="skeleton-divider" />
        <div class="card-sk-grid">
          <div class="skeleton-line" />
          <div class="skeleton-line" />
          <div class="skeleton-line" />
          <div class="skeleton-line" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
}

.skeleton-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr 1fr 1fr 40px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  align-items: center;
}

.flex-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.skeleton-lines {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
}

.skeleton-circle {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  background: #e2e8f0;
  animation: pulse 1.5s infinite;
  flex-shrink: 0;
}

.skeleton-circle.sm {
  width: 24px;
  height: 24px;
}

.skeleton-line {
  height: 12px;
  background: #e2e8f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.line-name { width: 120px; height: 14px; }
.line-sub { width: 70px; height: 10px; }
.line-code { width: 80px; height: 20px; }
.line-pill { width: 90px; height: 20px; }
.line-guardian { width: 110px; }
.line-badge { width: 60px; height: 20px; }

.card-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.skeleton-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
}

.card-sk-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.flex-1 { flex: 1; }

.skeleton-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.75rem 0;
}

.card-sk-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .hide-mobile { display: none; }
}

@media (min-width: 769px) {
  .hide-desktop { display: none; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
</style>
