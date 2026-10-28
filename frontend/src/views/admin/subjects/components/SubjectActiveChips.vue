<script setup lang="ts">
defineProps<{
  department: string;
  status: string;
  section: string;
  assignmentState: string;
  search: string;
}>();

const emit = defineEmits<{
  (e: 'removeDepartment'): void;
  (e: 'removeStatus'): void;
  (e: 'removeSection'): void;
  (e: 'removeAssignmentState'): void;
  (e: 'removeSearch'): void;
  (e: 'clearAll'): void;
}>();
</script>

<template>
  <div
    v-if="department || status || section || assignmentState || search"
    class="active-chips-bar"
  >
    <span class="chips-label">Active Filters:</span>

    <div class="chips-list">
      <!-- Search Filter Chip -->
      <div v-if="search" class="filter-chip">
        <span class="chip-key">Search:</span>
        <span class="chip-val">"{{ search }}"</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove search filter"
          @click="emit('removeSearch')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Department Filter Chip -->
      <div v-if="department" class="filter-chip">
        <span class="chip-key">Department:</span>
        <span class="chip-val">{{ department }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove department filter"
          @click="emit('removeDepartment')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Status Filter Chip -->
      <div v-if="status" class="filter-chip">
        <span class="chip-key">Status:</span>
        <span class="chip-val">{{ status }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove status filter"
          @click="emit('removeStatus')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Section Filter Chip -->
      <div v-if="section" class="filter-chip">
        <span class="chip-key">Section:</span>
        <span class="chip-val">{{ section }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove section filter"
          @click="emit('removeSection')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Assignment State Filter Chip -->
      <div v-if="assignmentState" class="filter-chip">
        <span class="chip-key">Allocation:</span>
        <span class="chip-val">{{ assignmentState === 'ASSIGNED' ? 'Assigned Classes' : 'Unassigned' }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove allocation filter"
          @click="emit('removeAssignmentState')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Clear All Button -->
      <button
        type="button"
        class="clear-all-chips-btn"
        @click="emit('clearAll')"
      >
        Clear all
      </button>
    </div>
  </div>
</template>

<style scoped>
.active-chips-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.5rem 0.25rem;
  width: 100%;
  box-sizing: border-box;
}

.chips-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
  flex-shrink: 0;
}

.chips-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  height: 1.625rem;
  padding: 0 0.5rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #1e293b;
  box-sizing: border-box;
}

.chip-key {
  color: #64748b;
  font-weight: 500;
}

.chip-val {
  font-weight: 600;
}

.remove-chip-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  padding: 0;
  margin-left: 0.125rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  border-radius: 9999px;
  transition: all 0.15s ease;
}

.remove-chip-btn:hover {
  background: #cbd5e1;
  color: #0f172a;
}

.remove-chip-btn svg {
  width: 0.75rem;
  height: 0.75rem;
}

.clear-all-chips-btn {
  background: none;
  border: none;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s ease;
}

.clear-all-chips-btn:hover {
  color: #1d4ed8;
}
</style>
