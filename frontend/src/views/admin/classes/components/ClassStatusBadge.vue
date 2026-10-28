<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status?: string;
  capacityStatus?: string;
  type?: 'status' | 'capacity';
}>();

const config = computed(() => {
  if (props.type === 'capacity' || (!props.status && props.capacityStatus)) {
    const cap = (props.capacityStatus || '').toUpperCase();
    switch (cap) {
      case 'OVER_CAPACITY':
        return { label: 'Over Capacity', dotClass: 'dot-danger', badgeClass: 'badge-danger' };
      case 'FULL':
        return { label: 'Full', dotClass: 'dot-warning', badgeClass: 'badge-warning' };
      case 'NEAR_CAPACITY':
        return { label: 'Near Capacity', dotClass: 'dot-amber', badgeClass: 'badge-amber' };
      case 'NORMAL':
      default:
        return { label: 'Available', dotClass: 'dot-success', badgeClass: 'badge-success' };
    }
  }

  const s = (props.status || 'ACTIVE').toUpperCase();
  switch (s) {
    case 'ACTIVE':
      return { label: 'Active', dotClass: 'dot-success', badgeClass: 'badge-success' };
    case 'INACTIVE':
      return { label: 'Inactive', dotClass: 'dot-muted', badgeClass: 'badge-muted' };
    case 'ARCHIVED':
      return { label: 'Archived', dotClass: 'dot-indigo', badgeClass: 'badge-indigo' };
    case 'FULL':
      return { label: 'Full', dotClass: 'dot-warning', badgeClass: 'badge-warning' };
    default:
      return { label: s, dotClass: 'dot-muted', badgeClass: 'badge-muted' };
  }
});
</script>

<template>
  <span class="status-badge" :class="config.badgeClass">
    <span class="status-dot" :class="config.dotClass"></span>
    <span class="status-label">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
  letter-spacing: 0.01em;
  user-select: none;
  border: 1.5px solid transparent;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Success / Active */
.badge-success {
  background-color: #ecfdf5;
  color: #047857;
  border-color: #a7f3d0;
}
.dot-success {
  background-color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.7);
}

/* Warning / Full */
.badge-warning {
  background-color: #fffbeb;
  color: #b45309;
  border-color: #fde68a;
}
.dot-warning {
  background-color: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.7);
}

/* Amber / Near Capacity */
.badge-amber {
  background-color: #fff7ed;
  color: #c2410c;
  border-color: #fed7aa;
}
.dot-amber {
  background-color: #ea580c;
  box-shadow: 0 0 8px rgba(234, 88, 12, 0.7);
}

/* Danger / Over Capacity */
.badge-danger {
  background-color: #fef2f2;
  color: #b91c1c;
  border-color: #fecaca;
}
.dot-danger {
  background-color: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.7);
}

/* Indigo / Archived */
.badge-indigo {
  background-color: #eef2ff;
  color: #4338ca;
  border-color: #c7d2fe;
}
.dot-indigo {
  background-color: #6366f1;
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.7);
}

/* Muted / Inactive */
.badge-muted {
  background-color: #f1f5f9;
  color: #475569;
  border-color: #cbd5e1;
}
.dot-muted {
  background-color: #94a3b8;
}
</style>
