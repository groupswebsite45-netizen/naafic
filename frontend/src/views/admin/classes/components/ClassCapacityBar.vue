<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    enrolled: number;
    capacity: number;
    compact?: boolean;
    showLabel?: boolean;
  }>(),
  {
    compact: false,
    showLabel: true,
  }
);

const capacityValue = computed(() => Math.max(1, props.capacity || 1));
const percentage = computed(() => {
  return Math.round((props.enrolled / capacityValue.value) * 100);
});

const progressWidth = computed(() => {
  return Math.min(100, percentage.value);
});

const barColorClass = computed(() => {
  if (props.enrolled > props.capacity) return 'bar-danger';
  if (percentage.value >= 100) return 'bar-warning';
  if (percentage.value >= 85) return 'bar-amber';
  return 'bar-success';
});
</script>

<template>
  <div class="capacity-container" :class="{ 'is-compact': compact }">
    <div v-if="showLabel" class="capacity-header">
      <span class="capacity-text">
        <strong class="enrolled-num">{{ enrolled }}</strong>
        <span class="capacity-slash">/</span>
        <span class="total-num">{{ capacity }}</span>
        <span class="capacity-subtext">Students</span>
      </span>
      <span class="capacity-percentage-badge" :class="barColorClass">
        {{ percentage }}%
      </span>
    </div>

    <div class="progress-track" :title="`${enrolled} of ${capacity} enrolled (${percentage}%)`">
      <div
        class="progress-fill"
        :class="barColorClass"
        :style="{ width: `${progressWidth}%` }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.capacity-container {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 100%;
  min-width: 0;
}

.capacity-container.is-compact {
  gap: 0.25rem;
}

.capacity-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  line-height: 1.2;
}

.capacity-text {
  color: #334155;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.enrolled-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 0.88rem;
  color: #0f172a;
}

.capacity-slash {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.8rem;
}

.total-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 0.84rem;
  color: #475569;
}

.capacity-subtext {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  margin-left: 0.15rem;
}

.capacity-percentage-badge {
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  flex-shrink: 0;
  border: 1px solid transparent;
}

.progress-track {
  width: 100%;
  height: 7px;
  background-color: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.capacity-container.is-compact .progress-track {
  height: 5px;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Gradients and Badges */
.progress-fill.bar-success {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.35);
}

.capacity-percentage-badge.bar-success {
  background-color: #ecfdf5;
  color: #047857;
  border-color: #a7f3d0;
}

.progress-fill.bar-amber {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.35);
}

.capacity-percentage-badge.bar-amber {
  background-color: #fffbeb;
  color: #b45309;
  border-color: #fde68a;
}

.progress-fill.bar-warning {
  background: linear-gradient(90deg, #f97316 0%, #ea580c 100%);
  box-shadow: 0 1px 3px rgba(249, 115, 22, 0.35);
}

.capacity-percentage-badge.bar-warning {
  background-color: #fff7ed;
  color: #c2410c;
  border-color: #fed7aa;
}

.progress-fill.bar-danger {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.35);
}

.capacity-percentage-badge.bar-danger {
  background-color: #fef2f2;
  color: #b91c1c;
  border-color: #fecaca;
}
</style>
