<script setup lang="ts">
import { ExamFilterOptions } from '../../../../types/school';

defineProps<{
  query: string;
  academicYear: string;
  status: string;
  filterOptions: ExamFilterOptions | null;
  activeFilterCount: number;
}>();

const emit = defineEmits<{
  (e: 'update:query', value: string): void;
  (e: 'update:academicYear', value: string): void;
  (e: 'update:status', value: string): void;
  (e: 'open-filter-drawer'): void;
  (e: 'refresh'): void;
}>();
</script>

<template>
  <div class="exam-toolbar-container">
    <div class="search-box">
      <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
      </svg>
      <input
        type="text"
        :value="query"
        placeholder="Search exams by title or type..."
        class="search-input"
        @input="emit('update:query', ($event.target as HTMLInputElement).value)"
      />
      <button
        v-if="query"
        type="button"
        class="clear-search-btn"
        @click="emit('update:query', '')"
      >
        &times;
      </button>
    </div>

    <div class="quick-filters">
      <!-- Academic Year Filter -->
      <select
        :value="academicYear"
        class="toolbar-select"
        title="Filter by Academic Year"
        @change="emit('update:academicYear', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">All Academic Years</option>
        <option
          v-for="year in filterOptions?.academic_years || ['2025-2026', '2026-2027']"
          :key="year"
          :value="year"
        >
          {{ year }}
        </option>
      </select>

      <!-- Status Filter -->
      <select
        :value="status"
        class="toolbar-select"
        title="Filter by Status"
        @change="emit('update:status', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">All Statuses</option>
        <option value="DRAFT">Draft</option>
        <option value="SCHEDULED">Scheduled</option>
        <option value="ONGOING">Ongoing</option>
        <option value="COMPLETED">Completed</option>
        <option value="PUBLISHED">Published</option>
        <option value="CANCELLED">Cancelled</option>
      </select>

      <!-- Mobile/Advanced Filter Button -->
      <button
        type="button"
        class="filter-drawer-btn"
        @click="emit('open-filter-drawer')"
      >
        <svg class="filter-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
        </svg>
        <span>Filters</span>
        <span v-if="activeFilterCount > 0" class="filter-badge">
          {{ activeFilterCount }}
        </span>
      </button>

      <!-- Refresh Button -->
      <button
        type="button"
        class="refresh-btn"
        title="Refresh Data"
        @click="emit('refresh')"
      >
        <svg class="refresh-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.exam-toolbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.875rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 240px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 16px;
  height: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2rem 0.5rem 2.25rem;
  font-size: 0.875rem;
  color: var(--text-primary, #0f172a);
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.clear-search-btn {
  position: absolute;
  right: 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: none;
  background-color: #e2e8f0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1;
  cursor: pointer;
}

.quick-filters {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-shrink: 0;
}

.toolbar-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: var(--text-primary, #0f172a);
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 8px;
  cursor: pointer;
  outline: none;
}

.toolbar-select:focus {
  border-color: #4f46e5;
}

.filter-drawer-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary, #1e293b);
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-drawer-btn:hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

.filter-icon {
  width: 16px;
  height: 16px;
  color: #64748b;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: #4f46e5;
  color: #ffffff;
  border-radius: 50%;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: #64748b;
  background-color: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-btn:hover {
  background-color: #f8fafc;
  color: #0f172a;
}

.refresh-icon {
  width: 18px;
  height: 18px;
}

@media (max-width: 768px) {
  .exam-toolbar-container {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box {
    width: 100%;
  }
  .quick-filters {
    width: 100%;
    justify-content: space-between;
  }
  .toolbar-select {
    display: none; /* Hide compact selects in favor of filter drawer on mobile */
  }
  .filter-drawer-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
