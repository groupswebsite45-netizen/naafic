<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  entered: number;
  total: number;
  percentage?: number;
}>();

const calculatedPercentage = computed(() => {
  if (props.percentage !== undefined) return Math.min(100, Math.max(0, props.percentage));
  if (props.total <= 0) return 0;
  return Math.min(100, Math.round((props.entered / props.total) * 100));
});

const progressColor = computed(() => {
  const p = calculatedPercentage.value;
  if (p === 100) return '#10b981'; // complete
  if (p >= 60) return '#3b82f6';  // good progress
  if (p > 0) return '#f59e0b';   // in progress
  return '#cbd5e1';              // not started
});
</script>

<template>
  <div class="result-progress-container">
    <div class="progress-labels">
      <span class="counts">{{ entered }} / {{ total }}</span>
      <span class="percentage" :style="{ color: calculatedPercentage === 100 ? '#059669' : 'inherit' }">
        {{ calculatedPercentage }}%
      </span>
    </div>
    <div class="progress-track">
      <div
        class="progress-bar"
        :style="{
          width: `${calculatedPercentage}%`,
          backgroundColor: progressColor
        }"
      />
    </div>
  </div>
</template>

<style scoped>
.result-progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  min-width: 100px;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary, #64748b);
  line-height: 1;
}

.counts {
  color: var(--text-primary, #1e293b);
}

.percentage {
  font-size: 0.6875rem;
}

.progress-track {
  width: 100%;
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease, background-color 0.3s ease;
}
</style>
