<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  searchQuery: string;
  selectedYear: string;
  selectedDivision?: string;
  selectedStatus: string;
  selectedCapacity: string;
  activeFilterCount: number;
  years: string[];
}>();

const emit = defineEmits<{
  (e: 'update:searchQuery', value: string): void;
  (e: 'update:selectedYear', value: string): void;
  (e: 'update:selectedDivision', value: string): void;
  (e: 'update:selectedStatus', value: string): void;
  (e: 'update:selectedCapacity', value: string): void;
  (e: 'openFilters'): void;
  (e: 'resetFilters'): void;
}>();

const hasActiveFilters = computed(() => {
  return (
    Boolean(props.searchQuery) ||
    Boolean(props.selectedYear) ||
    Boolean(props.selectedDivision) ||
    Boolean(props.selectedStatus) ||
    Boolean(props.selectedCapacity) ||
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
          placeholder="Search by class name, code or section..."
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
        <!-- Division Select -->
        <select
          class="select-input"
          :value="selectedDivision"
          @change="emit('update:selectedDivision', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Divisions</option>
          <option value="PRIMARY">Primary Division</option>
          <option value="SECONDARY">Secondary Division</option>
        </select>

        <!-- Academic Year Select -->
        <select
          class="select-input"
          :value="selectedYear"
          @change="emit('update:selectedYear', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Academic Years</option>
          <option v-for="yr in years" :key="yr" :value="yr">
            {{ yr }}
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

        <!-- Capacity Select -->
        <select
          class="select-input"
          :value="selectedCapacity"
          @change="emit('update:selectedCapacity', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Capacity States</option>
          <option value="NORMAL">Available Seats</option>
          <option value="NEAR_CAPACITY">Near Capacity</option>
          <option value="FULL">Full</option>
          <option value="OVER_CAPACITY">Over Capacity</option>
        </select>
      </div>
    </div>

    <div class="toolbar-right">
      <!-- Filter Drawer Trigger Button -->
      <button
        type="button"
        class="filter-toggle-btn"
        :class="{ 'has-active': activeFilterCount > 0 }"
        @click="emit('openFilters')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
        </svg>
        <span>Filters</span>
        <span v-if="activeFilterCount > 0" class="filter-count-badge">
          {{ activeFilterCount }}
        </span>
      </button>

      <!-- Reset Button -->
      <button
        v-if="hasActiveFilters"
        type="button"
        class="reset-btn"
        title="Reset all filters"
        @click="emit('resetFilters')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
        </svg>
        <span>Reset</span>
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
  background-color: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 18px;
  padding: 0.95rem 1.25rem;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 #ffffff;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.toolbar-container:hover {
  border-color: #cbd5e1;
  box-shadow: 0 6px 22px -3px rgba(15, 23, 42, 0.07);
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
  max-width: 26rem;
  min-width: 12rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  width: 18px;
  height: 18px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 44px;
  padding: 0 2.25rem 0 2.75rem;
  background-color: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.88rem;
  color: #0f172a;
  font-weight: 500;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  background-color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.search-input::placeholder {
  color: #94a3b8;
}

.clear-search-btn {
  position: absolute;
  right: 0.75rem;
  background: transparent;
  border: none;
  padding: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
}

.clear-search-btn:hover {
  color: #0f172a;
}

.clear-search-btn svg {
  width: 1rem;
  height: 1rem;
}

.quick-selects {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.select-input {
  height: 44px;
  padding: 0 2.25rem 0 1rem;
  background-color: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.84rem;
  font-weight: 600;
  color: #334155;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='m19 9-7 7-7-7'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.85rem center;
  background-size: 14px;
  transition: all 0.2s ease;
}

.select-input:hover {
  background-color: #ffffff;
  border-color: #cbd5e1;
}

.select-input:focus {
  background-color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.filter-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  height: 44px;
  padding: 0 1rem;
  background-color: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.84rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-toggle-btn:hover {
  background-color: #ffffff;
  border-color: #cbd5e1;
  color: #0f172a;
}

.filter-toggle-btn.has-active {
  background-color: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}

.filter-toggle-btn svg {
  width: 1rem;
  height: 1rem;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 9999px;
  background-color: #2563eb;
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 700;
}

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  height: 40px;
  padding: 0 0.85rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #e11d48;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-btn:hover {
  background-color: #ffe4e6;
}

.reset-btn svg {
  width: 0.95rem;
  height: 0.95rem;
}

@media (max-width: 1024px) {
  .quick-selects {
    display: none;
  }
}

@media (max-width: 640px) {
  .toolbar-container {
    padding: 0.625rem 0.75rem;
  }

  .search-wrapper {
    max-width: 100%;
    min-width: 0;
  }

  .reset-btn span {
    display: none;
  }
}
</style>
