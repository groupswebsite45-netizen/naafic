<script setup lang="ts">
interface Props {
  modelValue: string;
  options: string[];
  disabled?: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'change', value: string): void;
}>();

function onSelect(event: Event) {
  const target = event.target as HTMLSelectElement;
  emit('update:modelValue', target.value);
  emit('change', target.value);
}
</script>

<template>
  <div class="selector-group">
    <label class="selector-label">
      <svg class="label-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span>EXAMINATION SERIES</span>
    </label>
    <div class="select-wrapper">
      <select
        :value="modelValue"
        class="custom-select"
        :disabled="disabled"
        aria-label="Select Examination Series"
        @change="onSelect"
      >
        <option v-for="ex in options" :key="ex" :value="ex">
          {{ ex }}
        </option>
      </select>
      <svg class="chevron-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.selector-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 220px;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #94a3b8;
  text-transform: uppercase;
}

.label-icon {
  width: 0.875rem;
  height: 0.875rem;
  color: #a855f7;
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.custom-select {
  width: 100%;
  appearance: none;
  background-color: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.6rem 2.25rem 0.6rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease-in-out;
}

.custom-select:hover:not(:disabled) {
  border-color: #9333ea;
  background-color: #1e293b;
}

.custom-select:focus {
  border-color: #c084fc;
  box-shadow: 0 0 0 3px rgba(192, 132, 252, 0.2);
}

.custom-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chevron-icon {
  position: absolute;
  right: 0.75rem;
  width: 1rem;
  height: 1rem;
  color: #94a3b8;
  pointer-events: none;
}
</style>
