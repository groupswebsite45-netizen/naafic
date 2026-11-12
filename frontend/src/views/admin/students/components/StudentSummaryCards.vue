<script setup lang="ts">
import { computed } from 'vue';
import { StudentSummary } from '../../../../types/school';

const props = defineProps<{
  summary: StudentSummary | null;
  isLoading: boolean;
}>();

const cards = computed(() => [
  {
    key: 'total',
    label: 'Total Students',
    value: props.summary?.total_students ?? 0,
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    colorClass: 'blue',
    subtext: 'Enrolled in database',
  },
  {
    key: 'active',
    label: 'Active Students',
    value: props.summary?.active_students ?? 0,
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    colorClass: 'green',
    subtext: 'Regular attendance',
  },
  {
    key: 'inactive',
    label: 'Inactive / Suspended',
    value: props.summary?.inactive_students ?? 0,
    icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
    colorClass: 'amber',
    subtext: 'Deactivated records',
  },
  {
    key: 'unassigned',
    label: 'Without Class',
    value: props.summary?.unassigned_students ?? 0,
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    colorClass: 'purple',
    subtext: 'Needs class enrollment',
  },
]);
</script>

<template>
  <div class="summary-grid">
    <div
      v-for="card in cards"
      :key="card.key"
      class="summary-card"
      :class="card.colorClass"
    >
      <div class="summary-icon-wrap" :class="card.colorClass">
        <svg class="summary-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" :d="card.icon" />
        </svg>
      </div>
      <div class="summary-content">
        <span class="summary-label">{{ card.label }}</span>
        <div class="summary-value-row">
          <span v-if="isLoading" class="summary-skeleton-val" />
          <span v-else class="summary-value">{{ card.value.toLocaleString() }}</span>
        </div>
        <span class="summary-sub">{{ card.subtext }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
  }
}

@media (max-width: 640px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.65rem;
    margin-bottom: 1rem;
  }

  .summary-card {
    padding: 0.75rem 0.65rem;
    gap: 0.5rem;
    border-radius: 10px;
  }

  .summary-icon-wrap {
    width: 36px;
    height: 36px;
  }

  .summary-icon {
    width: 18px;
    height: 18px;
  }

  .summary-label {
    font-size: 0.6875rem;
  }

  .summary-value {
    font-size: 1.25rem;
  }

  .summary-sub {
    display: none;
  }
}

@media (max-width: 360px) {
  .summary-grid {
    gap: 0.5rem;
  }

  .summary-card {
    padding: 0.65rem 0.5rem;
  }

  .summary-icon-wrap {
    width: 30px;
    height: 30px;
  }

  .summary-icon {
    width: 16px;
    height: 16px;
  }

  .summary-value {
    font-size: 1.15rem;
  }
}

.summary-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.125rem 1.25rem;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.summary-card.blue { border-left: 4px solid #2563eb; }
.summary-card.green { border-left: 4px solid #10b981; }
.summary-card.amber { border-left: 4px solid #f59e0b; }
.summary-card.purple { border-left: 4px solid #8b5cf6; }

.summary-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-icon-wrap.blue { background: #eff6ff; color: #2563eb; }
.summary-icon-wrap.green { background: #ecfdf5; color: #10b981; }
.summary-icon-wrap.amber { background: #fffbeb; color: #d97706; }
.summary-icon-wrap.purple { background: #f5f3ff; color: #7c3aed; }

.summary-icon {
  width: 22px;
  height: 22px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.summary-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.summary-value-row {
  display: flex;
  align-items: baseline;
}

.summary-value {
  font-size: 1.625rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.summary-skeleton-val {
  display: inline-block;
  width: 48px;
  height: 28px;
  background: #e2e8f0;
  border-radius: 6px;
  animation: pulse 1.5s infinite;
}

.summary-sub {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.125rem;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
