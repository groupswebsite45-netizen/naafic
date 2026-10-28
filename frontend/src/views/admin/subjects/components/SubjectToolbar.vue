<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  searchQuery: string;
  selectedDepartment: string;
  selectedStatus: string;
  selectedSection: string;
  selectedAssignmentState: string;
  activeFilterCount: number;
  departments: string[];
}>();

const emit = defineEmits<{
  (e: 'update:searchQuery', value: string): void;
  (e: 'update:selectedDepartment', value: string): void;
  (e: 'update:selectedStatus', value: string): void;
  (e: 'update:selectedSection', value: string): void;
  (e: 'update:selectedAssignmentState', value: string): void;
  (e: 'openFilters'): void;
  (e: 'resetFilters'): void;
}>();

const hasActiveFilters = computed(() => {
  return (
    Boolean(props.searchQuery) ||
    Boolean(props.selectedDepartment) ||
    Boolean(props.selectedStatus) ||
    Boolean(props.selectedSection) ||
    Boolean(props.selectedAssignmentState) ||
    props.activeFilterCount > 0
  );
});
</script>

<template>
  <div class="toolbar-container">
    <div class="toolbar-left">
      <!-- Search Input -->
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          type="text"
          class="search-input"
          placeholder="Search by subject name, code or department..."
          :value="searchQuery"
          @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
        />
        <button
          v-if="searchQuery"
          type="button"
          class="clear-search-btn"
          title="Clear search"
          @click="emit('update:searchQuery', '')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Quick Dropdowns (Desktop & Tablet) -->
      <div class="quick-selects">
        <!-- Department Select -->
        <select
          class="select-input"
          :value="selectedDepartment"
          @change="emit('update:selectedDepartment', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">
            {{ dept }}
          </option>
        </select>

        <!-- Status Select -->
        <select
          class="select-input"
          :value="selectedStatus"
          @change="emit('update:selectedStatus', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
          <option value="ARCHIVED">Archived</option>
        </select>

        <!-- Assignment State Select -->
        <select
          class="select-input"
          :value="selectedAssignmentState"
          @change="emit('update:selectedAssignmentState', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Allocations</option>
          <option value="ASSIGNED">Assigned Classes</option>
          <option value="UNASSIGNED">Unassigned</option>
        </select>
      </div>
    </div>

    <div class="toolbar-right">
      <!-- Filter Button (Opens Drawer on Mobile/Tablet or for Extended Filters) -->
      <button
        type="button"
        class="filter-toggle-btn"
        :class="{ 'has-active': activeFilterCount > 0 }"
        @click="emit('openFilters')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
        </svg>
        <span class="btn-label">Filters</span>
        <span v-if="activeFilterCount > 0" class="filter-count-badge">
          {{ activeFilterCount }}
        </span>
      </button>

      <!-- Reset Filters Button -->
      <button
        v-if="hasActiveFilters"
        type="button"
        class="reset-filters-btn"
        title="Reset all search and filter criteria"
        @click="emit('resetFilters')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
        </svg>
        <span class="btn-label">Reset</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.toolbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
  width: 100%;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 180px;
  max-width: 420px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 1rem;
  height: 1rem;
  color: var(--text-muted, #94a3b8);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 2.375rem;
  padding: 0 2.25rem 0 2.25rem;
  font-size: 0.875rem;
  color: var(--text-main, #0f172a);
  background: var(--bg-main, #f8fafc);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.search-input:focus {
  background: #ffffff;
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.search-input::placeholder {
  color: var(--text-muted, #94a3b8);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  background: none;
  border: none;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  border-radius: 9999px;
  transition: all 0.15s ease;
}

.clear-search-btn:hover {
  background: var(--border-color, #e2e8f0);
  color: var(--text-main, #0f172a);
}

.clear-search-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.quick-selects {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.select-input {
  height: 2.375rem;
  padding: 0 2rem 0 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-main, #0f172a);
  background-color: var(--bg-main, #f8fafc);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.625rem center;
  background-size: 0.875rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.select-input:focus {
  background-color: #ffffff;
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.filter-toggle-btn,
.reset-filters-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid var(--border-color, #e2e8f0);
  background: var(--bg-main, #f8fafc);
  color: var(--text-main, #0f172a);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.filter-toggle-btn:hover,
.reset-filters-btn:hover {
  background: #ffffff;
  border-color: var(--border-focus, #cbd5e1);
  color: var(--brand-primary, #1e40af);
}

.filter-toggle-btn svg,
.reset-filters-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.filter-toggle-btn.has-active {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1e40af;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.125rem;
  height: 1.125rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background: #1e40af;
  color: #ffffff;
  border-radius: 9999px;
  line-height: 1;
}

.reset-filters-btn {
  color: var(--text-muted, #64748b);
}

.reset-filters-btn:hover {
  color: var(--danger, #ef4444);
  border-color: #fecaca;
  background: #fef2f2;
}

@media (max-width: 912px) {
  .quick-selects {
    display: none;
  }

  .search-wrapper {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .toolbar-container {
    padding: 0.75rem;
  }

  .btn-label {
    display: none;
  }

  .filter-toggle-btn,
  .reset-filters-btn {
    padding: 0 0.625rem;
  }
}
</style>
