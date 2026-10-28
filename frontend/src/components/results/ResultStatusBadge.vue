<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  status: string;
  size?: 'sm' | 'md';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
});

const normalizedStatus = computed(() => {
  return (props.status || 'PENDING').toUpperCase().replace(/\s+/g, '_');
});

const config = computed(() => {
  switch (normalizedStatus.value) {
    case 'RELEASED':
      return { label: 'RELEASED', bg: 'rgba(16, 185, 129, 0.12)', color: '#10b981', border: 'rgba(16, 185, 129, 0.3)', dot: '#10b981' };
    case 'APPROVED':
      return { label: 'APPROVED', bg: 'rgba(59, 130, 246, 0.12)', color: '#3b82f6', border: 'rgba(59, 130, 246, 0.3)', dot: '#3b82f6' };
    case 'COMPLETE':
      return { label: 'COMPLETE', bg: 'rgba(14, 165, 233, 0.12)', color: '#0ea5e9', border: 'rgba(14, 165, 233, 0.3)', dot: '#0ea5e9' };
    case 'SUBMITTED':
      return { label: 'SUBMITTED', bg: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)', dot: '#f59e0b' };
    case 'READY_TO_SUBMIT':
      return { label: 'READY TO SUBMIT', bg: 'rgba(99, 102, 241, 0.12)', color: '#818cf8', border: 'rgba(99, 102, 241, 0.3)', dot: '#818cf8' };
    case 'PARTIAL':
      return { label: 'PARTIAL', bg: 'rgba(234, 88, 12, 0.12)', color: '#fb923c', border: 'rgba(234, 88, 12, 0.3)', dot: '#fb923c' };
    case 'RETURNED':
      return { label: 'RETURNED', bg: 'rgba(239, 68, 68, 0.12)', color: '#ef4444', border: 'rgba(239, 68, 68, 0.3)', dot: '#ef4444' };
    case 'DRAFT':
      return { label: 'DRAFT', bg: 'rgba(148, 163, 184, 0.12)', color: '#94a3b8', border: 'rgba(148, 163, 184, 0.3)', dot: '#94a3b8' };
    case 'REVIEW':
      return { label: 'UNDER REVIEW', bg: 'rgba(168, 85, 247, 0.12)', color: '#c084fc', border: 'rgba(168, 85, 247, 0.3)', dot: '#c084fc' };
    case 'VIEWED':
      return { label: 'VIEWED', bg: 'rgba(16, 185, 129, 0.12)', color: '#10b981', border: 'rgba(16, 185, 129, 0.3)', dot: '#10b981' };
    case 'NOT_RELEASED':
      return { label: 'NOT RELEASED', bg: 'rgba(100, 116, 139, 0.12)', color: '#94a3b8', border: 'rgba(100, 116, 139, 0.3)', dot: '#94a3b8' };
    case 'PENDING':
    case 'NOT_STARTED':
    default:
      return { label: 'PENDING', bg: 'rgba(100, 116, 139, 0.12)', color: '#94a3b8', border: 'rgba(100, 116, 139, 0.3)', dot: '#94a3b8' };
  }
});
</script>

<template>
  <span
    class="result-badge"
    :class="`size-${size}`"
    :style="{
      backgroundColor: config.bg,
      color: config.color,
      borderColor: config.border,
    }"
  >
    <span class="badge-dot" :style="{ backgroundColor: config.dot }" />
    <span class="badge-text">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.result-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  border-width: 1px;
  border-style: solid;
  border-radius: 9999px;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
  user-select: none;
  width: fit-content;
}

.size-sm {
  padding: 0.15rem 0.5rem;
  font-size: 0.6875rem;
}

.size-md {
  padding: 0.25rem 0.6875rem;
  font-size: 0.75rem;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-text {
  line-height: 1;
}
</style>
