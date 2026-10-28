<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status: string;
  size?: 'sm' | 'md';
}>();

const normalized = computed(() => (props.status || 'ACTIVE').toUpperCase().trim());

const badgeClass = computed(() => {
  switch (normalized.value) {
    case 'ACTIVE':
      return 'badge-active';
    case 'INACTIVE':
      return 'badge-inactive';
    case 'SUSPENDED':
      return 'badge-suspended';
    case 'GRADUATED':
      return 'badge-graduated';
    case 'PENDING':
    case 'TRANSFERRED':
      return 'badge-pending';
    default:
      return 'badge-neutral';
  }
});

const label = computed(() => {
  switch (normalized.value) {
    case 'ACTIVE':
      return 'Active';
    case 'INACTIVE':
      return 'Inactive';
    case 'SUSPENDED':
      return 'Suspended';
    case 'GRADUATED':
      return 'Graduated';
    case 'TRANSFERRED':
      return 'Transferred';
    case 'PENDING':
      return 'Pending';
    default:
      return props.status;
  }
});
</script>

<template>
  <span class="status-badge" :class="[badgeClass, size === 'sm' ? 'size-sm' : 'size-md']">
    <span class="dot" />
    <span class="text">{{ label }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 9999px;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
  letter-spacing: 0.02em;
  transition: all 0.15s ease;
}

.size-md {
  padding: 0.32rem 0.75rem;
  font-size: 0.78rem;
}

.size-sm {
  padding: 0.2rem 0.55rem;
  font-size: 0.72rem;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  flex-shrink: 0;
  background: currentColor;
}

.size-sm .dot {
  width: 6px;
  height: 6px;
}

/* Status variants */
.badge-active {
  background: #DCFCE7;
  color: #15803D;
  border: 1.5px solid #86EFAC;
}
.badge-active .dot {
  background: #16A34A;
  box-shadow: 0 0 8px rgba(22, 163, 74, 0.7);
}

.badge-inactive {
  background: #F1F5F9;
  color: #475569;
  border: 1.5px solid #CBD5E1;
}
.badge-inactive .dot {
  background: #94A3B8;
}

.badge-suspended {
  background: #FEF3C7;
  color: #B45309;
  border: 1.5px solid #FCD34D;
}
.badge-suspended .dot {
  background: #D97706;
  box-shadow: 0 0 8px rgba(217, 119, 6, 0.6);
}

.badge-graduated {
  background: #EDE9FE;
  color: #6D28D9;
  border: 1.5px solid #C4B5FD;
}
.badge-graduated .dot {
  background: #7C3AED;
  box-shadow: 0 0 8px rgba(124, 58, 237, 0.6);
}

.badge-pending {
  background: #E0F2FE;
  color: #0369A1;
  border: 1.5px solid #7DD3FC;
}
.badge-pending .dot {
  background: #0284C7;
  box-shadow: 0 0 8px rgba(2, 132, 199, 0.6);
}

.badge-neutral {
  background: #F8FAFC;
  color: #64748B;
  border: 1.5px solid #E2E8F0;
}
</style>
