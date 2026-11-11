<script setup lang="ts">
import { computed } from 'vue';

interface FilterState {
  query?: string;
  academic_year?: string;
  exam_type?: string;
  class_id?: number;
  subject_id?: number;
  status?: string;
}

const props = defineProps<{
  filters: FilterState;
  classLookup?: Record<number, string>;
  subjectLookup?: Record<number, string>;
}>();

const emit = defineEmits<{
  (e: 'remove', key: keyof FilterState): void;
  (e: 'clear-all'): void;
}>();

const activeChips = computed(() => {
  const chips: { key: keyof FilterState; label: string; value: string }[] = [];

  if (props.filters.query) {
    chips.push({ key: 'query', label: 'Search', value: props.filters.query });
  }
  if (props.filters.academic_year) {
    chips.push({ key: 'academic_year', label: 'Year', value: props.filters.academic_year });
  }
  if (props.filters.exam_type) {
    chips.push({ key: 'exam_type', label: 'Type', value: props.filters.exam_type });
  }
  if (props.filters.class_id) {
    const className = props.classLookup?.[props.filters.class_id] || `Class #${props.filters.class_id}`;
    chips.push({ key: 'class_id', label: 'Class', value: className });
  }
  if (props.filters.subject_id) {
    const subjectName = props.subjectLookup?.[props.filters.subject_id] || `Subject #${props.filters.subject_id}`;
    chips.push({ key: 'subject_id', label: 'Subject', value: subjectName });
  }
  if (props.filters.status) {
    chips.push({ key: 'status', label: 'Status', value: props.filters.status });
  }

  return chips;
});
</script>

<template>
  <div v-if="activeChips.length > 0" class="active-chips-bar">
    <span class="chips-title">Active Filters:</span>
    <div class="chips-list">
      <div v-for="chip in activeChips" :key="chip.key" class="filter-chip">
        <span class="chip-label">{{ chip.label }}:</span>
        <span class="chip-value">{{ chip.value }}</span>
        <button
          type="button"
          class="chip-remove-btn"
          title="Remove filter"
          @click="emit('remove', chip.key)"
        >
          &times;
        </button>
      </div>

      <button
        type="button"
        class="clear-all-btn"
        @click="emit('clear-all')"
      >
        Clear All
      </button>
    </div>
  </div>
</template>

<style scoped>
.active-chips-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.875rem;
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  flex-wrap: wrap;
}

.chips-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.chips-list {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.chip-label {
  font-weight: 500;
  color: #64748b;
}

.chip-value {
  font-weight: 600;
  color: #0f172a;
}

.chip-remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-left: 0.15rem;
  border-radius: 50%;
  border: none;
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip-remove-btn:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

.clear-all-btn {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #4f46e5;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.clear-all-btn:hover {
  text-decoration: underline;
}
</style>
