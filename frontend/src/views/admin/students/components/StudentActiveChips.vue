<script setup lang="ts">
import { computed } from 'vue';
import { SchoolClass, StudentFilterParams } from '../../../../types/school';

const props = defineProps<{
  filters: StudentFilterParams;
  availableClasses: SchoolClass[];
}>();

const emit = defineEmits<{
  (e: 'remove', key: keyof StudentFilterParams): void;
  (e: 'clearAll'): void;
}>();

const chips = computed(() => {
  const list: { key: keyof StudentFilterParams; label: string; value: string }[] = [];

  if (props.filters.search?.trim()) {
    list.push({ key: 'search', label: 'Search', value: `"${props.filters.search.trim()}"` });
  }

  if (props.filters.academic_year) {
    list.push({ key: 'academic_year', label: 'Year', value: props.filters.academic_year });
  }

  if (props.filters.class_id) {
    const found = props.availableClasses.find((c) => c.id === Number(props.filters.class_id));
    list.push({
      key: 'class_id',
      label: 'Class',
      value: found ? `${found.name} (${found.code})` : `Class #${props.filters.class_id}`,
    });
  }

  if (props.filters.status) {
    list.push({ key: 'status', label: 'Status', value: props.filters.status });
  }

  if (props.filters.gender) {
    list.push({ key: 'gender', label: 'Gender', value: props.filters.gender });
  }

  if (props.filters.has_portal !== undefined) {
    list.push({
      key: 'has_portal',
      label: 'Portal',
      value: props.filters.has_portal ? 'Enabled' : 'Disabled',
    });
  }

  return list;
});
</script>

<template>
  <div v-if="chips.length > 0" class="active-chips-container" aria-label="Active Search & Filter Criteria">
    <span class="chips-label">ACTIVE FILTERS:</span>
    <div class="chips-list">
      <div v-for="chip in chips" :key="chip.key" class="filter-chip">
        <span class="chip-name">{{ chip.label }}:</span>
        <strong class="chip-val">{{ chip.value }}</strong>
        <button
          type="button"
          class="chip-remove-btn"
          :title="`Remove ${chip.label} filter`"
          :aria-label="`Remove ${chip.label} filter`"
          @click="emit('remove', chip.key)"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    <button type="button" class="btn-clear-all" aria-label="Clear all filters" @click="emit('clearAll')">
      Clear all
    </button>
  </div>
</template>

<style scoped>
.active-chips-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.875rem;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.chips-label {
  font-size: 0.71875rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.chips-list {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
  min-width: 0;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.6rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #1e40af;
  line-height: 1.2;
  box-sizing: border-box;
  max-width: 100%;
}

.chip-name {
  color: #3b82f6;
  font-weight: 500;
}

.chip-val {
  font-weight: 600;
  color: #1e3a8a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.chip-remove-btn {
  background: none;
  border: none;
  color: #3b82f6;
  width: 24px;
  height: 24px;
  padding: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.12s ease;
  margin-left: 0.15rem;
}

.chip-remove-btn:hover {
  color: #1d4ed8;
  background: #dbeafe;
}

.btn-clear-all {
  background: none;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #e11d48;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.12s ease;
  white-space: nowrap;
}

.btn-clear-all:hover {
  text-decoration: underline;
  background: #fff1f2;
}

@media (max-width: 480px) {
  .active-chips-container {
    gap: 0.375rem;
  }
  
  .filter-chip {
    padding: 0.2rem 0.5rem;
    font-size: 0.71875rem;
  }
}
</style>
