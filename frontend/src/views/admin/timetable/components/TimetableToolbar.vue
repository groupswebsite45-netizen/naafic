<script setup lang="ts">
import { computed } from 'vue';
import { SchoolClass, Teacher, Subject } from '../../../../types/school';

const props = defineProps<{
  academicYear: string;
  selectedClassId?: number;
  selectedTeacherId?: number;
  selectedSubjectId?: number;
  selectedDay?: string;
  selectedRoom?: string;
  currentView: 'weekly' | 'class' | 'teacher' | 'day';
  activeFilterCount: number;
  academicYears: string[];
  classes: SchoolClass[];
  teachers: Teacher[];
  subjects: Subject[];
  days: string[];
  rooms: string[];
}>();

const emit = defineEmits<{
  (e: 'update:academicYear', val: string): void;
  (e: 'update:selectedClassId', val?: number): void;
  (e: 'update:selectedTeacherId', val?: number): void;
  (e: 'update:selectedSubjectId', val?: number): void;
  (e: 'update:selectedDay', val?: string): void;
  (e: 'update:selectedRoom', val?: string): void;
  (e: 'update:currentView', val: 'weekly' | 'class' | 'teacher' | 'day'): void;
  (e: 'openFilters'): void;
  (e: 'resetFilters'): void;
}>();

const hasActiveFilters = computed(() => {
  return (
    Boolean(props.selectedClassId) ||
    Boolean(props.selectedTeacherId) ||
    Boolean(props.selectedSubjectId) ||
    Boolean(props.selectedDay) ||
    Boolean(props.selectedRoom) ||
    props.activeFilterCount > 0
  );
});
</script>

<template>
  <div class="timetable-toolbar-card">
    <div class="toolbar-top-row">
      <!-- Left: Academic Year + Quick Selects -->
      <div class="toolbar-left-group">
        <!-- Academic Year Dropdown -->
        <div class="academic-year-picker">
          <span class="year-label">Academic Year:</span>
          <select
            class="year-select"
            :value="academicYear"
            @change="emit('update:academicYear', ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="yr in academicYears" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Desktop Quick Selects -->
        <div class="quick-dropdowns">
          <!-- Class Select -->
          <select
            class="filter-select"
            :value="selectedClassId || ''"
            @change="emit('update:selectedClassId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined)"
          >
            <option value="">All Classes</option>
            <option v-for="c in classes" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>

          <!-- Teacher Select -->
          <select
            class="filter-select"
            :value="selectedTeacherId || ''"
            @change="emit('update:selectedTeacherId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined)"
          >
            <option value="">All Teachers</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">
              {{ t.first_name }} {{ t.last_name }}
            </option>
          </select>

          <!-- Day Select -->
          <select
            class="filter-select"
            :value="selectedDay || ''"
            @change="emit('update:selectedDay', ($event.target as HTMLSelectElement).value || undefined)"
          >
            <option value="">All Days</option>
            <option v-for="d in days" :key="d" :value="d">
              {{ d }}
            </option>
          </select>
        </div>
      </div>

      <!-- Right: View Switcher & Filter Drawer Button -->
      <div class="toolbar-right-group">
        <!-- View Switcher Segmented Control -->
        <div class="view-segmented-control">
          <button
            type="button"
            class="view-btn"
            :class="{ active: currentView === 'weekly' }"
            title="Weekly Timetable Grid"
            @click="emit('update:currentView', 'weekly')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect width="18" height="18" x="3" y="3" rx="2" />
              <path d="M3 9h18" />
              <path d="M3 15h18" />
              <path d="M9 3v18" />
              <path d="M15 3v18" />
            </svg>
            <span class="view-label">Weekly Grid</span>
          </button>

          <button
            type="button"
            class="view-btn"
            :class="{ active: currentView === 'class' }"
            title="Class-Focused Timetable"
            @click="emit('update:currentView', 'class')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h10" />
            </svg>
            <span class="view-label">Class View</span>
          </button>

          <button
            type="button"
            class="view-btn"
            :class="{ active: currentView === 'teacher' }"
            title="Teacher-Focused Timetable"
            @click="emit('update:currentView', 'teacher')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
            </svg>
            <span class="view-label">Teacher View</span>
          </button>

          <button
            type="button"
            class="view-btn"
            :class="{ active: currentView === 'day' }"
            title="Single Day View"
            @click="emit('update:currentView', 'day')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 14 14" />
            </svg>
            <span class="view-label">Day View</span>
          </button>
        </div>

        <!-- Filter Drawer Button -->
        <button
          type="button"
          class="drawer-toggle-btn"
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
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timetable-toolbar-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 0.875rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  width: 100%;
  box-sizing: border-box;
}

.toolbar-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.toolbar-left-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.academic-year-picker {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: #f8fafc;
  padding: 0.25rem 0.5rem 0.25rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  flex-shrink: 0;
}

.year-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.year-select {
  height: 1.875rem;
  background: transparent;
  border: none;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--brand-primary, #1e40af);
  outline: none;
  cursor: pointer;
  padding-right: 1.25rem;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%231e40af' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right center;
  background-size: 0.75rem;
}

.quick-dropdowns {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-select {
  height: 2.375rem;
  padding: 0 1.875rem 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-main, #0f172a);
  background-color: #f8fafc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.625rem center;
  background-size: 0.8125rem;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.filter-select:focus {
  background-color: #ffffff;
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.toolbar-right-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  flex-wrap: wrap;
}

/* Segmented View Switcher */
.view-segmented-control {
  display: inline-flex;
  align-items: center;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid #e2e8f0;
}

.view-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.35rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.view-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.view-btn.active {
  background: #ffffff;
  color: var(--brand-primary, #1e40af);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.drawer-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #0f172a;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.drawer-toggle-btn:hover {
  background: #ffffff;
  border-color: #94a3b8;
  color: var(--brand-primary, #1e40af);
}

.drawer-toggle-btn.has-active {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1e40af;
}

.drawer-toggle-btn svg {
  width: 0.875rem;
  height: 0.875rem;
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

.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.375rem;
  height: 2.375rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.reset-btn:hover {
  background: #fef2f2;
  border-color: #fecaca;
  color: #ef4444;
}

.reset-btn svg {
  width: 0.9375rem;
  height: 0.9375rem;
}

@media (max-width: 992px) {
  .quick-dropdowns {
    display: none;
  }
}

@media (max-width: 640px) {
  .view-label {
    display: none;
  }

  .view-btn {
    padding: 0.35rem 0.5rem;
  }

  .toolbar-top-row {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-right-group {
    justify-content: space-between;
  }
}
</style>
