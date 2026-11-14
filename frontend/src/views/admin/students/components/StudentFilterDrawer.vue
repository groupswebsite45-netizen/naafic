<script setup lang="ts">
import { reactive, watch, computed } from 'vue';
import { SchoolClass, StudentFilterParams } from '../../../../types/school';

const props = withDefaults(
  defineProps<{
    isOpen: boolean;
    filters: StudentFilterParams;
    availableClasses: SchoolClass[];
    availableYears?: string[];
  }>(),
  {
    availableYears: () => ['2026/2027'],
  }
);

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'apply', filters: StudentFilterParams): void;
  (e: 'reset'): void;
}>();

const local = reactive<StudentFilterParams>({
  class_id: props.filters.class_id || undefined,
  academic_year: props.filters.academic_year || '',
  gender: props.filters.gender || '',
  status: props.filters.status || '',
  has_portal: props.filters.has_portal,
});

const drawerClasses = computed(() => {
  if (!local.academic_year) return props.availableClasses;
  return props.availableClasses.filter(c => c.academic_year === local.academic_year);
});

watch(
  () => props.filters,
  (newVal) => {
    local.class_id = newVal.class_id || undefined;
    local.academic_year = newVal.academic_year || '';
    local.gender = newVal.gender || '';
    local.status = newVal.status || '';
    local.has_portal = newVal.has_portal;
  },
  { deep: true }
);

watch(
  () => local.academic_year,
  (newYear) => {
    if (newYear && local.class_id) {
      const existsInYear = props.availableClasses.some(c => c.id === Number(local.class_id) && c.academic_year === newYear);
      if (!existsInYear) {
        local.class_id = undefined;
      }
    }
  }
);

function handleApply() {
  emit('apply', {
    ...props.filters,
    class_id: local.class_id ? Number(local.class_id) : undefined,
    academic_year: local.academic_year || undefined,
    gender: local.gender || undefined,
    status: local.status || undefined,
    has_portal: local.has_portal,
    page: 1,
  });
  emit('close');
}

function handleReset() {
  local.class_id = undefined;
  local.academic_year = '';
  local.gender = '';
  local.status = '';
  local.has_portal = undefined;
  emit('reset');
  emit('close');
}
</script>

<template>
  <div v-if="isOpen" class="drawer-backdrop" @click.self="emit('close')">
    <div class="drawer-panel">
      <!-- Drawer Header -->
      <div class="drawer-header">
        <div class="drawer-title-wrap">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <h3 class="drawer-title">Filter Students</h3>
        </div>
        <button class="drawer-close-btn" @click="emit('close')">&times;</button>
      </div>

      <!-- Drawer Body -->
      <div class="drawer-body">
        <!-- Academic Year Filter -->
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="local.academic_year" class="form-control">
            <option value="">All Academic Years</option>
            <option v-for="yr in availableYears" :key="yr" :value="yr">
              {{ yr }}
            </option>
          </select>
        </div>

        <!-- Class Filter -->
        <div class="form-group">
          <label class="form-label">Class</label>
          <select v-model="local.class_id" class="form-control">
            <option :value="undefined">All Classes</option>
            <option v-for="c in drawerClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>

        <!-- Gender Filter -->
        <div class="form-group">
          <label class="form-label">Gender</label>
          <div class="radio-pill-group">
            <label class="radio-pill" :class="{ active: !local.gender }">
              <input v-model="local.gender" type="radio" value="" />
              <span>All</span>
            </label>
            <label class="radio-pill" :class="{ active: local.gender === 'Male' }">
              <input v-model="local.gender" type="radio" value="Male" />
              <span>Male</span>
            </label>
            <label class="radio-pill" :class="{ active: local.gender === 'Female' }">
              <input v-model="local.gender" type="radio" value="Female" />
              <span>Female</span>
            </label>
          </div>
        </div>

        <!-- Status Filter -->
        <div class="form-group">
          <label class="form-label">Enrollment Status</label>
          <select v-model="local.status" class="form-control">
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SUSPENDED">Suspended</option>
            <option value="GRADUATED">Graduated</option>
          </select>
        </div>

        <!-- Portal Access Filter -->
        <div class="form-group">
          <label class="form-label">Portal Account</label>
          <div class="radio-pill-group">
            <label class="radio-pill" :class="{ active: local.has_portal === undefined }">
              <input v-model="local.has_portal" type="radio" :value="undefined" />
              <span>All</span>
            </label>
            <label class="radio-pill" :class="{ active: local.has_portal === true }">
              <input v-model="local.has_portal" type="radio" :value="true" />
              <span>Enabled</span>
            </label>
            <label class="radio-pill" :class="{ active: local.has_portal === false }">
              <input v-model="local.has_portal" type="radio" :value="false" />
              <span>Disabled</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Drawer Footer -->
      <div class="drawer-footer">
        <button class="btn-secondary" @click="handleReset">Reset</button>
        <button class="btn-primary" @click="handleApply">Apply Filters</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  z-index: 50;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease;
  box-sizing: border-box;
}

.drawer-panel {
  width: 100%;
  max-width: 360px;
  background: #ffffff;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  animation: slideIn 0.25s ease;
  box-sizing: border-box;
}

.drawer-header {
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.drawer-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.drawer-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.drawer-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.drawer-close-btn:hover {
  color: #0f172a;
}

.drawer-body {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
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
  color: #475569;
}

.form-control {
  width: 100%;
  height: 38px;
  padding: 0 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.84375rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
}

.form-control:focus {
  background: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.radio-pill-group {
  display: flex;
  gap: 0.375rem;
  width: 100%;
}

.radio-pill {
  flex: 1 1 0%;
  text-align: center;
  padding: 0.45rem 0.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.78125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
  box-sizing: border-box;
  white-space: nowrap;
}

.radio-pill input {
  display: none;
}

.radio-pill.active {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}

.drawer-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.625rem;
  background: #f8fafc;
  box-sizing: border-box;
}

.btn-secondary {
  height: 38px;
  padding: 0 0.875rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  box-sizing: border-box;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.btn-primary {
  height: 38px;
  padding: 0 1.125rem;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  box-sizing: border-box;
}

.btn-primary:hover {
  background: #1d4ed8;
}

@media (max-width: 480px) {
  .drawer-panel {
    max-width: 100%;
  }

  .drawer-footer {
    justify-content: space-between;
  }

  .btn-primary {
    flex: 1;
  }

  .btn-secondary {
    flex: 0 0 auto;
  }
}
</style>

