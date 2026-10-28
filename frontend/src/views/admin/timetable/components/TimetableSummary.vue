<script setup lang="ts">
import { computed } from 'vue';
import { TimetableSummary } from '../../../../types/school';

const props = defineProps<{
  summary: TimetableSummary | null;
  isLoading: boolean;
}>();

const hasConflicts = computed(() => {
  return (props.summary?.conflicts_count ?? 0) > 0;
});
</script>

<template>
  <div class="summary-grid">
    <!-- Total Periods -->
    <div class="summary-card">
      <div class="card-icon-wrap bg-blue">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">Total Periods</span>
        <div v-if="isLoading" class="skeleton-val"></div>
        <span v-else class="card-value">{{ summary?.total_periods ?? 0 }}</span>
      </div>
    </div>

    <!-- Scheduled Classes -->
    <div class="summary-card">
      <div class="card-icon-wrap bg-indigo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M6 6h10" />
          <path d="M6 10h10" />
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">Scheduled Classes</span>
        <div v-if="isLoading" class="skeleton-val"></div>
        <span v-else class="card-value">{{ summary?.scheduled_classes ?? 0 }}</span>
      </div>
    </div>

    <!-- Teachers Assigned -->
    <div class="summary-card">
      <div class="card-icon-wrap bg-emerald">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M19 8v6m3-3h-6" />
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">Teachers Scheduled</span>
        <div v-if="isLoading" class="skeleton-val"></div>
        <span v-else class="card-value">{{ summary?.assigned_teachers ?? 0 }}</span>
      </div>
    </div>

    <!-- Conflicts Count -->
    <div class="summary-card" :class="{ 'has-conflicts': hasConflicts }">
      <div class="card-icon-wrap" :class="hasConflicts ? 'bg-amber' : 'bg-slate'">
        <svg v-if="hasConflicts" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">Conflicts</span>
        <div v-if="isLoading" class="skeleton-val"></div>
        <div v-else class="conflict-val-wrap">
          <span class="card-value" :class="{ 'text-amber': hasConflicts }">
            {{ summary?.conflicts_count ?? 0 }}
          </span>
          <span v-if="hasConflicts" class="conflict-warning-pill">Action needed</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.875rem;
  width: 100%;
  box-sizing: border-box;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1rem 1.125rem;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  min-width: 0;
}

.summary-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.summary-card.has-conflicts {
  border-color: #fde68a;
  background: #fffdf5;
}

.card-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-md, 0.5rem);
  flex-shrink: 0;
}

.card-icon-wrap svg {
  width: 1.25rem;
  height: 1.25rem;
}

.bg-blue {
  background: #eff6ff;
  color: #1e40af;
}

.bg-indigo {
  background: #eef2ff;
  color: #4338ca;
}

.bg-emerald {
  background: #ecfdf5;
  color: #047857;
}

.bg-slate {
  background: #f1f5f9;
  color: #475569;
}

.bg-amber {
  background: #fef3c7;
  color: #d97706;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.card-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-value {
  font-size: 1.375rem;
  font-weight: 800;
  color: var(--text-main, #0f172a);
  line-height: 1.2;
}

.text-amber {
  color: #b45309;
}

.conflict-val-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.conflict-warning-pill {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.1rem 0.375rem;
  background: #fef3c7;
  color: #b45309;
  border-radius: 9999px;
  border: 1px solid #fde68a;
  white-space: nowrap;
}

.skeleton-val {
  width: 2.5rem;
  height: 1.5rem;
  background: #e2e8f0;
  border-radius: 0.25rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
