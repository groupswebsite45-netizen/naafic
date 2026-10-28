<script setup lang="ts">
import { reactive, watch, computed } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  years: string[];
  initialFilters: {
    academic_year: string;
    division?: string;
    status: string;
    level: string;
    section: string;
    capacity_filter: string;
  };
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'apply', filters: typeof props.initialFilters): void;
  (e: 'reset'): void;
}>();

const primaryLevels = [
  'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4',
  'Grade 5', 'Grade 6', 'Grade 7', 'Grade 8'
];

const secondaryLevels = [
  'Form 1', 'Form 2', 'Form 3', 'Form 4'
];

const localFilters = reactive({
  academic_year: '',
  division: '',
  status: '',
  level: '',
  section: '',
  capacity_filter: '',
});

const availableLevels = computed(() => {
  if (localFilters.division === 'PRIMARY') return primaryLevels;
  if (localFilters.division === 'SECONDARY') return secondaryLevels;
  return [...primaryLevels, ...secondaryLevels];
});

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      localFilters.academic_year = props.initialFilters.academic_year || '';
      localFilters.division = props.initialFilters.division || '';
      localFilters.status = props.initialFilters.status || '';
      localFilters.level = props.initialFilters.level || '';
      localFilters.section = props.initialFilters.section || '';
      localFilters.capacity_filter = props.initialFilters.capacity_filter || '';
    }
  },
  { immediate: true }
);

function handleApply() {
  emit('apply', { ...localFilters });
  emit('close');
}

function handleReset() {
  localFilters.academic_year = '';
  localFilters.division = '';
  localFilters.status = '';
  localFilters.level = '';
  localFilters.section = '';
  localFilters.capacity_filter = '';
  emit('reset');
  emit('close');
}
</script>

<template>
  <div v-if="isOpen" class="drawer-overlay" @click.self="emit('close')">
    <div class="drawer-panel">
      <!-- Header -->
      <div class="drawer-header">
        <div class="drawer-title-group">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          <h3 class="drawer-title">Filter Classes</h3>
        </div>
        <button type="button" class="drawer-close-btn" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Body Form -->
      <div class="drawer-body">
        <!-- Academic Year -->
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="localFilters.academic_year" class="form-select">
            <option value="">All Academic Years</option>
            <option v-for="yr in years" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Academic Division -->
        <div class="form-group">
          <label class="form-label">Academic Division</label>
          <select v-model="localFilters.division" class="form-select">
            <option value="">All Academic Divisions</option>
            <option value="PRIMARY">Primary Division (Grades 1–8)</option>
            <option value="SECONDARY">Secondary Division (Forms 1–4)</option>
          </select>
        </div>

        <!-- Status -->
        <div class="form-group">
          <label class="form-label">Status</label>
          <select v-model="localFilters.status" class="form-select">
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>

        <!-- Class Level / Grade -->
        <div class="form-group">
          <label class="form-label">Level / Grade</label>
          <select v-model="localFilters.level" class="form-select">
            <option value="">All Levels</option>
            <option v-for="lvl in availableLevels" :key="lvl" :value="lvl">
              {{ lvl }}
            </option>
          </select>
        </div>

        <!-- Section / Stream -->
        <div class="form-group">
          <label class="form-label">Section / Stream</label>
          <input
            v-model="localFilters.section"
            type="text"
            class="form-input"
            placeholder="e.g. A, B, C, Stream North..."
          />
        </div>

        <!-- Capacity State -->
        <div class="form-group">
          <label class="form-label">Capacity Utilization</label>
          <select v-model="localFilters.capacity_filter" class="form-select">
            <option value="">All Capacity States</option>
            <option value="NORMAL">Available Seats (< 85%)</option>
            <option value="NEAR_CAPACITY">Near Capacity (85% - 99%)</option>
            <option value="FULL">Full (100%)</option>
            <option value="OVER_CAPACITY">Over Capacity (> 100%)</option>
          </select>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="drawer-footer">
        <button type="button" class="btn-secondary" @click="handleReset">
          Reset Filters
        </button>
        <button type="button" class="btn-primary" @click="handleApply">
          Apply Filters
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.15s ease-out;
}

.drawer-panel {
  width: 100%;
  max-width: 24rem;
  height: 100%;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  box-sizing: border-box;
  animation: slideInRight 0.2s ease-out;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.drawer-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #0f172a;
  min-width: 0;
}

.drawer-title-group svg {
  width: 1.25rem;
  height: 1.25rem;
  color: #2563eb;
  flex-shrink: 0;
}

.drawer-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.drawer-close-btn {
  background: transparent;
  border: none;
  min-width: 44px;
  min-height: 44px;
  color: #64748b;
  cursor: pointer;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.12s ease;
}

.drawer-close-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.drawer-close-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.drawer-body {
  padding: 1.25rem;
  flex: 1 1 0%;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
  box-sizing: border-box;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-select,
.form-input {
  width: 100%;
  height: 40px;
  padding: 0 0.75rem;
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.form-select:focus,
.form-input:focus {
  background-color: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.drawer-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
}

.btn-secondary {
  height: 40px;
  padding: 0 1.25rem;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-secondary:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-primary {
  height: 40px;
  padding: 0 1.25rem;
  background-color: #2563eb;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

@media (max-width: 640px) {
  .drawer-panel {
    max-width: 100%;
    height: auto;
    max-height: 85vh;
    border-radius: 1rem 1rem 0 0;
    margin-top: auto;
    animation: slideInUp 0.2s ease-out;
  }

  .drawer-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    height: 44px;
  }

  @keyframes slideInUp {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
  }
}
</style>
