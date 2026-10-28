<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status?: string;
}>();

const config = computed(() => {
  const s = (props.status || 'ACTIVE').toUpperCase();
  switch (s) {
    case 'ACTIVE':
      return { label: 'Active', dotClass: 'dot-success', badgeClass: 'badge-success' };
    case 'INACTIVE':
      return { label: 'Inactive', dotClass: 'dot-muted', badgeClass: 'badge-muted' };
    case 'ARCHIVED':
      return { label: 'Archived', dotClass: 'dot-indigo', badgeClass: 'badge-indigo' };
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
  gap: 0.375rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
  letter-spacing: 0.01em;
  user-select: none;
  border: 1px solid transparent;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-success {
  background-color: #ecfdf5;
  color: #065f46;
  border-color: #a7f3d0;
}
.dot-success {
  background-color: #10b981;
}

.badge-indigo {
  background-color: #eef2ff;
  color: #3730a3;
  border-color: #c7d2fe;
}
.dot-indigo {
  background-color: #6366f1;
}

.badge-muted {
  background-color: #f3f4f6;
  color: #4b5563;
  border-color: #e5e7eb;
}
.dot-muted {
  background-color: #9ca3af;
}
</style>
