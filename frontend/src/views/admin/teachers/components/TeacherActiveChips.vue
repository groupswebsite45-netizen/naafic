<script setup lang="ts">
import { computed } from 'vue';
import { SchoolClass, Subject, TeacherFilterParams } from '../../../../types/school';

const props = defineProps<{
  filters: TeacherFilterParams;
  availableClasses: SchoolClass[];
  availableSubjects: Subject[];
}>();

const emit = defineEmits<{
  (e: 'remove', key: keyof TeacherFilterParams): void;
  (e: 'clearAll'): void;
}>();

const activeChips = computed(() => {
  const chips: Array<{ key: keyof TeacherFilterParams; label: string; value: string }> = [];

  if (props.filters.search?.trim()) {
    chips.push({ key: 'search', label: 'Search', value: `"${props.filters.search.trim()}"` });
  }

  if (props.filters.class_id) {
    const cls = props.availableClasses.find((c) => c.id === props.filters.class_id);
    chips.push({ key: 'class_id', label: 'Class', value: cls ? `${cls.name} (${cls.code})` : `Class #${props.filters.class_id}` });
  }

  if (props.filters.subject_id) {
    const sub = props.availableSubjects.find((s) => s.id === props.filters.subject_id);
    chips.push({ key: 'subject_id', label: 'Subject', value: sub ? sub.name : `Subject #${props.filters.subject_id}` });
  }

  if (props.filters.status) {
    chips.push({ key: 'status', label: 'Status', value: props.filters.status });
  }

  if (props.filters.has_portal !== undefined) {
    chips.push({ key: 'has_portal', label: 'Portal', value: props.filters.has_portal ? 'Enabled' : 'Not Created' });
  }

  if (props.filters.academic_year) {
    chips.push({ key: 'academic_year', label: 'Year', value: props.filters.academic_year });
  }

  return chips;
});
</script>

<template>
  <div v-if="activeChips.length > 0" class="chips-container">
    <span class="chips-title">Active Filters:</span>
    <div class="chips-wrap">
      <div v-for="chip in activeChips" :key="chip.key" class="filter-chip">
        <span class="chip-label">{{ chip.label }}:</span>
        <span class="chip-value">{{ chip.value }}</span>
        <button
          type="button"
          class="chip-remove"
          :title="`Remove ${chip.label} filter`"
          @click="emit('remove', chip.key)"
        >
          &times;
        </button>
      </div>

      <button type="button" class="btn-clear-all" @click="emit('clearAll')">
        Clear all
      </button>
    </div>
  </div>
</template>

<style scoped>
.chips-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.625rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.chips-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}

.chips-wrap {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  color: #334155;
}

.chip-label {
  font-weight: 600;
  color: #64748b;
}

.chip-value {
  font-weight: 600;
  color: #0f172a;
}

.chip-remove {
  background: none;
  border: none;
  color: #64748b;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  line-height: 1;
}

.chip-remove:hover {
  color: #e11d48;
}

.btn-clear-all {
  background: none;
  border: none;
  font-size: 0.72rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  padding: 0.15rem 0.35rem;
  text-decoration: underline;
}

.btn-clear-all:hover {
  color: #1d4ed8;
}
</style>
