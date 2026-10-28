<script setup lang="ts">
import { computed } from 'vue';
import { SchoolClass } from '../../../../types/school';

const props = withDefaults(
  defineProps<{
    search: string;
    classId: number | string;
    academicYear?: string;
    availableYears?: string[];
    status: string;
    activeFiltersCount: number;
    availableClasses: SchoolClass[];
    isLoading: boolean;
  }>(),
  {
    academicYear: '',
    availableYears: () => ['2026/2027', '2025/2026', '2027/2028'],
  }
);

const emit = defineEmits<{
  (e: 'update:search', val: string): void;
  (e: 'update:classId', val: number | string): void;
  (e: 'update:academicYear', val: string): void;
  (e: 'update:status', val: string): void;
  (e: 'openDrawer'): void;
  (e: 'resetFilters'): void;
}>();

const hasActiveFilters = computed(() => {
  return (
    props.search.trim() !== '' ||
    props.classId !== '' ||
    props.academicYear !== '' ||
    props.status !== '' ||
    props.activeFiltersCount > 0
  );
});
</script>

<template>
  <div class="toolbar-box">
    <!-- Desktop / Laptop View (>=1024px) -->
    <div class="toolbar-desktop hide-under-1024">
      <!-- Search Input -->
      <div class="search-input-wrap">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          :value="search"
          type="text"
          placeholder="Search by name, admission #, guardian, phone..."
          class="search-input"
          aria-label="Search students"
          @input="emit('update:search', ($event.target as HTMLInputElement).value)"
        />
        <button
          v-if="search"
          type="button"
          class="clear-btn"
          title="Clear search"
          aria-label="Clear search"
          @click="emit('update:search', '')"
        >
          &times;
        </button>
      </div>

      <!-- Quick Filter Dropdowns -->
      <div class="quick-dropdowns">
        <!-- Academic Year Dropdown -->
        <select
          :value="academicYear"
          class="select-control"
          title="Filter by Academic Year"
          aria-label="Filter by Academic Year"
          @change="emit('update:academicYear', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Academic Years</option>
          <option v-for="yr in availableYears" :key="yr" :value="yr">
            {{ yr }}
          </option>
        </select>

        <!-- Class Dropdown -->
        <select
          :value="classId"
          class="select-control"
          title="Filter by Class"
          aria-label="Filter by Class"
          @change="emit('update:classId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : '')"
        >
          <option value="">All Classes</option>
          <option v-for="c in availableClasses" :key="c.id" :value="c.id">
            {{ c.name }} ({{ c.code }})
          </option>
        </select>

        <!-- Status Dropdown -->
        <select
          :value="status"
          class="select-control"
          title="Filter by Status"
          aria-label="Filter by Status"
          @change="emit('update:status', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
          <option value="SUSPENDED">Suspended</option>
          <option value="GRADUATED">Graduated</option>
        </select>
      </div>

      <!-- Filter Drawer & Reset Buttons -->
      <div class="toolbar-actions">
        <button
          type="button"
          class="btn-filters-toggle"
          :class="{ active: activeFiltersCount > 0 }"
          aria-label="Open advanced filters"
          @click="emit('openDrawer')"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span class="btn-text">Filters</span>
          <span v-if="activeFiltersCount > 0" class="filter-count-badge">{{ activeFiltersCount }}</span>
        </button>

        <button
          v-if="hasActiveFilters"
          type="button"
          class="btn-reset-toolbar"
          title="Reset all filters"
          aria-label="Reset all filters"
          @click="emit('resetFilters')"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Reset</span>
        </button>
      </div>
    </div>

    <!-- Tablet / Mobile Responsive Layout (<1024px) -->
    <div class="toolbar-mobile-tablet hide-above-1024">
      <!-- Search Input Full Width -->
      <div class="search-input-wrap mobile-search-wrap">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          :value="search"
          type="text"
          placeholder="Search students..."
          class="search-input mobile-search-input"
          aria-label="Search students"
          @input="emit('update:search', ($event.target as HTMLInputElement).value)"
        />
        <button
          v-if="search"
          type="button"
          class="clear-btn mobile-clear-btn"
          title="Clear search"
          aria-label="Clear search"
          @click="emit('update:search', '')"
        >
          &times;
        </button>
      </div>

      <!-- Quick Filter Selects Grid (2 columns on mobile/tablet) -->
      <div class="mobile-filters-grid">
        <!-- Academic Year -->
        <div class="mobile-filter-col">
          <select
            :value="academicYear"
            class="select-control mobile-select"
            aria-label="Filter by Academic Year"
            @change="emit('update:academicYear', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">All Academic Years</option>
            <option v-for="yr in availableYears" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Class -->
        <div class="mobile-filter-col">
          <select
            :value="classId"
            class="select-control mobile-select"
            aria-label="Filter by Class"
            @change="emit('update:classId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : '')"
          >
            <option value="">All Classes</option>
            <option v-for="c in availableClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>

        <!-- Status -->
        <div class="mobile-filter-col">
          <select
            :value="status"
            class="select-control mobile-select"
            aria-label="Filter by Status"
            @change="emit('update:status', ($event.target as HTMLSelectElement).value)"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SUSPENDED">Suspended</option>
            <option value="GRADUATED">Graduated</option>
          </select>
        </div>

        <!-- Filter Drawer Button -->
        <div class="mobile-filter-col">
          <button
            type="button"
            class="btn-filters-toggle mobile-filter-btn"
            :class="{ active: activeFiltersCount > 0 }"
            aria-label="More filters"
            @click="emit('openDrawer')"
          >
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span class="btn-text">More Filters</span>
            <span v-if="activeFiltersCount > 0" class="filter-count-badge">{{ activeFiltersCount }}</span>
          </button>
        </div>
      </div>

      <!-- Reset Filter Button on Mobile (Full Width or compact) -->
      <div v-if="hasActiveFilters" class="mobile-reset-row">
        <button
          type="button"
          class="btn-reset-mobile"
          @click="emit('resetFilters')"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Reset All Filters</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar-box {
  background: #FFFFFF;
  border-radius: 18px;
  border: 1.5px solid #E2E8F0;
  padding: 0.95rem 1.25rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.04), inset 0 1px 0 #FFFFFF;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.toolbar-box:hover {
  border-color: #CBD5E1;
  box-shadow: 0 6px 22px -3px rgba(15, 23, 42, 0.07);
}

/* Desktop View */
.toolbar-desktop {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  box-sizing: border-box;
}

.search-input-wrap {
  position: relative;
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  align-items: center;
  box-sizing: border-box;
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
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.88rem;
  color: #0f172a;
  font-weight: 500;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  background: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  color: #0f172a;
}

.quick-dropdowns {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-shrink: 0;
}

.select-control {
  height: 44px;
  padding: 0 2.25rem 0 1rem;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.84rem;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.85rem center;
  background-size: 14px;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.select-control:hover {
  background-color: #ffffff;
  border-color: #cbd5e1;
}

.select-control:focus {
  background-color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-filters-toggle {
  height: 44px;
  padding: 0 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.84rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-sizing: border-box;
}

.btn-filters-toggle:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #0f172a;
}

.btn-filters-toggle.active {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: #2563eb;
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 9999px;
}

.btn-reset-toolbar {
  height: 40px;
  padding: 0 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #e11d48;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
  white-space: nowrap;
}

.btn-reset-toolbar:hover {
  background: #ffe4e6;
}

/* Mobile / Tablet View */
.toolbar-mobile-tablet {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  width: 100%;
  box-sizing: border-box;
}

.mobile-search-wrap {
  width: 100%;
}

.mobile-filters-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  width: 100%;
  box-sizing: border-box;
}

.mobile-filter-col {
  min-width: 0;
  width: 100%;
}

.mobile-select {
  width: 100%;
  height: 42px;
  font-size: 0.8125rem;
}

.mobile-filter-btn {
  width: 100%;
  height: 42px;
}

.mobile-reset-row {
  width: 100%;
}

.btn-reset-mobile {
  width: 100%;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  font-size: 0.78125rem;
  font-weight: 600;
  color: #e11d48;
  cursor: pointer;
  transition: all 0.12s ease;
  box-sizing: border-box;
}

.btn-reset-mobile:hover {
  background: #ffe4e6;
}

/* Visibility classes */
@media (min-width: 1024px) {
  .hide-above-1024 {
    display: none !important;
  }
}

@media (max-width: 1023px) {
  .hide-under-1024 {
    display: none !important;
  }
}

/* Ultra-compact mobile (<360px) */
@media (max-width: 359px) {
  .mobile-filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
