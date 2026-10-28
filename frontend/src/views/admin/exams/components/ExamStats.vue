<script setup lang="ts">
import { ExamSummary } from '../../../../types/school';

defineProps<{
  summary: ExamSummary | null;
  isLoading?: boolean;
}>();
</script>

<template>
  <div class="stats-grid">
    <!-- Total Exams -->
    <div class="stat-card">
      <div class="stat-content">
        <span class="stat-label">Total Exams</span>
        <div class="stat-value">
          <span v-if="!isLoading">{{ summary?.total_exams ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">All scheduled assessments</span>
      </div>
      <div class="stat-icon-wrapper blue">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      </div>
    </div>

    <!-- Upcoming Exams -->
    <div class="stat-card">
      <div class="stat-content">
        <span class="stat-label">Upcoming</span>
        <div class="stat-value">
          <span v-if="!isLoading">{{ summary?.upcoming_exams ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">Scheduled on calendar</span>
      </div>
      <div class="stat-icon-wrapper amber">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    </div>

    <!-- Ongoing Exams -->
    <div class="stat-card">
      <div class="stat-content">
        <span class="stat-label">Ongoing</span>
        <div class="stat-value">
          <span v-if="!isLoading">{{ summary?.ongoing_exams ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">Active testing window</span>
      </div>
      <div class="stat-icon-wrapper indigo">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>

    <!-- Completed Exams -->
    <div class="stat-card">
      <div class="stat-content">
        <span class="stat-label">Completed</span>
        <div class="stat-value">
          <span v-if="!isLoading">{{ summary?.completed_exams ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">Testing concluded</span>
      </div>
      <div class="stat-icon-wrapper purple">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    </div>

    <!-- Published Results -->
    <div class="stat-card highlight">
      <div class="stat-content">
        <span class="stat-label">Results Published</span>
        <div class="stat-value text-emerald">
          <span v-if="!isLoading">{{ summary?.published_results ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">Live for authorized portals</span>
      </div>
      <div class="stat-icon-wrapper emerald">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      </div>
    </div>

    <!-- Students Assessed -->
    <div class="stat-card">
      <div class="stat-content">
        <span class="stat-label">Students Assessed</span>
        <div class="stat-value">
          <span v-if="!isLoading">{{ summary?.total_students_assessed ?? 0 }}</span>
          <span v-else class="stat-skeleton" />
        </div>
        <span class="stat-caption">Recorded in PostgreSQL</span>
      </div>
      <div class="stat-icon-wrapper sky">
        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.875rem;
  margin-bottom: 1.25rem;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  min-width: 0;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
}

.stat-card.highlight {
  border-color: #a7f3d0;
  background: linear-gradient(to bottom right, #ffffff, #f0fdf4);
}

.stat-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  line-height: 1.2;
  margin: 0.2rem 0;
}

.stat-value.text-emerald {
  color: #059669;
}

.stat-caption {
  font-size: 0.6875rem;
  color: var(--text-muted, #94a3b8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  flex-shrink: 0;
}

.stat-icon {
  width: 20px;
  height: 20px;
}

.stat-icon-wrapper.blue {
  background-color: #eff6ff;
  color: #2563eb;
}

.stat-icon-wrapper.amber {
  background-color: #fffbeb;
  color: #d97706;
}

.stat-icon-wrapper.indigo {
  background-color: #eef2ff;
  color: #4f46e5;
}

.stat-icon-wrapper.purple {
  background-color: #faf5ff;
  color: #7e22ce;
}

.stat-icon-wrapper.emerald {
  background-color: #ecfdf5;
  color: #059669;
}

.stat-icon-wrapper.sky {
  background-color: #f0f9ff;
  color: #0284c7;
}

.stat-skeleton {
  display: inline-block;
  width: 32px;
  height: 22px;
  background: #e2e8f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.625rem;
  }
  .stat-card {
    padding: 0.75rem;
  }
  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
