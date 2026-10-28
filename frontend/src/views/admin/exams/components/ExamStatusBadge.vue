<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status?: string | null;
}>();

const normalized = computed(() => {
  return (props.status || 'SCHEDULED').toUpperCase();
});

const label = computed(() => {
  switch (normalized.value) {
    case 'DRAFT': return 'Draft';
    case 'SCHEDULED': return 'Scheduled';
    case 'OPEN_FOR_RESULTS': return 'Open for Results';
    case 'ONGOING':
    case 'IN_PROGRESS': return 'In Progress';
    case 'COMPLETED': return 'Completed';
    case 'CLOSED': return 'Closed';
    case 'PUBLISHED': return 'Published';
    case 'CANCELLED': return 'Cancelled';
    default: return props.status || 'Unknown';
  }
});

const badgeClass = computed(() => {
  switch (normalized.value) {
    case 'DRAFT': return 'badge-draft';
    case 'SCHEDULED': return 'badge-scheduled';
    case 'OPEN_FOR_RESULTS': return 'badge-open';
    case 'ONGOING':
    case 'IN_PROGRESS': return 'badge-ongoing';
    case 'COMPLETED': return 'badge-completed';
    case 'CLOSED': return 'badge-closed';
    case 'PUBLISHED': return 'badge-published';
    case 'CANCELLED': return 'badge-cancelled';
    default: return 'badge-default';
  }
});
</script>

<template>
  <span class="status-badge" :class="badgeClass">
    <span class="status-dot" />
    <span class="status-text">{{ label }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
  width: fit-content;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-draft {
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}
.badge-draft .status-dot {
  background-color: #64748b;
}

.badge-scheduled {
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}
.badge-scheduled .status-dot {
  background-color: #2563eb;
}

.badge-open {
  background-color: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.badge-open .status-dot {
  background-color: #10b981;
}

.badge-closed {
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}
.badge-closed .status-dot {
  background-color: #64748b;
}

.badge-ongoing {
  background-color: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}
.badge-ongoing .status-dot {
  background-color: #f59e0b;
}

.badge-completed {
  background-color: #f3e8ff;
  color: #7e22ce;
  border: 1px solid #e9d5ff;
}
.badge-completed .status-dot {
  background-color: #9333ea;
}

.badge-published {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}
.badge-published .status-dot {
  background-color: #10b981;
}

.badge-cancelled {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}
.badge-cancelled .status-dot {
  background-color: #ef4444;
}

.badge-default {
  background-color: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
.badge-default .status-dot {
  background-color: #94a3b8;
}
</style>
