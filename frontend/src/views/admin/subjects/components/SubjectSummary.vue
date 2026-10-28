<script setup lang="ts">
import { SubjectSummary } from '../../../../types/school';

defineProps<{
  summary: SubjectSummary | null;
  isLoading: boolean;
}>();
</script>

<template>
  <div class="stats-grid">
    <!-- Total Subjects -->
    <div class="stat-card">
      <div class="stat-icon icon-blue">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Total Subjects</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.total_subjects ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Active Subjects -->
    <div class="stat-card">
      <div class="stat-icon icon-emerald">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Active Subjects</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.active_subjects ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Assigned Subjects -->
    <div class="stat-card">
      <div class="stat-icon icon-indigo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Assigned to Classes</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.assigned_subjects ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Unassigned Subjects -->
    <div class="stat-card">
      <div class="stat-icon icon-amber">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" x2="12" y1="8" y2="12" />
          <line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Unassigned Subjects</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.unassigned_subjects ?? 0 }}
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  width: 100%;
}

.stat-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem 1.125rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  min-width: 0;
}

.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.icon-blue {
  background-color: #eff6ff;
  color: #2563eb;
}

.icon-emerald {
  background-color: #ecfdf5;
  color: #059669;
}

.icon-indigo {
  background-color: #eef2ff;
  color: #4f46e5;
}

.icon-amber {
  background-color: #fffbeb;
  color: #d97706;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-skeleton {
  width: 3rem;
  height: 1.5rem;
  background-color: #f1f5f9;
  border-radius: 0.25rem;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 0.75rem 0.875rem;
    gap: 0.625rem;
  }

  .stat-icon {
    width: 2.25rem;
    height: 2.25rem;
  }

  .stat-icon svg {
    width: 1.125rem;
    height: 1.125rem;
  }

  .stat-value {
    font-size: 1.2rem;
  }
}
</style>
