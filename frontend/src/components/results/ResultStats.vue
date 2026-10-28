<script setup lang="ts">
import { ResultOverviewStats } from '../../types/resultWorkflow';

interface Props {
  stats: ResultOverviewStats | null;
  isLoading?: boolean;
}

defineProps<Props>();
</script>

<template>
  <div class="stats-grid">
    <!-- Card 1: CLASSES -->
    <div class="stat-card blue">
      <div class="stat-header">
        <span class="stat-label">CLASSES</span>
        <div class="icon-wrap blue">
          <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
      </div>
      <div class="stat-body">
        <span v-if="isLoading" class="stat-skeleton" />
        <span v-else class="stat-value">{{ stats?.classes_count ?? 0 }}</span>
        <span class="stat-sub">Active streams</span>
      </div>
    </div>

    <!-- Card 2: SUBMISSIONS -->
    <div class="stat-card amber">
      <div class="stat-header">
        <span class="stat-label">SUBMISSIONS</span>
        <div class="icon-wrap amber">
          <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
      </div>
      <div class="stat-body">
        <span v-if="isLoading" class="stat-skeleton" />
        <span v-else class="stat-value">
          {{ stats?.submissions_completed ?? 0 }} <span class="stat-denom">/ {{ stats?.submissions_total ?? 0 }}</span>
        </span>
        <span class="stat-sub">Faculty submissions</span>
      </div>
    </div>

    <!-- Card 3: PENDING -->
    <div class="stat-card orange">
      <div class="stat-header">
        <span class="stat-label">PENDING</span>
        <div class="icon-wrap orange">
          <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div class="stat-body">
        <span v-if="isLoading" class="stat-skeleton" />
        <span v-else class="stat-value">{{ stats?.pending_count ?? 0 }}</span>
        <span class="stat-sub">Awaiting marks</span>
      </div>
    </div>

    <!-- Card 4: APPROVED -->
    <div class="stat-card purple">
      <div class="stat-header">
        <span class="stat-label">APPROVED</span>
        <div class="icon-wrap purple">
          <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div class="stat-body">
        <span v-if="isLoading" class="stat-skeleton" />
        <span v-else class="stat-value">{{ stats?.approved_count ?? 0 }}</span>
        <span class="stat-sub">Verified by Admin</span>
      </div>
    </div>

    <!-- Card 5: RELEASED -->
    <div class="stat-card emerald">
      <div class="stat-header">
        <span class="stat-label">RELEASED</span>
        <div class="icon-wrap emerald">
          <svg class="stat-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </div>
      </div>
      <div class="stat-body">
        <span v-if="isLoading" class="stat-skeleton" />
        <span v-else class="stat-value">{{ stats?.released_count ?? 0 }}</span>
        <span class="stat-sub">Visible to students</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
  width: 100%;
}

.stat-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.15rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: #475569;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.stat-card.blue::before { background: linear-gradient(90deg, #0284c7, #38bdf8); }
.stat-card.amber::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
.stat-card.orange::before { background: linear-gradient(90deg, #ea580c, #fb923c); }
.stat-card.purple::before { background: linear-gradient(90deg, #7c3aed, #c084fc); }
.stat-card.emerald::before { background: linear-gradient(90deg, #059669, #34d399); }

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #94a3b8;
  text-transform: uppercase;
}

.icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-wrap.blue { background-color: rgba(2, 132, 199, 0.15); color: #38bdf8; }
.icon-wrap.amber { background-color: rgba(217, 119, 6, 0.15); color: #fbbf24; }
.icon-wrap.orange { background-color: rgba(234, 88, 12, 0.15); color: #fb923c; }
.icon-wrap.purple { background-color: rgba(124, 58, 237, 0.15); color: #c084fc; }
.icon-wrap.emerald { background-color: rgba(5, 150, 105, 0.15); color: #34d399; }

.stat-icon {
  width: 1rem;
  height: 1rem;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.2;
}

.stat-denom {
  font-size: 1rem;
  font-weight: 600;
  color: #94a3b8;
}

.stat-sub {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 500;
}

.stat-skeleton {
  display: block;
  width: 60%;
  height: 1.75rem;
  background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Tablet viewports (640px - 1024px) */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

/* Mobile viewports (320px - 640px) */
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .stat-card:last-child {
    grid-column: span 2;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
