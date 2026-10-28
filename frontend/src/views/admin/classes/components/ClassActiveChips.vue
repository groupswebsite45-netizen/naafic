<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  searchQuery: string;
  selectedYear: string;
  selectedDivision?: string;
  selectedStatus: string;
  selectedLevel: string;
  selectedSection: string;
  selectedCapacity: string;
}>();

const emit = defineEmits<{
  (e: 'removeSearch'): void;
  (e: 'removeYear'): void;
  (e: 'removeDivision'): void;
  (e: 'removeStatus'): void;
  (e: 'removeLevel'): void;
  (e: 'removeSection'): void;
  (e: 'removeCapacity'): void;
  (e: 'clearAll'): void;
}>();

const capacityLabel = computed(() => {
  switch (props.selectedCapacity) {
    case 'NORMAL': return 'Available Seats';
    case 'NEAR_CAPACITY': return 'Near Capacity';
    case 'FULL': return 'Full';
    case 'OVER_CAPACITY': return 'Over Capacity';
    default: return props.selectedCapacity;
  }
});

const hasChips = computed(() => {
  return (
    Boolean(props.searchQuery) ||
    Boolean(props.selectedYear) ||
    Boolean(props.selectedDivision) ||
    Boolean(props.selectedStatus) ||
    Boolean(props.selectedLevel) ||
    Boolean(props.selectedSection) ||
    Boolean(props.selectedCapacity)
  );
});
</script>

<template>
  <div v-if="hasChips" class="chips-container">
    <span class="chips-label">Active Filters:</span>

    <!-- Search Query Chip -->
    <div v-if="searchQuery" class="chip">
      <span class="chip-text">Search: <strong>"{{ searchQuery }}"</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeSearch')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Division Chip -->
    <div v-if="selectedDivision" class="chip">
      <span class="chip-text">Division: <strong>{{ selectedDivision }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeDivision')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Year Chip -->
    <div v-if="selectedYear" class="chip">
      <span class="chip-text">Year: <strong>{{ selectedYear }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeYear')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Status Chip -->
    <div v-if="selectedStatus" class="chip">
      <span class="chip-text">Status: <strong>{{ selectedStatus }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeStatus')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Level Chip -->
    <div v-if="selectedLevel" class="chip">
      <span class="chip-text">Level: <strong>{{ selectedLevel }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeLevel')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Section Chip -->
    <div v-if="selectedSection" class="chip">
      <span class="chip-text">Section: <strong>{{ selectedSection }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeSection')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Capacity Chip -->
    <div v-if="selectedCapacity" class="chip">
      <span class="chip-text">Capacity: <strong>{{ capacityLabel }}</strong></span>
      <button type="button" class="chip-remove" title="Remove filter" @click="emit('removeCapacity')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
      </button>
    </div>

    <!-- Clear All Button -->
    <button type="button" class="clear-all-btn" @click="emit('clearAll')">
      Clear all
    </button>
  </div>
</template>

<style scoped>
.chips-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.25rem 0;
  width: 100%;
}

.chips-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  margin-right: 0.25rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  color: #334155;
  user-select: none;
}

.chip-text strong {
  font-weight: 600;
  color: #0f172a;
}

.chip-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  padding: 0;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 50%;
}

.chip-remove:hover {
  color: #ef4444;
}

.chip-remove svg {
  width: 0.75rem;
  height: 0.75rem;
}

.clear-all-btn {
  background: transparent;
  border: none;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  border-radius: 0.25rem;
}

.clear-all-btn:hover {
  text-decoration: underline;
  color: #1d4ed8;
}
</style>
